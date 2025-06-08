import re
import logging
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

class MoodleScraper:
    """
    Moodleサイトから課題情報をスクレイピングするクラス。
    requestsとBeautifulSoupを使用します。

    使用方法:
    # loggingの設定を別途行う
    logger = logging.getLogger(__name__) # 例
    with MoodleScraper("USER", "PASS", "MOODLE_LOGIN_URL", logger) as scraper:
        if scraper.login():
            assignments = scraper.scrape_all_assignments()
    """

    def __init__(self, username, password, moodle_login_url, logger):
        self.username = username
        self.password = password
        self.login_url = moodle_login_url
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logger.info("MoodleScraperが初期化されました。")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.logger.info("セッションを終了しました。")

    def login(self):
        self.logger.info(f"{self.login_url} にアクセスしてログインします...")
        try:
            # ログインページからlogintokenを取得
            login_page_res = self.session.get(self.login_url, timeout=10)
            login_page_res.raise_for_status()
            soup = BeautifulSoup(login_page_res.text, 'html.parser')
            logintoken = soup.find('input', {'name': 'logintoken'})
            if not logintoken:
                self.logger.error("ログインページのlogintokenが見つかりませんでした。")
                return False
            logintoken_value = logintoken['value']

            # ログイン情報をPOST
            payload = {
                'username': self.username,
                'password': self.password,
                'logintoken': logintoken_value,
            }
            login_res = self.session.post(self.login_url, data=payload, timeout=10)
            login_res.raise_for_status()

            # ログイン成功の確認
            soup = BeautifulSoup(login_res.text, 'html.parser')
            if soup.select_one(".usermenu"):
                self.home_url = login_res.url
                self.logger.info("ログインに成功しました。")
                return True
            else:
                self.logger.error("ログインに失敗しました。ID/Passwordが間違っている可能性があります。")
                return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"ログイン処理中にネットワークエラーが発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"ログイン中に予期せぬエラーが発生しました: {e}")
            return False

    def scrape_all_assignments(self):
        courses = self._get_courses()
        all_assignments = []
        for course_name, course_url in courses:
            all_assignments.extend(self._scrape_assignments_from_course(course_name, course_url))
        return all_assignments

    def _get_courses(self):
        self.logger.info(f"トップページから授業一覧を取得します...")
        try:
            res = self.session.get(self.home_url, timeout=10)
            res.raise_for_status()

            soup = BeautifulSoup(res.text, 'html.parser')
            courses = []
            selector = 'section[data-block="course_list"] ul.unlist a'
            elements = soup.select(selector)
            self.logger.info(f"{len(elements)} 件のコース要素が見つかりました。")

            for el in elements:
                try:
                    course_url = el.get("href")
                    course_name = el.text
                    if course_url and course_name:
                        courses.append((course_name, course_url))
                except Exception as e:
                    self.logger.warning(f"授業タイトルまたはURLの取得に失敗しました: {e}")
            
            if not courses:
                self.logger.warning("取得できたコースはありませんでした。")
            return courses

        except requests.exceptions.RequestException as e:
            self.logger.error(f"マイコースページの読み込みに失敗しました: {e}")
            return []

    def _scrape_assignments_from_course(self, course_name, course_url):
        self.logger.info(f"授業「{course_name}」の処理を開始します (URL: {course_url})")
        try:
            res = self.session.get(course_url, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            if soup.select_one("ul[data-for='course_sectionlist']"):
                return self._scrape_topic_week_page(course_name, soup)
            elif soup.select_one("div[id='tabs-tree-start']"):
                return self._scrape_tab_page(course_name, soup)
            else:
                self.logger.warning(f"授業「{course_name}」は予期しないページ形式です。")
                return []

        except requests.exceptions.RequestException as e:
            self.logger.error(f"授業「{course_name}」のページ形式を判断できませんでした: {e}")
            return []

    def _scrape_topic_week_page(self, course_name, soup):
        self.logger.info(f"授業「{course_name}」: topic/week形式のページを処理します。")
        return self._process_assign_on_current_page(course_name, soup)

    def _scrape_tab_page(self, course_name, soup):
        self.logger.info(f"授業「{course_name}」: tab形式のページを処理します。")
        assignments = []
        tab_elements = soup.select("div.tabs-wrapper a.nav-link")
        tabs_info = [(el.get("title", el.text.strip()), el.get("href")) for el in tab_elements if el.get("href")]
        self.logger.info(f"{len(tabs_info)}個のタブが見つかりました。")

        for tab_title, tab_url in tabs_info:
            try:
                self.logger.info(f"タブ「{tab_title}」を処理中...")
                res = self.session.get(tab_url, timeout=10)
                res.raise_for_status()
                tab_soup = BeautifulSoup(res.text, 'html.parser')
                assignments.extend(self._process_assign_on_current_page(course_name, tab_soup))
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"授業「{course_name}」のタブ「{tab_title}」の処理に失敗: {e}")
        
        return assignments

    def _process_assign_on_current_page(self, course_name, soup):
        assignments = []
        elements = soup.select("li.modtype_assign a.aalink, li.modtype_quiz a.aalink")
        assign_links = [el.get("href") for el in elements if el.get("href")]

        for assign_url in assign_links:
            assignment_data = self._scrape_assign_details(assign_url, course_name)
            if assignment_data:
                assignments.append(assignment_data)
        return assignments

    def _scrape_assign_details(self, assign_url, course_name):
        try:
            res = self.session.get(assign_url, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            title, date = None, None

            info_div = soup.select_one("div.activity-information")
            if info_div:
                title = info_div.get("data-activityname")
            else:
                self.logger.warning(f"URL: {assign_url} で課題タイトルが見つかりませんでした。")

            date_div = soup.select_one("div.activity-dates")
            if date_div:
                date = self._parse_start_end_datetimes(date_div.get_text())
            else:
                self.logger.warning(f"URL: {assign_url} で課題期日が見つかりませんでした。")
            
            start_date, due_date = (date[0], date[1]) if date else (None, None)

            self.logger.info(f"課題取得: {title}, URL: {assign_url}, 期日: {due_date}")
            return {'title': title, 'url': assign_url, 'course': course_name, 'start_date': start_date, 'due_date': due_date}

        except requests.exceptions.RequestException as e:
            self.logger.error(f"課題詳細ページの取得に失敗しました ({assign_url}): {e}")
            return None

    @staticmethod
    def _parse_start_end_datetimes(text, tz_str="Asia/Tokyo"):
        start_dt, end_dt = None, None
        try:
            tz = ZoneInfo(tz_str)
        except Exception:
            tz = ZoneInfo("UTC")
        
        pattern = re.compile(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日.*?(\d{1,2}):(\d{1,2})')
        for line in text.splitlines():
            match = pattern.search(line)
            if not match:
                continue
            
            time_parts = map(int, match.groups())
            naive_dt = datetime(*time_parts)
            aware_dt = naive_dt.replace(tzinfo=tz)
            
            if '開始' in line:
                start_dt = aware_dt
            elif '期限' in line or '終了' in line:
                end_dt = aware_dt
        return (start_dt, end_dt)