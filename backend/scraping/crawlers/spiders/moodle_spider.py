import re
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Tuple, Optional, Dict, Any

import scrapy
from scraping.crawlers.items import AssignmentItem

class MoodleSpider(scrapy.Spider):
    """
    Moodleサイトから課題情報をスクレイピングするSpider。
    HTTPリクエストのみで動作し、Playwrightは使用しない。
    """
    name = 'moodle'

    _MONTH_MAP_EN: Dict[str, int] = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
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

    def __init__(self, user_pk, password, login_url, *args, **kwargs):
        """
        Spider実行時に引数を受け取るコンストラクタ。
        Management CommandやCeleryタスクから渡される。
        """
        super(MoodleSpider, self).__init__(*args, **kwargs)
        self.user_pk = user_pk
        self.username = str(user_pk) # ログインIDとして使用
        self.password = password
        self.login_url = login_url
        self.home_url = None
        self.lang_code = 'ja'
    
    async def start(self):
        """
        クロールの起点となるメソッド。
        まずログインページにアクセスし、コールバックとして `parse_login_token` を指定。
        """
        yield scrapy.Request(
            url=self.login_url,
            callback=self.parse_login_token,
        )

    def parse_login_token(self, response):
        """
        ログインページからlogintokenを抽出し、ログイン情報をPOSTする。
        """
        logintoken = response.css('input[name="logintoken"]::attr(value)').get()
        if not logintoken:
            self.logger.error("ログインページのlogintokenが見つかりませんでした。")
            return

        self.logger.info("logintokenを取得し、ログインを試みます。")
        yield scrapy.FormRequest.from_response(
            response,
            formdata={
                'username': self.username,
                'password': self.password,
                'logintoken': logintoken,
            },
            callback=self.parse_dashboard
        )
    
    def parse_dashboard(self, response):
        """
        ログイン後のダッシュボードページを解析する。
        """
        # ログイン成功をユーザーメニューの有無で判定
        if not response.css("div.usermenu"):
            error_msg = "".join(response.css('div.alert-danger ::text').getall()).strip()
            self.logger.error(f"ログインに失敗しました。エラー: {error_msg or 'ユーザーメニューが見つかりません'}")
            return
        
        self.logger.info("ログインに成功しました。")
        self.home_url = response.url
        self._extract_lang_code(response)

        # コース一覧のリンクを抽出し、各コースページへのリクエストを生成
        self.logger.info("トップページから授業一覧を取得します...")
        course_links = response.css('section[data-block="course_list"] ul.unlist a')
        self.logger.info(f"{len(course_links)} 件のコース要素が見つかりました。")

        for link in course_links:
            course_name = link.css('::text').get('').strip()
            course_url = response.urljoin(link.css('::attr(href)').get())
            if course_name and course_url:
                yield scrapy.Request(
                    url=course_url,
                    callback=self.parse_course,
                    cb_kwargs={'course_name': course_name},
                )

    def parse_course(self, response, course_name):
        """
        コースページを解析し、課題とタブのリンクをたどる。
        """
        self.logger.info(f"授業「{course_name}」を処理中")

        # 課題(assign)と小テスト(quiz)のリンクを抽出
        for link in response.css("li.modtype_assign a.aalink, li.modtype_quiz a.aalink"):
            yield response.follow(
                link,
                callback=self.parse_assignment_details,
                cb_kwargs={'course_name': course_name},
            )
        
        # タブ形式のページの場合、各タブのリンクもたどる
        # response.followは重複するURLへのリクエストを自動的にフィルタリングしてくれる
        for link in response.css("div.tabs-wrapper a.nav-link"):
            yield response.follow(
                link,
                callback=self.parse_course,
                cb_kwargs={'course_name': course_name},
            )

    def parse_assignment_details(self, response, course_name):
        """
        課題詳細ページから情報を抽出し、AssignmentItemに格納してPipelineに渡す。
        """
        item = AssignmentItem()
        item['user_pk'] = self.user_pk
        item['platform'] = self.name
        item['course_name'] = course_name
        item['title'] = response.css("div.activity-information::attr(data-activityname)").get("").strip()
        item['url'] = response.url
        
        # 課題詳細
        content_html = response.css("div.activity-description").get()
        if content_html:
            item['content'] = "".join(scrapy.Selector(text=content_html).css('::text').getall()).strip()
        else:
            item['content'] = ""

        # 提出状況
        if 'assign' in response.url:
            item['is_submitted'] = bool(response.css("div.submissionstatustable td.submissionstatussubmitted").get())
        elif 'quiz' in response.url:
            item['is_submitted'] = bool(response.css("div#feedback").get())
        else:
            item['is_submitted'] = False

        # 日付情報
        date_text = response.css("div.activity-dates").get()
        start_date, due_date = self._parse_start_end_datetimes(date_text, self.lang_code)
        item['start_date'] = start_date
        item['due_date'] = due_date

        self.logger.info(f"課題取得: {item['title']}, 期日: {item['due_date']}")
        yield item

    def _extract_lang_code(self, response):
        """ページから言語コードを抽出する"""
        lang_text = response.css("div.container-fluid a.dropdown-toggle.nav-link::text").get('')
        matches = re.findall(r'\(([a-zA-Z\-_]+)\)', lang_text)
        if matches:
            self.lang_code = matches[-1]
            self.logger.info(f"特定された言語コードは {self.lang_code} です。")
        else:
            self.lang_code = 'ja'
            self.logger.warning("言語コードが見つかりませんでした。デフォルトの 'ja' を適用します。")

    def _parse_start_end_datetimes(self, text: str, lang_code: Optional[str], tz_str: str = "Asia/Tokyo") -> Tuple[Optional[datetime], Optional[datetime]]:
        """日付情報を含むHTMLテキストを解析し、開始・終了日時を返す"""
        if not text:
            return None, None
            
        start_dt, end_dt = None, None
        config = self._DATE_CONFIG.get(lang_code, self._DATE_CONFIG['ja'])
        pattern = config['pattern']
        tz = ZoneInfo(tz_str)

        clean_text = "".join(scrapy.Selector(text=text).css('::text').getall())
        for line in clean_text.splitlines():
            match = pattern.search(line)
            if not match:
                continue
            try:
                # 日付と時刻の解析ロジック（従来通り）
                parts = dict(zip(config['group_order'], match.groups()))
                time_parts: Dict[str, int] = {k: int(v) for k, v in parts.items() if v and k in ['year', 'month', 'day', 'hour', 'minute']}
                if 'month_str' in parts and 'month_map' in config and parts['month_str']:
                    time_parts['month'] = self._MONTH_MAP_EN[parts['month_str'].lower()]
                if 'ampm' in parts and parts['ampm']:
                    hour = time_parts.get('hour', 0)
                    if parts['ampm'].lower() == 'pm' and hour != 12: hour += 12
                    elif parts['ampm'].lower() == 'am' and hour == 12: hour = 0
                    time_parts['hour'] = hour
                naive_dt = datetime(**time_parts)
                aware_dt = naive_dt.replace(tzinfo=tz)

                if any(keyword in line for keyword in config['start_keywords']):
                    start_dt = aware_dt
                elif any(keyword in line for keyword in config['end_keywords']):
                    end_dt = aware_dt
            except (ValueError, KeyError, TypeError) as e:
                self.logger.warning(f"日付の解析に失敗しました: {line.strip()}, lang: {lang_code}, error: {e}")
                continue
        return start_dt, end_dt