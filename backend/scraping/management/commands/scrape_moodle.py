import os
import re
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, StaleElementReferenceException, ElementNotInteractableException
)

# Djangoのモデルとプロジェクト設定をインポート
from scraping.models import Assignment
from accounts.models import User

# .envファイルをロード
load_dotenv()

# ロガーの設定
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Moodleから課題をスクレイピングし、データベースに保存する'

    def add_arguments(self, parser):
        parser.add_argument('moodle_username', type=str, help='Moodleのユーザー名')

    def handle(self, *args, **options):
        # コマンドライン引数からユーザー名を取得
        moodle_username = options['moodle_username']

        # Djangoのユーザーを取得
        try:
            user = User.objects.get(username=moodle_username)
        except User.DoesNotExist:
            logger.warning(f'存在しないDjangoユーザー "{moodle_username}" でコマンドが実行されました。')
            self.stdout.write(self.style.ERROR(f'Djangoユーザー "{moodle_username}" が見つかりません。'))
            return

        # 環境変数からMoodleのパスワードとURLを取得
        moodle_password = os.getenv('MOODLE_PASSWORD')
        moodle_url = os.getenv('MOODLE_URL')

        if not all([moodle_password, moodle_url]):
            logger.error('.envファイルに MOODLE_PASSWORD と MOODLE_URL が設定されていません。')
            self.stdout.write(self.style.ERROR('.envファイルに MOODLE_PASSWORD と MOODLE_URL を設定してください。'))
            return

        self.stdout.write(f'ユーザー "{moodle_username}" の課題をMoodleから取得します...')

        try:
            with MoodleScraper(moodle_username, moodle_password, moodle_url, logger) as scraper:
                scraper.login()
                assignments_data = scraper.scrape_all_assignments()

                if not assignments_data:
                    logger.info(f'ユーザー "{moodle_username}" の課題をスクレイピングしましたが、取得結果は0件でした。')
                    self.stdout.write(self.style.WARNING('取得できた課題はありませんでした。'))
                    return

                # 取得した課題をデータベースに保存
                saved_count = 0
                updated_count = 0
                for item in assignments_data:
                    # タイムゾーン情報を持たないdatetimeオブジェクトを、Djangoが利用できるawareなオブジェクトに変換
                    due_date_aware = None
                    if item['due_date']:
                        due_date_aware = make_aware(item['due_date'])
                    
                    # update_or_createでデータの登録・更新を自動化
                    obj, created = Assignment.objects.update_or_create(
                        user=user,
                        title=item['title'],
                        defaults={
                            'description': item['url'], # descriptionにURLを保存
                            'due_date': due_date_aware,
                        }
                    )
                    if created:
                        saved_count += 1
                    else:
                        updated_count += 1

                self.stdout.write(self.style.SUCCESS(f'処理完了: {saved_count}件の新しい課題を保存し、{updated_count}件の課題を更新しました。'))

        except Exception as e:
            logger.error(f"スクレイピング中にエラーが発生しました: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR('スクリプトの実行中にエラーが発生しました。詳細はログを確認してください。'))

class MoodleScraper:
    """
    Moodleサイトから課題情報をスクレイピングするクラス。

    使用方法:
    with MoodleScraper(USER, PASS, URL) as scraper:
        scraper.login()
        assignments = scraper.scrape_all_assignments()
    """
    def __init__(self, username, password, moodle_url, logger, headless=True):
        self.username = username
        self.password = password
        self.moodle_url = moodle_url
        self.login_url = self.moodle_url # 通常は同じURL
        self.my_courses_url = self.moodle_url.replace('/login/index.php', '/my/courses.php')
        self.logger = logger

        # ブラウザ設定
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.wait_long = WebDriverWait(self.driver, 10)
        self.wait_short = WebDriverWait(self.driver, 3)

        self.logger.info("MoodleScraperが初期化されました。")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()
        self.logger.info("ブラウザを終了しました。")

    def login(self):
        # Moodleにログイン
        self.logger.info(f"{self.login_url} にアクセスしてログインします...")
        self.driver.get(self.login_url)

        try:
            username_field = self.wait_long.until(EC.element_to_be_clickable((By.ID, 'username')))
            username_field.send_keys(self.username)
        except TimeoutException:
            self.logger.error("ログインページの読み込みに時間がかかりすぎています")
            raise

        for i in range(3):
            try:
                password_field = self.wait_long.until(EC.element_to_be_clickable((By.ID, 'password')))
                password_field.send_keys(self.password)
                break
            except (StaleElementReferenceException, ElementNotInteractableException) as e:
                self.logger.warning(f"試行 {i+1}/3: パスワードフィールドの操作に失敗 ({e.__class__.__name__})。再試行します。")
                time.sleep(0.5)
            except TimeoutException:
                self.logger.error("パスワードフィールドが見つからないかクリック可能になりませんでした。")
                raise
        else:
            self.logger.error("パスワードフィールドの操作に5回失敗しました。")
            raise

        login_button = self.wait_long.until(EC.element_to_be_clickable((By.ID, 'loginbtn')))
        login_button.click()

        try:
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".usermenu")))
            self.logger.info("ログインに成功しました。")
        except TimeoutException:
            self.logger.error("ログインに失敗しました。ID/Passwordが間違っているか、ログインに時間がかかりすぎています。")
            raise

    def scrape_all_assignments(self):
        # 登録されている全ての授業から課題をスクレイピング
        courses = self._get_courses()
        all_assignments = []
        for course_name, course_url in courses:
            all_assignments.extend(self._scrape_assignments_from_course(course_name, course_url))
        return all_assignments

    def _get_courses(self):
        # マイコースページから授業の一覧を取得
        self.logger.info("マイコースページに遷移して授業一覧を取得します...")
        self.driver.get(self.my_courses_url)
        courses = []
        try:
            elements = self.wait_long.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.aalink.coursename")))
            for el in elements:
                course_url = el.get_attribute("href")
                try:
                    child_el = el.find_element(By.CSS_SELECTOR, "span.multiline")
                    course_name = child_el.get_attribute("title")
                    if course_url:
                        courses.append((course_name, course_url))
                except Exception as e:
                    self.logger.warning(f"授業タイトルの取得に失敗しました: {e} (URL: {course_url})")
        except TimeoutException:
            self.logger.error("登録されている授業がないか、マイコースページに遷移できませんでした。")
            raise
        return courses

    def _scrape_assignments_from_course(self, course_name, course_url):
        # 特定の授業ページから課題をスクレイピング
        self.logger.info(f"授業「{course_name}」の処理を開始します (URL: {course_url})")
        self.driver.get(course_url)
        course_assignments = []
        try:
            element = self.wait_short.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[id='tabs-tree-start'], ul[data-for='course_sectionlist']")))
            
            if "course_sectionlist" == element.get_attribute("data-for"):
                course_assignments = self._scrape_topic_week_page((course_name, course_url))
            elif "tabs-tree-start" == element.get_attribute("id"):
                course_assignments = self._scrape_tab_page((course_name, course_url))
            else:
                self.logger.warning(f"授業「{course_name}」は予期しないページ形式です。")
        except TimeoutException:
            self.logger.error(f"授業「{course_name}」のページ形式を判断できませんでした (タイムアウト)。")
        return course_assignments

    def _scrape_topic_week_page(self, course):
        # topic/week形式の授業ページの処理
        self.logger.info("topic/week形式のページを処理します。")
        try:
            return self._process_assign_on_current_page()
        except TimeoutException:
            self.logger.warning(f"授業「{course[0]}」では課題が見つかりませんでした (タイムアウト)。")
            return []

    def _scrape_tab_page(self, course):
        # tab形式の授業ページの処理
        self.logger.info("tab形式のページを処理します。")
        assignments = []
        try:
            elements = self.wait_short.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.tabs-wrapper a.nav-link")))
            tabs = [(el.get_attribute("title"), el.get_attribute("href")) for el in elements if el.get_attribute("href")]
            
            for tab_title, tab_url in tabs:
                self.driver.get(tab_url)
                self.logger.info(f"タブ「{tab_title}」を処理中...")
                try:
                    assignments.extend(self._process_assign_on_current_page())
                except TimeoutException:
                    self.logger.warning(f"授業「{course[0]}」のタブ「{tab_title}」では課題が見つかりませんでした (タイムアウト)。")
        except TimeoutException:
            self.logger.error(f"授業「{course[0]}」のタブが見つかりませんでした。")
        return assignments

    def _process_assign_on_current_page(self):
        # 現在のページの課題を処理
        assignments = []
        try:
            elements = self.wait_short.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.modtype_assign a.aalink, li.modtype_quiz a.aalink")))
            assign_links = [el.get_attribute("href") for el in elements]
            
            for assign_url in assign_links:
                assignment_data = self._scrape_assign_details(assign_url)
                if assignment_data:
                    assignments.append(assignment_data)
            return assignments
        except TimeoutException:
            raise

    def _scrape_assign_details(self, assign_url):
        # 課題の詳細をスクレイピング
        self.driver.get(assign_url)
        title, date = None, None
        try:
            info_div = self.wait_short.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.activity-information")))
            title = info_div.get_attribute("data-activityname")
        except TimeoutException:
            self.logger.warning(f"URL: {assign_url} で課題タイトルが見つかりませんでした (タイムアウト)。")
        try:
            date_div = self.wait_short.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.activity-dates")))
            date = self._parse_start_end_datetimes(date_div.text)
        except TimeoutException:
            self.logger.warning(f"URL: {assign_url} で課題期日が見つかりませんでした (タイムアウト)。")

        self.logger.info(f"課題取得: {title}, URL: {assign_url}, 期日: {date}")
        return {'title': title, 'url': assign_url, 'due_date': date}
    
    @staticmethod
    def _parse_start_end_datetimes(text):
        # テキストから（終了）日時を抽出してdatatime型を返す
        pattern = re.compile(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日.*?(\d{1,2}):(\d{1,2})')
        matches = pattern.findall(text)
        datetimes = [datetime(*map(int, match)) for match in matches]
        if len(datetimes) == 2: return datetimes[1]
        if len(datetimes) == 1: return datetimes[0]
        return None
