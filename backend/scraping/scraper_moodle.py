import re
import time
import logging
from datetime import datetime
from zoneinfo import ZoneInfo 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, StaleElementReferenceException, ElementNotInteractableException
)

class MoodleScraper:
    """
    Moodleサイトから課題情報をスクレイピングするクラス。

    使用方法:
    logger = logging.getLogger(__name__) # 例
    # loggingの設定を別途行う
    with MoodleScraper("USER", "PASS", "MOODLE_LOGIN_URL", logger) as scraper:
        scraper.login()
        assignments = scraper.scrape_all_assignments()
    """
    def __init__(self, username, password, moodle_login_url, logger, headless=True):
        self.username = username
        self.password = password
        self.login_url = moodle_login_url
        self.logger = logger

        # ブラウザ設定
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox') # CI環境などで必要になることがある
        options.add_argument('--window-size=1920,1080') # ウィンドウサイズを指定
        if headless:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.wait_long = WebDriverWait(self.driver, 10)
        self.wait_short = WebDriverWait(self.driver, 1)

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
            self.logger.error("ログインページのユーザー名フィールドの読み込みに失敗しました。")
            self.driver.save_screenshot("error_login_username_timeout.png")
            return False

        MAX_RETRIES = 3
        for i in range(MAX_RETRIES):
            try:
                password_field = self.wait_long.until(EC.element_to_be_clickable((By.ID, 'password')))
                password_field.send_keys(self.password)
                break
            except (StaleElementReferenceException, ElementNotInteractableException) as e:
                self.logger.warning(f"試行 {i+1}/3: パスワードフィールドの操作に失敗 ({e.__class__.__name__})。再試行します。")
                time.sleep(0.5)
            except TimeoutException:
                self.logger.error("パスワードフィールドが見つからないかクリック可能になりませんでした。")
                self.driver.save_screenshot("error_login_password_timeout.png")
                return False
        else:
            self.logger.error(f"パスワードフィールドの操作に{MAX_RETRIES}回失敗しました。")
            self.driver.save_screenshot("error_login_password_failed.png")
            return False

        try:
            login_button = self.wait_long.until(EC.element_to_be_clickable((By.ID, 'loginbtn')))
            login_button.click()
        except TimeoutException:
            self.logger.error("ログインボタンが見つからないかクリック可能になりませんでした。")
            self.driver.save_screenshot("error_login_button_timeout.png")
            return False

        try:
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".usermenu")))
            self.logger.info("ログインに成功しました。")
        except TimeoutException:
            self.logger.error("ログインに失敗しました。ID/Passwordが間違っているか、ログイン後のページ遷移に時間がかかりすぎています。")
            self.driver.save_screenshot("error_login_failed_or_timeout.png")
            return False
        
        return True

    def scrape_all_assignments(self):
        # 登録されている全ての授業から課題をスクレイピング
        # 辞書(課題情報)のリストを返す
        courses = self._get_courses()
        all_assignments = []
        for course_name, course_url in courses:
            all_assignments.extend(self._scrape_assignments_from_course(course_name, course_url))
        return all_assignments

    def _get_courses(self):
        # マイコースページから授業の一覧を取得
        # タプル(course_name, course_url)のリストを返す
        self.logger.info(f"授業一覧を取得します...")
        courses = []
        try:
            selector = 'section[data-block="course_list"] ul.unlist a'
            elements = self.wait_long.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
            self.logger.info(f"{len(elements)} 件のコース要素が見つかりました。")
            for el in elements:
                try:
                    course_url = el.get_attribute("href")
                    course_name = el.text
                    if course_url and course_name:
                        courses.append((course_name, course_url))
                except Exception as e:
                    self.logger.warning(f"授業タイトルまたはURLの取得に失敗しました: {e}")
        except TimeoutException:
            self.logger.error("登録されている授業がないか、マイコースページの読み込みに失敗しました。")
            self.driver.save_screenshot("error_get_courses_timeout.png")
        if not courses:
            self.logger.warning("取得できたコースはありませんでした。")
        return courses

    def _scrape_assignments_from_course(self, course_name, course_url):
        # 授業ページから課題をスクレイピング
        # 授業ページの課題情報(辞書)すべてをリストで返す
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
        self.logger.info(f"授業「{course[0]}」: topic/week形式のページを処理します。")
        try:
            return self._process_assign_on_current_page(course[0])
        except TimeoutException:
            self.logger.warning(f"授業「{course[0]}」では課題が見つかりませんでした (タイムアウト)。")
            return []

    def _scrape_tab_page(self, course):
        # tab形式の授業ページの処理
        self.logger.info("tab形式のページを処理します。")
        assignments = []
        try:
            elements = self.wait_short.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.tabs-wrapper a.nav-link")))
            tabs_info = [(el.get_attribute("title"), el.get_attribute("href")) for el in elements if el.get_attribute("href")]
            self.logger.info(f"{len(tabs_info)}個のタブが見つかりました。")
            
            for tab_title, tab_url in tabs_info:
                self.driver.get(tab_url)
                self.logger.info(f"タブ「{tab_title}」を処理中...")
                try:
                    assignments.extend(self._process_assign_on_current_page(course[0]))
                except TimeoutException:
                    self.logger.warning(f"授業「{course[0]}」のタブ「{tab_title}」では課題が見つかりませんでした (タイムアウト)。")
        except TimeoutException:
            self.logger.error(f"授業「{course[0]}」のタブが見つかりませんでした(タイムアウト)。")
        return assignments

    def _process_assign_on_current_page(self, course_name):
        # 現在のページの課題を処理
        assignments = []
        try:
            elements = self.wait_short.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.modtype_assign a.aalink, li.modtype_quiz a.aalink")))
            assign_links = [el.get_attribute("href") for el in elements]
            
            for assign_url in assign_links:
                assignment_data = self._scrape_assign_details(assign_url, course_name)
                if assignment_data:
                    assignments.append(assignment_data)
            return assignments
        except TimeoutException:
            return []

    def _scrape_assign_details(self, assign_url, course_name):
        # 課題の詳細をスクレイピング
        # 課題情報を辞書で返す
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

        start_date = None
        due_date = None
        if date:
            start_date = date[0]
            due_date = date[1]

        self.logger.info(f"課題取得: {title}, URL: {assign_url}, 期日: {due_date}")
        return {'title': title, 'url': assign_url, 'course': course_name, 'start_date': start_date, 'due_date': due_date}
    
    @staticmethod
    def _parse_start_end_datetimes(text, tz_str="Asia/Tokyo"):
        """
        テキストから開始日時と終了日時を抽出し、タイムゾーン情報を持つdatetimeオブジェクトのタプルとして返す
        return (start_datetime, end_datetime) のタプル
        見つからない日時は None になる
        """
        # 結果を格納する変数を準備（初期値はNone）
        start_dt = None
        end_dt = None

        # タイムゾーンオブジェクトを取得
        try:
            tz = ZoneInfo(tz_str)
        except Exception:
            tz = ZoneInfo("UTC")

        # 年月日時分を抽出する正規表現パターン
        pattern = re.compile(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日.*?(\d{1,2}):(\d{1,2})')

        # 行ごとに処理する
        for line in text.splitlines():
            # 日時部分を探索
            match = pattern.search(line)
            if not match:
                continue # 行に日時がなければ次の行へ

            # datetimeオブジェクトを生成
            time_parts = map(int, match.groups())
            naive_dt = datetime(*time_parts)
            # タイムゾーン情報を付与
            aware_dt = naive_dt.replace(tzinfo=tz)

            # キーワードに応じて、対応する変数に格納
            if '開始' in line:
                start_dt = aware_dt
            elif '期限' in line or '終了' in line:
                end_dt = aware_dt

        # 抽出した開始日時と終了日時をタプルで返す
        return (start_dt, end_dt)
