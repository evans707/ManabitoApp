import os
import logging
from dotenv import load_dotenv

# ScrapyのCrawlerProcessとSettingsをインポート
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

# Djangoのモデルと、作成したScrapyの設定モジュールをインポート
from accounts.models import User
from .crawlers import settings as crawler_settings_module
from .crawlers.spiders.moodle_spider import MoodleSpider
from .crawlers.spiders.webclass_spider import WebclassSpider

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
        settings = Settings()
        settings.setmodule(crawler_settings_module, priority='project')
        
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
