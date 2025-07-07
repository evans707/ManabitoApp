import re
import logging
from urllib.parse import urljoin
from datetime import datetime
from zoneinfo import ZoneInfo

import scrapy
from scrapy.http import Request, Response
from playwright.async_api import Page, Frame, Locator

from scraping.crawlers.items import AssignmentItem

class WebclassSpider(scrapy.Spider):
    """
    東京電機大学のWebClassから課題情報をスクレイピングするSpider。
    Playwrightの機能のみを使用し、BeautifulSoupには依存しない。
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
            'headless': False
        },
        'PLAYWRIGHT_PROCESS_REQUEST_HEADERS': None
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

    def start_requests(self):
        """
        スパイダーの開始点。ログインページにアクセスする。
        """
        yield scrapy.Request(
            self.login_url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                # ページの自動クローズを無効にし、手動で管理する
                "playwright_page_coroutines": [
                    # このリクエストが完了してもページを閉じないようにする
                    lambda page: page.wait_for_timeout(1) 
                ]
            },
            callback=self.login_and_scrape,
            errback=self.errback_close_page,
        )

    async def login_and_scrape(self, response: Response):
        """
        ログイン処理からサイト全体のスクレイピングまでを一貫して実行する。
        これにより、同じpageオブジェクト（＝セッション）を維持する。
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

            # --- ダッシュボードから全コース情報を取得 ---
            courses_data = await self._get_courses_from_dashboard(page, current_courses)
            if not courses_data:
                self.log("No courses found on dashboard. Exiting.", level=logging.INFO)
                return

            # --- 各コースを順番に処理 ---
            for course in courses_data:
                if len(course["assignments"])==0:
                    self.log(f"Not Found assignments in {course['name']}.", level=logging.INFO)
                    continue
                # page.goto()を使って同じページオブジェクトで画面遷移する
                self.log(f"Navigating to course page: {course['name']}", level=logging.INFO)
                await page.goto(course['url'])
                
                # 遷移したコースページから課題情報をパースしてItemをyieldする
                async for item in self._parse_course_page(page, course):
                    yield item

        except Exception as e:
            self.log(f"An error occurred during the scraping process: {e}", level=logging.ERROR)
        finally:
            # すべての処理が完了したらページを閉じる
            self.log("Closing page.", level=logging.INFO)
            await page.close()

    async def _get_courses_from_dashboard(self, page: Page, current_courses: list) -> list:
        """
        ダッシュボードをパースし、すべてのコースと課題の概要情報をリストとして返す。
        この時点では画面遷移しない。
        """
        try:
            await page.get_by_role('link', name='» ダッシュボード').click()
            iframe = page.frame_locator("#ip-iframe")
            await iframe.locator("main[role='main']").wait_for(timeout=5000)
            self.log("Dashboard iframe loaded. Scraping courses...", level=logging.INFO)

            self.log("Waiting for the first course link to appear...", level=logging.INFO)
            first_course_link = iframe.locator('a.font-semibold[target="course"]').first
            await first_course_link.wait_for(timeout=5000)
            self.log("Dashboard iframe content loaded.", level=logging.INFO)
            
            # await page.pause()

            # --- コース情報を抽出 ---
            course_link_locators = iframe.locator('a.font-semibold[target="course"]')
            course_count = await course_link_locators.count()
            self.log(f"Found {course_count} courses in dashboard.", level=logging.INFO)

            courses = []
            for course_link_locator in await course_link_locators.all():
                course_name = (await course_link_locator.text_content()).strip()
                # ホームに存在しないコースは処理を飛ばす
                if course_name not in current_courses:
                    self.log(f"Skipping dashboard course '{course_name}' as it's not on the main timetable/list.", level=logging.INFO)
                    continue

                course_locator = course_link_locator.locator('../..')
                course_url_path = await course_link_locator.get_attribute("href")

                if not (course_name and course_url_path):
                    continue

                course = {
                    "name": course_name, 
                    "url": urljoin(self.BASE_DOMAIN, course_url_path), 
                    "assignments": []
                }

                # --- 課題概要テーブルを検索・解析 ---
                self.log(f"Parsing course table for '{course['name']}'...", level=logging.INFO)
                table_locator = course_locator.locator("table")
                if await table_locator.count() == 0:
                    self.log(f"Not Found assignments in {course_name}.", level=logging.INFO)
                    continue
                if await table_locator.count() > 0:
                    headers = [await h.text_content() for h in await table_locator.locator("thead th").all()]
                    if not headers: headers = ["教材", "締切", "実施日", "最高点", "状態"]

                    for row_locator in await table_locator.locator("tbody tr").all():
                        cols_text = [await col.text_content() for col in await row_locator.locator("td").all()]
                        if len(cols_text) < len(headers): continue
                        assign_data = {headers[k].strip(): col_text.strip() for k, col_text in enumerate(cols_text)}
                        course["assignments"].append(assign_data)
                
                courses.append(course)
            
            return courses
        except Exception as e:
            self.log(f"An error occurred during dashboard parsing: {e}", level=logging.ERROR)
            return []
            
    async def _parse_course_page(self, page: Page, course_data: dict):
        """
        単一のコースページをパースし、課題詳細を取得してItemをyieldする。
        """
        self.log(f"Parsing course for '{course_data['name']}'...", level=logging.INFO)
        try:
            await page.wait_for_selector('div.cl-contentsList_content', timeout=10000)

            assignments_dict = {a.get("教材"): a for a in course_data.get("assignments", []) if a.get("教材")}

            for content_locator in await page.locator('div.cl-contentsList_content').all():
                name_locator = content_locator.locator('h4.cm-contentsList_contentName')
                content_name = (await name_locator.text_content() or "").strip()
                if not content_name or content_name not in assignments_dict:
                    continue
                
                found_assign = assignments_dict[content_name]
                self.log(f"Found matching assignment: '{content_name}'", level=logging.INFO)

                assign_data = {'course_name': course_data["name"], "title": content_name}
                status_text = found_assign.get('実施日')
                assign_data["is_submitted"] = not(status_text == '-' or status_text is None)

                date_locator = content_locator.locator(".cl-contentsList_contentInfo .cm-contentsList_contentDetailListItemData")
                if await date_locator.count() > 0:
                    date_text = await date_locator.text_content()
                    assign_data["start_date"], assign_data["due_date"] = self._parse_datetime_range(date_text)
                else:
                    assign_data["start_date"], assign_data["due_date"] = (None, None)

                detail_link_locator = content_locator.locator("a[href*='/contents/']")
                if await detail_link_locator.count() > 0:
                    content_url_path = await detail_link_locator.first.get_attribute("href")
                    content_detail_url = urljoin(self.BASE_DOMAIN, content_url_path)

                    # 詳細ページに遷移してパースし、Itemを生成する
                    item = await self._parse_assignment_detail(page, content_detail_url, assign_data)
                    yield item

                    # 元のコースページに戻って次の課題を探す
                    await page.go_back()
                    await page.wait_for_selector('div.cl-contentsList_content', timeout=10000) # 戻ったことを確認
                else:
                    self.log(f"Could not find detail link for '{content_name}'", level=logging.WARNING)
        except Exception as e:
            self.log(f"Error parsing course page '{course_data['name']}': {e}", level=logging.WARNING)

    async def _parse_assignment_detail(self, page: Page, detail_url: str, assign_data: dict) -> AssignmentItem:
        """
        課題詳細ページに遷移し、情報をパースしてAssignmentItemを返す。
        """
        await page.goto(detail_url)
        self.log(f"Parsing assignment detail for '{assign_data['title']}'...", level=logging.INFO)
        try:
            item = AssignmentItem()
            item['user_pk'] = self.user_pk
            item['platform'] = self.name
            item['course_name'] = assign_data["course_name"]
            item['title'] = assign_data["title"]
            item['start_date'] = assign_data.get("start_date")
            item['due_date'] = assign_data.get("due_date")
            item['is_submitted'] = assign_data["is_submitted"]
            item['content'] = ''
            
            submission_url = page.url # デフォルトは現在のURL
            assign_url_locator = page.locator("span#execUrlTarget")
            if await assign_url_locator.count() > 0:
                url_from_span = await assign_url_locator.text_content()
                if url_from_span:
                    submission_url = url_from_span.strip()

            item['url'] = submission_url

            self.log(f"Created item: {item['title']} for course {item['course_name']}", level=logging.INFO)
            return item
        except Exception as e:
            self.log(f"Error parsing assignment page for '{assign_data['title']}': {e}", level=logging.ERROR)
            return None # エラー時はNoneを返す

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

    async def errback_close_page(self, failure):
        """エラー発生時にPlaywrightのページを閉じる。"""
        page = failure.request.meta.get("playwright_page")
        if page and not page.is_closed():
            self.log(f"Closing page due to an error: {failure.value}", level=logging.ERROR)
            await page.close()