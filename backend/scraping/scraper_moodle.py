import re
import logging
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict, Any, Optional, Type
from types import TracebackType


class MoodleScraper:
    """Moodleサイトから課題情報をスクレイピングするクラス。

    requestsとBeautifulSoupを使用して、Moodleにログインし、コースから課題情報を取得します。
    インスタンスは `with` ステートメントで安全にセッションを管理できます。

    Example:
        import logging
        import pprint

        # ロガーの基本的な設定（INFOレベル以上のログをコンソールに出力）
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)

        # ご自身のMoodleの情報を設定してください
        MOODLE_LOGIN_URL = "https://your.moodle.site/login/index.php"
        USERNAME = "your_username"
        PASSWORD = "your_password"

        try:
            # withステートメントでインスタンス化し、自動的にセッションを閉じます
            with MoodleScraper(USERNAME, PASSWORD, MOODLE_LOGIN_URL, logger) as scraper:
                # ログイン処理
                if scraper.login():
                    # 全てのコースから課題を取得
                    assignments = scraper.scrape_all_assignments()

                    if assignments:
                        print(f"--- {len(assignments)}件の課題が見つかりました ---")
                        # 取得した課題を見やすく表示
                        pprint.pprint(assignments)
                    else:
                        print("取得できる課題はありませんでした。")

        except Exception as e:
            logger.error(f"スクレイピング処理中に予期せぬエラーが発生しました: {e}")
    """

    # 英語の月名を数値に変換するためのマッピング
    _MONTH_MAP_EN: Dict[str, int] = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    # 言語ごとの設定
    # group_orderで正規表現のキャプチャグループの順序を指定することで、様々な日付形式に対応
    _DATE_CONFIG: Dict[str, Dict[str, Any]] = {
        'en': { # English
            'pattern': re.compile(
                r'(?:\w+,\s+)?(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4}),\s+(\d{1,2}):(\d{2})\s+(AM|PM)',
                re.IGNORECASE
            ),
            'group_order': ['day', 'month_str', 'year', 'hour', 'minute', 'ampm'],
            'month_map': _MONTH_MAP_EN,
            'start_keywords': ['Open'],
            'end_keywords': ['Due', 'Close']
        },
        'en_us': { # English(United States)
            'pattern': re.compile(
                r'(?:\w+,\s+)?(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4}),\s+(\d{1,2}):(\d{2})\s+(AM|PM)',
                re.IGNORECASE
            ),
            'group_order': ['month_str', 'day', 'year', 'hour', 'minute', 'ampm'],
            'month_map': _MONTH_MAP_EN,
            'start_keywords': ['Open'],
            'end_keywords': ['Due', 'Close']
        },
        'vi': { # Vietnamese
            'pattern': re.compile(
                r'Thứ\s+\w+,\s*(\d{1,2})\s+tháng\s+(\d{1,2})\s+(\d{4}),\s*(\d{1,2}):(\d{2})\s*(AM|PM)',
                re.IGNORECASE
            ),
            'group_order': ['day', 'month', 'year', 'hour', 'minute', 'ampm'],
            'start_keywords': ['Open'],
            'end_keywords': ['Due', 'Close']
        },
        'zh_tw': { # 正體中文
            'pattern': re.compile(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日.*?(\d{1,2}):(\d{2})'),
            'group_order': ['year', 'month', 'day', 'hour', 'minute'],
            'start_keywords': ['開始', '開啟'],
            'end_keywords': ['到期', '關閉', '結束']
        },
        'ja': { # 日本語
            'pattern': re.compile(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日.*?(\d{1,2}):(\d{2})'),
            'group_order': ['year', 'month', 'day', 'hour', 'minute'],
            'start_keywords': ['開始'],
            'end_keywords': ['期限', '終了']
        },
        'zh_cn': { # 简体中文
            'pattern': re.compile(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日.*?(\d{1,2}):(\d{2})'),
            'group_order': ['year', 'month', 'day', 'hour', 'minute'],
            'start_keywords': ['打开', '已打开'],
            'end_keywords': ['到期日', '关闭', '已关闭']
        },
        'ko': { # 한국어
            'pattern': re.compile(
                r'(?:\w+,\s+)?(\d{1,2})\s+(\d{1,2})월\s+(\d{4}),\s+(\d{1,2}):(\d{2})\s+(AM|PM)',
                re.IGNORECASE
            ),
            'group_order': ['day', 'month', 'year', 'hour', 'minute', 'ampm'],
            'start_keywords': ['Opened','열기', '열림'],
            'end_keywords': ['Due','닫기', '닫힘']
        }
    }

    def __init__(self, username: str, password: str, moodle_login_url: str, logger: logging.Logger):
        """MoodleScraperのコンストラクタ。

        Args:
            username (str): Moodleのユーザー名。
            password (str): Moodleのパスワード。
            moodle_login_url (str): MoodleのログインページのURL。
            logger (logging.Logger): ログ出力用のロガーインスタンス。
        """
        self.username: str = username
        self.password: str = password
        self.login_url: str = moodle_login_url
        self.home_url: Optional[str] = None
        self.lang_code: str = 'ja'
        self.logger: logging.Logger = logger
        self.session: requests.Session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logger.info("MoodleScraperが初期化されました。")

    def __enter__(self) -> 'MoodleScraper':
        """withステートメントの開始時に呼び出され、自身のインスタンスを返します。"""
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> None:
        """withステートメントの終了時にセッションをクローズします。"""
        self.session.close()
        self.logger.info("セッションを終了しました。")

    def login(self) -> bool:
        """Moodleサイトにログインします。

        ログインページのlogintokenを取得し、ユーザー名とパスワードと共にPOSTします。
        ログイン成功後は、ホームページのURLをインスタンス変数に保存します。

        Returns:
            bool: ログインに成功した場合はTrue、失敗した場合はFalse。
        """
        self.logger.info(f"{self.login_url} にアクセスしてログインします...")
        try:
            # ログインページからlogintokenを取得
            login_page_res = self.session.get(self.login_url, timeout=10)
            login_page_res.raise_for_status()
            soup = BeautifulSoup(login_page_res.text, 'html.parser')
            logintoken_input = soup.find('input', {'name': 'logintoken'})
            if not logintoken_input:
                self.logger.error("ログインページのlogintokenが見つかりませんでした。")
                return False
            logintoken_value = logintoken_input['value']

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
                self.logger.info("ログインに成功しました。")
                self.home_url = login_res.url
                self._extract_lang_code(soup)
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

    def scrape_all_assignments(self) -> List[Dict[str, Any]]:
        """履修している全てのコースから課題情報をスクレイピングします。

        Returns:
            List[Dict[str, Any]]: 全ての課題情報の辞書を含むリスト。
        """
        if not self.home_url:
            self.logger.error("ログインしていないため、課題を取得できません。")
            return []
        courses = self._get_courses()
        all_assignments = []
        for course_name, course_url in courses:
            all_assignments.extend(self._scrape_assignments_from_course(course_name, course_url))
        return all_assignments

    def _get_courses(self) -> List[Tuple[str, str]]:
        """ログイン後のホームページから履修しているコースの一覧を取得します。

        Returns:
            List[Tuple[str, str]]: (コース名, コースURL) のタプルのリスト。
        """
        self.logger.info("トップページから授業一覧を取得します...")
        if not self.home_url:
            self.logger.error("ホームページのURLが設定されていません。")
            return []
        try:
            res = self.session.get(self.home_url, timeout=10)
            res.raise_for_status()

            soup = BeautifulSoup(res.text, 'html.parser')
            courses: List[Tuple[str, str]] = []
            selector = 'section[data-block="course_list"] ul.unlist a'
            elements = soup.select(selector)
            self.logger.info(f"{len(elements)} 件のコース要素が見つかりました。")

            for el in elements:
                try:
                    course_url = el.get("href")
                    course_name = el.text.strip()
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

    def _scrape_assignments_from_course(self, course_name: str, course_url: str) -> List[Dict[str, Any]]:
        """単一のコースページから課題情報をスクレイピングします。

        ページの形式（トピック/週形式 or タブ形式）を判別し、適切な処理を呼び出します。

        Args:
            course_name (str): コース名。
            course_url (str): コースページのURL。

        Returns:
            List[Dict[str, Any]]: そのコース内の課題情報のリスト。
        """
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

    def _scrape_topic_week_page(self, course_name: str, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """トピック形式または週形式のコースページから課題をスクレイピングします。

        Args:
            course_name (str): コース名。
            soup (BeautifulSoup): 解析対象のページのBeautifulSoupオブジェクト。

        Returns:
            List[Dict[str, Any]]: そのページ内の課題情報のリスト。
        """
        self.logger.info(f"授業「{course_name}」: topic/week形式のページを処理します。")
        return self._process_assign_on_current_page(course_name, soup)

    def _scrape_tab_page(self, course_name: str, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """タブ形式のコースページを処理します。

        各タブを巡回し、それぞれのページから課題情報を収集します。

        Args:
            course_name (str): コース名。
            soup (BeautifulSoup): 解析対象のページのBeautifulSoupオブジェクト。

        Returns:
            List[Dict[str, Any]]: そのコース内の全タブの課題情報のリスト。
        """
        self.logger.info(f"授業「{course_name}」: tab形式のページを処理します。")
        assignments: List[Dict[str, Any]] = []
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

    def _process_assign_on_current_page(self, course_name: str, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """現在のページから課題と小テストのリンクを抽出し、詳細情報を取得します。

        Args:
            course_name (str): コース名。
            soup (BeautifulSoup): 解析対象のページのBeautifulSoupオブジェクト。

        Returns:
            List[Dict[str, Any]]: そのページ内の課題情報のリスト。
        """
        assignments: List[Dict[str, Any]] = []
        elements = soup.select("li.modtype_assign a.aalink, li.modtype_quiz a.aalink")
        assign_links = [el.get("href") for el in elements if el.get("href")]

        for assign_url in assign_links:
            assignment_data = self._scrape_assign_details(assign_url, course_name)
            if assignment_data:
                assignments.append(assignment_data)
        return assignments

    def _scrape_assign_details(self, assign_url: str, course_name: str) -> Optional[Dict[str, Any]]:
        """個別の課題ページから詳細情報（タイトル、日時、内容など）を抽出します。

        Args:
            assign_url (str): 課題ページのURL。
            course_name (str): 課題が含まれるコース名。

        Returns:
            Optional[Dict[str, Any]]: 抽出した課題情報の辞書。失敗した場合はNone。
        """
        try:
            res = self.session.get(assign_url, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')

            title, date, content, is_submitted = None, None, None, False

            # 課題期日の取得
            info_div = soup.select_one("div.activity-information")
            if info_div:
                title = info_div.get("data-activityname")
            else:
                self.logger.warning(f"URL: {assign_url} で課題タイトルが見つかりませんでした。")

            date_div = soup.select_one("div.activity-dates")
            if date_div:
                date_text = date_div.get_text()
                date = self._parse_start_end_datetimes(date_text, self.lang_code)
            else:
                self.logger.warning(f"URL: {assign_url} で課題期日が見つかりませんでした。")

            # 課題内容の取得
            content_div = soup.select_one("div.activity-description")
            if content_div:
                content = content_div.text.strip()
            else:
                self.logger.warning(f"URL: {assign_url} でactivity-descriptionが見つかりませんでした。")

            start_date, due_date = (date[0], date[1]) if date else (None, None)

            # 課題が提出済みかの判断
            if 'assign' in assign_url:
                is_submitted = self._scrape_is_submitted_assign(assign_url, soup)
            elif 'quiz' in assign_url:
                is_submitted = self._scrape_is_submitted_quiz(assign_url, soup)
            else:
                self.logger.warning(f"URL: {assign_url} が課題か小テストかを判断できませんでした。")

            self.logger.info(f"課題取得: {title}, URL: {assign_url}, 期日: {due_date}")
            return {
                'title': title,
                'url': assign_url,
                'course': course_name,
                'start_date': start_date,
                'due_date': due_date,
                'content': content,
                'is_submitted': is_submitted
            }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"課題詳細ページの取得に失敗しました ({assign_url}): {e}")
            return None
    
    def _scrape_is_submitted_assign(self, assin_url: str, soup: BeautifulSoup) -> bool:
        """課題ページから提出ステータスを取得し返します。

        Args:
            assign_url (str): 課題ページのURL。
            soup (BeautifulSoup): 解析対象のページのBeautifulSoupオブジェクト。

        Returns:
            bool: 提出済みならTrue、未提出、取得できない場合はFalse。
        """
        is_submitted = False
        td_submitted = soup.select_one("div.submissionstatustable td.submissionstatussubmitted")
        if td_submitted:
            is_submitted = True
        return is_submitted
    
    def _scrape_is_submitted_quiz(self, assin_url: str, soup: BeautifulSoup) -> bool:
        """小テストページから提出ステータスを取得し返します。

        Args:
            assign_url (str): 課題ページのURL。
            soup (BeautifulSoup): 解析対象のページのBeautifulSoupオブジェクト。
        Returns:
            bool: 提出済みならTrue、未提出、取得できない場合はFalse。
        """
        is_submitted = False
        div_submitted = soup.select_one("#feedback")
        if div_submitted:
            is_submitted = True
        return is_submitted

    @classmethod
    def _parse_start_end_datetimes(cls, text: str, lang_code: Optional[str], tz_str: str = "Asia/Tokyo") -> Tuple[Optional[datetime], Optional[datetime]]:
        """日付情報を含む文字列を解析し、開始日時と終了日時のタプルを返します。

        Args:
            text (str): 解析対象の日付・時刻情報を含むテキスト。
            lang_code (Optional[str]): 言語コード ('en', 'ja'など)。日付フォーマットの識別に利用。
            tz_str (str, optional): タイムゾーン文字列。デフォルトは "Asia/Tokyo"。

        Returns:
            Tuple[Optional[datetime], Optional[datetime]]: (開始日時, 終了日時) のタプル。
                見つからない場合はNone。
        """
        start_dt, end_dt = None, None

        if not lang_code or lang_code not in cls._DATE_CONFIG:
            lang_code = 'ja'  # デフォルトとして日本語を設定

        config = cls._DATE_CONFIG[lang_code]
        pattern = config['pattern']

        try:
            tz = ZoneInfo(tz_str)
        except Exception:
            tz = ZoneInfo("UTC")

        for line in text.splitlines():
            match = pattern.search(line)
            if not match:
                continue

            try:
                parts = dict(zip(config['group_order'], match.groups()))
                time_parts: Dict[str, int] = {k: int(v) for k, v in parts.items() if v and k in ['year', 'month', 'day', 'hour', 'minute']}

                if 'month_str' in parts and 'month_map' in config and parts['month_str']:
                    time_parts['month'] = config['month_map'][parts['month_str'].lower()]

                if 'ampm' in parts and parts['ampm']:
                    hour = time_parts.get('hour', 0)
                    if parts['ampm'].lower() == 'pm' and hour != 12:
                        hour += 12
                    elif parts['ampm'].lower() == 'am' and hour == 12:
                        hour = 0
                    time_parts['hour'] = hour

                naive_dt = datetime(**time_parts)
                aware_dt = naive_dt.replace(tzinfo=tz)

                if any(keyword in line for keyword in config['start_keywords']):
                    start_dt = aware_dt
                elif any(keyword in line for keyword in config['end_keywords']):
                    end_dt = aware_dt
            except (ValueError, KeyError, TypeError) as e:
                logging.warning(f"日付の解析に失敗しました: {line.strip()}, lang: {lang_code}, error: {e}")
                continue

        return (start_dt, end_dt)

    def _extract_lang_code(self, soup: BeautifulSoup) -> str:
        """テキストから括弧で囲まれた言語コード (例: "(ja)") を抽出します。

        Args:
            soup (BeautifulSoup): 解析対象のページのBeautifulSoupオブジェクト。

        Returns:
            str: 見つかった言語コード。複数ある場合は最後のものを返す。見つからない場合は日本語。
        """
        # 言語コードの特定
        lang_div = soup.select_one("div.container-fluid a.dropdown-toggle.nav-link")
        if lang_div:
            lang_text = lang_div.text
        else:
            self.logger.warning(f"言語を特定するための要素が見つかりませんでした。")

        matches = re.findall(r'\(([a-zA-Z\-_]+)\)', lang_text)

        if matches:
            # 複数マッチした場合、最後のものを言語コードとみなして返す
            self.logger.info(f"特定された言語コードは{matches[-1]}です。")
            return matches[-1]
        else:
            # マッチするものが一つもなければ日本語を適用
            self.logger.warning(f"言語コードが見つかりませんでした。日本語を適用します。")
            return 'ja'