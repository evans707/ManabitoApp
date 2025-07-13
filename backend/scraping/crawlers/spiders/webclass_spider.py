import logging
from urllib.parse import urljoin
from datetime import datetime
from zoneinfo import ZoneInfo

import scrapy
from scrapy.http import Response
from playwright.async_api import Page

from scraping.crawlers.items import AssignmentItem


class LogoutException(Exception):
    """ログアウトを検知した際に発生させるカスタム例外"""
    pass


class WebclassSpider(scrapy.Spider):
    """
    WebClassから課題情報をスクレイピングするSpider。
    強制的にログアウトされる場合があり、処理が不安定。
    ログアウトした場合はLogoutExceptionを送出し、やり直しを求める。
    """
    name = "webclass"
    
    BASE_DOMAIN = "https://els.sa.dendai.ac.jp"

    custom_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True
        },
        'PLAYWRIGHT_PROCESS_REQUEST_HEADERS': None,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 3,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 3,
        # 'PLAYWRIGHT_MAX_CONTEXTS': 3,
        # 'PLAYWRIGHT_MAX_PAGES_PER_CONTEXT': 3,
        'LOG_LEVEL': 'INFO',
    }

    def __init__(self, user_pk=None, password=None, login_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not all([user_pk, password, login_url]):
            raise ValueError("user_pk, password, and login_url must be provided")
        
        self.user_pk = user_pk
        self.username = str(user_pk)
        self.password = password
        self.login_url = login_url
        self.log(f"{self.name} spider initialized for user_pk: {self.user_pk}", level=logging.INFO)

    async def start(self):
        """
        スパイダーの開始点。ログインページにアクセスする。
        """
        yield scrapy.Request(
            self.login_url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
            },
            callback=self.login_and_parse_home,
            errback=self.errback_general,
        )

    async def login_and_parse_home(self, response: Response):
        """
        ログイン処理からホームページのパースをする。
        """
        page: Page = response.meta["playwright_page"]
        
        try:
            # --- ログイン処理 ---
            self.log("Attempting to log in...", level=logging.INFO)
            await page.fill("#username", self.username)
            await page.fill("#password", self.password)
            await page.click("#LoginBtn")
            await page.wait_for_selector("a[href*='logout']", timeout=20000)
            self.log("Login successful.", level=logging.INFO)

            # await page.pause()

            # --- 時間割表のコースを抽出 ---
            schedule_loc = page.locator('#schedule-table a, .schedule-list .course .list-group-item-heading')
            raw_schedule_texts = await schedule_loc.all_inner_texts()

            # --- その他のコースを抽出 ---
            other_loc = page.locator('#courses_list_left .course-title a')
            raw_other_texts = await other_loc.all_inner_texts()

            # --- 全てのコース名を一つのリストにまとめる ---
            all_courses = set() # 重複を自動的に削除するためにsetを使用

            # 時間割表のコースを整形して追加
            for text in raw_schedule_texts:
                clean_text = text.strip().replace('» ', '')
                all_courses.add(clean_text)
            
            # その他のコースを整形して追加
            for text in raw_other_texts:
                clean_text = text.strip().replace('» ', '')
                all_courses.add(clean_text)

            current_courses = list(all_courses)
            self.log(f"Found {len(current_courses)} courses on home: {current_courses}", level=logging.INFO)

            # ダッシュボードへのリンクを取得して次のリクエストを生成
            dashboard_link_locator = page.get_by_role('link', name='» ダッシュボード')
            dashboard_path = await dashboard_link_locator.get_attribute('href')
            dashboard_url = response.urljoin(dashboard_path)

            yield scrapy.Request(
                dashboard_url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                },
                callback=self.parse_dashboard_frame,
                errback=self.errback_general,
                cb_kwargs={"current_courses": current_courses},
            )

        except Exception as e:
            self.log(f"An error occurred during the scraping process: {e}", level=logging.ERROR)
        finally:
            # すべての処理が完了したらページを閉じる
            self.log("Closing home page.", level=logging.INFO)
            await page.close()
    
    async def parse_dashboard_frame(self, response: Response, current_courses):
        """
        ダッシュボードのパースをする。
        """
        page: Page = response.meta["playwright_page"]

        try:
            await page.wait_for_load_state("networkidle")

            # await page.pause()

            await page.locator("main[role='main']").wait_for(timeout=10000)
            self.log("Dashboard loaded. Scraping courses...", level=logging.INFO)

            course_link_locators = page.locator('a.font-semibold[target="course"]')
            
            for course_link_locator in await course_link_locators.all():
                course_name = (await course_link_locator.text_content() or "").strip()
                if course_name not in current_courses:
                    # self.log(f"Skipping dashboard course '{course_name}' as it's not on the main timetable/list.", level=logging.INFO)
                    continue

                course_url_path = await course_link_locator.get_attribute("href")
                if not (course_name and course_url_path):
                    continue

                course_data = {
                    "name": course_name,
                    "url": urljoin(self.BASE_DOMAIN, course_url_path),
                    "assignments": []
                }

                # 課題概要テーブルを検索・解析
                course_locator = course_link_locator.locator('../..')
                table_locator = course_locator.locator("table")
                if await table_locator.count() > 0:
                    headers = [await h.text_content() for h in await table_locator.locator("thead th").all()]
                    if not headers: headers = ["教材", "締切", "実施日", "最高点", "状態"]

                    for row_locator in await table_locator.locator("tbody tr").all():
                        cols_text = [await col.text_content() for col in await row_locator.locator("td").all()]
                        if len(cols_text) < len(headers): continue
                        assign_data = {headers[k].strip(): col_text.strip() for k, col_text in enumerate(cols_text)}
                        course_data["assignments"].append(assign_data)

                if not course_data["assignments"]:
                    self.log(f"Not Found assignments in {course_data['name']} on dashboard.", level=logging.INFO)
                    continue
                self.log(f"Found {len(course_data['assignments'])} assignments in {course_data['name']} on dashboard.", level=logging.INFO)

                # コースページへのリクエストを生成
                yield scrapy.Request(
                    course_data['url'],
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                    },
                    callback=self.parse_course_page,
                    errback=self.errback_general,
                    cb_kwargs={"course_data": course_data},
                )

        except Exception as e:
            self.log(f"An error occurred during dashboard parsing: {e}", level=logging.ERROR)
        finally:
            if page and not page.is_closed():
                self.log("Closing dashboard page.", level=logging.INFO)
                await page.close()
    
    async def parse_course_page(self, response: Response, course_data):
        """
        単一のコースページをパースし、各課題詳細ページへのリクエストを生成する。
        """
        page: Page = response.meta["playwright_page"]
        
        try:
            logout_locator = page.locator("p.logout-screen-bottom-message, div.alert:has-text('別のコースへのアクセス')")
            if response.status == 401 or await logout_locator.count() > 0:
                self.log(f"Logout: Parsing course for '{course_data['name']}'", level=logging.ERROR)
                raise LogoutException(f"Logout detected on course page for '{course_data['name']}'")

            self.log(f"Parsing course for '{course_data['name']}'...", level=logging.INFO)
            await page.wait_for_selector('div.cl-contentsList_content', timeout=10000)

            assignments_dict = {a.get("教材"): a for a in course_data.get("assignments", []) if a.get("教材")}

            now = datetime.now(ZoneInfo("Asia/Tokyo"))

            for content_locator in await page.locator('div.cl-contentsList_content').all():
                # タイトル取得
                content_name_locator = content_locator.locator('h4.cm-contentsList_contentName')
                content_name = (await content_name_locator.text_content() or "").strip()
                if not content_name or content_name not in assignments_dict:
                    # ダッシュボードの課題リストに存在しなければ無視
                    continue
                
                found_assign = assignments_dict[content_name]

                # 課題データ作成
                assign_data = {'course_name': course_data["name"], "title": content_name}
                item = AssignmentItem()
                item['user_pk'] = self.user_pk
                item['platform'] = self.name
                item['course_name'] = course_data["name"]
                item['title'] = content_name

                # 課題カテゴリーを課題内容に使用
                content_categoryLabel_locator = content_locator.locator("div.cl-contentsList_categoryLabel")
                item['content'] = await content_categoryLabel_locator.text_content() or ""

                # 課題が提出済みか判断
                status_text = found_assign.get('実施日')
                item['is_submitted'] = not(status_text == '-' or status_text is None)

                # 課題期間の取得
                date_locator = content_locator.locator("div.cl-contentsList_contentInfo div.cm-contentsList_contentDetailListItemData")
                if await date_locator.count() > 0:
                    date_text = await date_locator.text_content()
                    item['start_date'], item['due_date'] = self._parse_datetime_range(date_text)
                else:
                    item['start_date'], item['due_date'] = (None, None)

                # 課題URLを取得、期限切れならコースURLを使用
                item['url'] = course_data["url"]
                is_expired = item['due_date'] is not None and now > item['due_date']
                if not is_expired:
                    content_link_locator = content_name_locator.locator("a")
                    if await content_link_locator.count() > 0:
                        content_url_path = await content_link_locator.first.get_attribute("href")
                        item['url'] = urljoin(self.BASE_DOMAIN, content_url_path)
                    else:
                        self.log(f"Could not find active assignment link for '{content_name}'. Defaulting to course URL.", level=logging.WARNING)

                # 課題の保存
                self.log(f"Created item: {item['title']} for course {item['course_name']}", level=logging.INFO)
                yield item
        
        except LogoutException as e:
            self.log(f"Error parsing course page '{course_data['name']}': {e}", level=logging.ERROR)
            raise
        except Exception as e:
            self.log(f"Error parsing course page '{course_data['name']}': {e}", level=logging.WARNING)
        finally:
            if page and not page.is_closed():
                self.log(f"Closing course page for '{course_data['name']}' .", level=logging.INFO)
                await page.close()

    @staticmethod
    def _parse_datetime_range(datetime_range_str: str) -> tuple[datetime, datetime]:
        """
        "YYYY/MM/DD HH:MM - YYYY/MM/DD HH:MM" 形式の文字列を
        二つのdatetimeオブジェクトに変換してタプルで返します。
        """
        try:
            start_str, end_str = datetime_range_str.split(' - ')
            datetime_format = "%Y/%m/%d %H:%M"
            tz = ZoneInfo("Asia/Tokyo")
            start_datetime = (datetime.strptime(start_str.strip(), datetime_format)).replace(tzinfo=tz)
            end_datetime = (datetime.strptime(end_str.strip(), datetime_format)).replace(tzinfo=tz)
            return start_datetime, end_datetime
        except ValueError:
            return None, None

    async def errback_general(self, failure):
        """
        エラー発生時にPlaywrightのページを閉じる汎用エラーバック。
        """
        self.log(f"Request failed: {failure.request.url} | Error: {failure.value}", level=logging.ERROR)
        page = failure.request.meta.get("playwright_page")
        if page and not page.is_closed():
            self.log(f"Closing page for failed request: {failure.request.url}", level=logging.INFO)
            await page.close()