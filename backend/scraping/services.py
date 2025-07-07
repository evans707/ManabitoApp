import os
import logging
from dotenv import load_dotenv

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from accounts.models import User
from .crawlers.spiders.moodle_spider import MoodleSpider
from .crawlers.spiders.webclass_spider import WebclassSpider
from .scraper_webclass import WebClassScraper

load_dotenv()
logger = logging.getLogger(__name__)

def _run_spider(spider_cls, user: User, password: str, login_url: str):
    """
    指定されたSpiderをCrawlerProcessで実行する共通関数
    """
    if not login_url:
        logger.error(f"環境変数で {spider_cls.name} のURLが設定されていません。")
        raise ValueError(f"{spider_cls.name}のURLが未設定です。")

    try:
        # Scrapyプロジェクトの設定を読み込む
        settings = get_project_settings()
        process = CrawlerProcess(settings)

        # スパイダーを実行。__init__に引数を渡す。
        process.crawl(
            spider_cls,
            user_pk=user.pk,
            password=password,
            login_url=login_url
        )
        # スパイダーの実行が完了するまでブロックする
        process.start()

    except Exception as e:
        logger.error(f"'{user.university_id}'の{spider_cls.name}スクレイピング中にエラー: {e}", exc_info=True)
        raise e


def scrape_moodle(user: User, password: str):
    """
    MoodleSpiderを実行する。
    """
    logger.info(f"ユーザー'{user.university_id}'のMoodleスクレイピング処理を開始します (Spider版)。")
    login_url = os.getenv('MOODLE_LOGIN_URL')
    _run_spider(MoodleSpider, user, password, login_url)
    logger.info(f"ユーザー'{user.university_id}'のMoodleスクレイピング処理が完了しました。")


def scrape_webclass(user: User, password: str):
    """
    WebclassSpiderを実行する。
    """
    logger.info(f"ユーザー'{user.university_id}'のWebClassスクレイピング処理を開始します (Spider版)。")
    login_url = os.getenv('WEBCLASS_LOGIN_URL')
    _run_spider(WebclassSpider, user, password, login_url)
    logger.info(f"ユーザー'{user.university_id}'のWebClassスクレイピング処理が完了しました。")
    

# こちらの方が動作は早いが正確な課題URLを取得できない
# def scrape_webclass(user: User, password: str):
#     """
#     指定されたユーザーのWebClass課題をスクレイピングし、DBに保存する。
#     成功した場合は (保存件数, 更新件数) のタプルを返す。
#     失敗した場合は例外を発生させる。
#     """
#     webclass_username = user.university_id
#     webclass_url = os.getenv('WEBCLASS_LOGIN_URL')

#     logger.info(f"ユーザー'{webclass_username}'のWebClassスクレイピング処理を開始します。")

#     if not webclass_url:
#         logger.error("環境変数 WEBCLASS_LOGIN_URL が設定されていません。")
#         raise ValueError("WebClassのURLが設定されていません。")

#     saved_count = 0
#     updated_count = 0

#     try:
#         with WebClassScraper(webclass_username, password, webclass_url, logger) as scraper:
#             # ログイン処理
#             if not scraper.login():
#                 logger.warning(f"ユーザー'{webclass_username}'のWebClassへのログインに失敗しました。")
#                 raise ConnectionError("WebClassへのログインに失敗しました。ユーザー名またはパスワードが間違っている可能性があります。")

#             logger.info(f"ユーザー'{webclass_username}'のログイン成功。課題の取得を開始します。")

#             # 課題データの取得
#             assignments_data = scraper.scrape_all_assignments()
#             if not assignments_data:
#                 logger.warning(f"ユーザー'{webclass_username}'のWebClass課題をスクレイピングしましたが、取得結果は0件でした。")
            
#             # データベースに保存
#             for item in assignments_data:
#                 item_title = item.get('title')
#                 if not item_title:
#                     logger.warning(f"タイトルが空の課題データが見つかったため、スキップします。データ: {item}")
#                     continue

#                 item_url = item.get('url')

#                 defaults = {
#                     'title': item.get('title'),
#                     'content': item.get('content'),
#                     'due_date': item.get('due_date'),
#                     'is_submitted': item.get('is_submitted', False),
#                 }

#                 if item_url:
#                     obj, created = Assignment.objects.update_or_create(
#                         user=user,
#                         url=item_url,
#                         defaults=defaults
#                     )
#                 else:
#                     logger.warning(f"URLがない課題を処理します: {defaults.get('title')}")
#                     obj, created = Assignment.objects.update_or_create(
#                         user=user,
#                         title=defaults.get('title'),
#                         defaults=defaults
#                     )

#                 if created:
#                     saved_count += 1
#                 else:
#                     updated_count += 1
        
#         logger.info(f"ユーザー'{webclass_username}'のWebClass処理完了: {saved_count}件の新規保存、{updated_count}件の更新。")
#         return (saved_count, updated_count)
    
#     except Exception as e:
#         logger.error(f"ユーザー'{webclass_username}'のWebClassスクレイピング中に予期せぬエラーが発生しました。", exc_info=True)
#         raise e