import getpass
import logging
import re
import traceback
from time import sleep
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        TimeoutException)
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# タイムゾーンの扱いのためにZoneInfoをインポート
from datetime import datetime
from zoneinfo import ZoneInfo

class WebClassScraper:
    """
    東京電機大学のWebClassから課題情報をスクレイピングするクラス。
    ダッシュボードから全コースの情報を取得し、各コースページに遷移して
    課題提出先のURLを詳細に取得する。（日付処理修正版）
    """

    DASHBOARD_HREF = "/webclass/ip_mods.php/plugin/score_summary_table/dashboard"
    BASE_DOMAIN = "https://els.sa.dendai.ac.jp"

    def __init__(self, username, password, webclass_url, logger, headless=True):
        self.username = username
        self.password = password
        self.login_url = webclass_url
        self.home_url = ''
        self.logger = logger
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--log-level=3')
        options.add_experimental_option('prefs', {'intl.accept_languages': 'ja,en-US,en'})
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 20)
        self.wait_long = WebDriverWait(self.driver, 30)
        self.logger.info("WebClassScraperが初期化されました。")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()
        self.logger.info("ブラウザを終了しました。")

    def login(self):
        self.logger.info(f"ログインページ ({self.login_url}) にアクセスしています...")
        self.driver.get(self.login_url)
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(self.username)
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            self.driver.find_element(By.ID, "LoginBtn").click()
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'logout')]")))
            self.logger.info("ログインに成功しました。")
            return True
        except TimeoutException:
            self.logger.error("ログインに失敗しました。ID/Passwordが間違っているか、ログイン後のページ構造が想定外です。")
            return False

    def scrape_all_assignments(self):
        all_assignments_list = []
        if not self._navigate_to_dashboard():
            return all_assignments_list
        try:
            course_elements = self._get_course_elements_from_dashboard()
            self.logger.info(f"{len(course_elements)}個のコースが見つかりました。")
            dashboard_window_handle = self.driver.current_window_handle
            for course_element in course_elements:
                assignments_from_course = self._process_single_course(course_element, dashboard_window_handle)
                if assignments_from_course:
                    all_assignments_list.extend(assignments_from_course)
        except Exception as e:
            self.logger.error(f"スクレイピング処理全体で予期せぬエラーが発生しました: {e}")
            self.logger.debug(traceback.format_exc())
        return all_assignments_list

    def _navigate_to_dashboard(self):
        self.logger.info("ダッシュボードに移動しています...")
        try:
            self.driver.switch_to.default_content()
            dashboard_link_xpath = f"//a[@href='{self.DASHBOARD_HREF}']"
            self.logger.info(f"ダッシュボードへのリンク ({dashboard_link_xpath}) を探しています...")
            dashboard_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, dashboard_link_xpath)))
            self.logger.info("ダッシュボードへのリンクを発見しました。クリックします...")
            dashboard_link.click()
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ip-iframe")))
            self.logger.info("ダッシュボードのiframeに切り替えました。")
            return True
        except TimeoutException:
            self.logger.error("ダッシュボードへの移動またはiframeへの切り替えがタイムアウトしました。")
            return False

    def _get_course_elements_from_dashboard(self):
        self.logger.info("コース要素の取得を開始します...")
        try:
            main_element_selector = (By.CSS_SELECTOR, "main[role='main']")
            main_element = self.wait.until(EC.presence_of_element_located(main_element_selector))
            sleep(2.0)
            course_wrapper_xpath = ".//div[contains(@class, 'mt-2') and .//a[contains(@class, 'font-semibold')]]"
            self.logger.info(f"コースラッパーをXPath: '{course_wrapper_xpath}' で検索します...")
            return main_element.find_elements(By.XPATH, course_wrapper_xpath)
        except TimeoutException:
            self.logger.error("ダッシュボード内のコース要素の取得がタイムアウトしました。")
            return []

    def _process_single_course(self, course_element, dashboard_handle):
        formatted_assignments = []
        course_name = "不明なコース"
        try:
            soup = BeautifulSoup(course_element.get_attribute('outerHTML'), "html.parser")
            course_link_tag = soup.select_one("a.font-semibold")
            if not course_link_tag: return None

            course_name = course_link_tag.get_text(strip=True)
            course_url = urljoin(self.BASE_DOMAIN, course_link_tag['href'])
            self.logger.info(f"\n■コース '{course_name}' の処理を開始...")

            table = soup.find("table")
            if not table or "登録されている教材がありません" in soup.get_text():
                self.logger.info(" -> 登録済みの教材はありません。")
                return [] 

            headers = [th.get_text(strip=True) for th in table.select("thead th")]
            if not headers: headers = ["教材", "締切", "実施日", "最高点", "状態"]

            for row in table.select("tbody tr"):
                cols = row.find_all("td")
                if len(cols) < len(headers): continue

                row_data = {headers[i]: col.get_text(strip=True) for i, col in enumerate(cols)}
                assignment_name = row_data.get("教材")
                if not assignment_name: continue

                submission_url = None
                if any(kw in assignment_name for kw in ["課題", "レポート", "小テスト", "アンケート"]):
                    self.logger.info(f" -> 課題「{assignment_name}」の提出先URLを検索...")
                    submission_url = self._get_submission_url_from_course_page(course_url, assignment_name, dashboard_handle)
                    
                    if not submission_url:
                        self.logger.warning(f" -> 課題「{assignment_name}」のURLが取得できなかったため、スキップします。")
                        continue

                    status_str = row_data.get("状態", "")
                    is_submitted = "済" in status_str
                    
                    due_date_str = row_data.get("締切")
                    due_date_obj = self._parse_webclass_due_date(due_date_str)

                    assignment_dict = {
                        'title': assignment_name,
                        'url': submission_url,
                        'course': course_name,
                        'start_date': None,
                        'due_date': due_date_obj,
                        'content': None,
                        'is_submitted': is_submitted,
                    }
                    formatted_assignments.append(assignment_dict)
            return formatted_assignments
        except Exception as e:
            self.logger.warning(f"コース '{course_name}' 処理中にエラーが発生: {e}")
            self.logger.debug(traceback.format_exc())
            return None

    def _get_submission_url_from_course_page(self, course_url, assignment_name, dashboard_handle):
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.new_window('tab')
            self.driver.get(course_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            url = self._find_link_on_page(soup, assignment_name)
            if url: self.logger.info(f"   -> URLを発見: {url}")
            else: self.logger.warning(f"   -> URLが見つかりませんでした。")
            return url
        except Exception as e:
            self.logger.error(f"   -> コースページ ({course_url}) へのアクセス中にエラー: {e}")
            return None
        finally:
            if len(self.driver.window_handles) > 1:
                self.driver.close()
            self.driver.switch_to.window(dashboard_handle)
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ip-iframe")))

    def _find_link_on_page(self, soup, assignment_name):
        norm_assignment_name = re.sub(r'[\(（].*?[\)）]', '', assignment_name).strip()
        all_links = soup.find_all("a", href=re.compile(r"/webclass/do_contents\.php\?.*"))
        
        # テキストが完全一致するものを最優先で探す
        for link in all_links:
            link_text = re.sub(r'[\(（].*?[\)）]', '', link.get_text(strip=True)).strip()
            if norm_assignment_name == link_text:
                return urljoin(self.BASE_DOMAIN, link['href'])

        # 部分一致するものを探す（より柔軟なマッチング）
        for link in all_links:
            if norm_assignment_name in link.get_text(strip=True):
                return urljoin(self.BASE_DOMAIN, link['href'])
        
        return None

    def _parse_webclass_due_date(self, date_str: str, tz_str: str = "Asia/Tokyo"):
        """★★★ 修正箇所 ★★★
        WebClassの締切日文字列 (例: "2025-06-19 23:59") をdatetimeオブジェクトに変換します。
        """
        if not date_str or not isinstance(date_str, str) or date_str == '-':
            return None
        
        try:
            # "YYYY-MM-DD HH:MM" 形式の文字列をdatetimeオブジェクトに変換
            dt_naive = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            # タイムゾーン情報を付与
            tz = ZoneInfo(tz_str)
            return dt_naive.astimezone(tz)
        except (ValueError, TypeError):
            self.logger.warning(f"日付文字列の変換に失敗しました: {date_str}")
            return None

def print_scraped_data(final_all_assignments_list):
    if not final_all_assignments_list:
        print("\n課題データは取得されませんでした。")
        return
    print(f"\n\n--- 全 {len(final_all_assignments_list)} 件のスクレイピングされた課題データ ---")
    courses = {}
    for assignment in final_all_assignments_list:
        course_name = assignment.get('course', '不明なコース')
        if course_name not in courses:
            courses[course_name] = []
        courses[course_name].append(assignment)

    for course_name, assignments in courses.items():
        print(f"\n■コース: {course_name}")
        for assign_idx, assign_data in enumerate(assignments):
            print(f"  課題 {assign_idx + 1}:")
            for key, value in assign_data.items():
                if key == 'course': continue
                print(f"    - {key}: {value if value is not None else 'N/A'}")
    print("\n-----------------------------------------")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
    try:
        webclass_login_url = "https://els.sa.dendai.ac.jp/webclass/login.php"
        user_id = input("WebClassのユーザーIDを入力してください: ")
        password = getpass.getpass("パスワードを入力してください: ")
        with WebClassScraper(user_id, password, webclass_login_url, logger, headless=True) as scraper:
            if scraper.login():
                all_data = scraper.scrape_all_assignments()
                print_scraped_data(all_data)
    except Exception as e:
        logger.error(f"スクリプトの実行中に致命的なエラーが発生しました: {e}")
        logger.debug(traceback.format_exc())