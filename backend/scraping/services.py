import os
import logging
from dotenv import load_dotenv

# ScrapyのCrawlerProcessとSettingsをインポート
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy import signals

# Djangoのモデルと、作成したScrapyの設定モジュールをインポート
from accounts.models import User
from .crawlers import settings as crawler_settings_module
from .crawlers.spiders.moodle_spider import MoodleSpider
from .crawlers.spiders.webclass_spider import WebclassSpider, LogoutException

load_dotenv()
logger = logging.getLogger(__name__)

def _run_spider(spider_cls, user: User, password: str, login_url: str):
    """
    指定されたSpiderをCrawlerProcessで実行し、終了ステータスを監視する共通関数
    """
    if not login_url:
        msg = f"環境変数で {spider_cls.name} のURLが設定されていません。"
        logger.error(msg)
        raise ValueError(msg)

    # スパイダーの失敗理由を記録するためのリスト
    failures = []

    # スパイダーが閉じたときに呼び出される関数
    def spider_closed(spider, reason):
        # 'finished' は正常終了を意味する
        if reason != 'finished':
            # 正常終了以外の場合、失敗理由をリストに追加
            failure_reason = f"Spider '{spider.name}' closed with reason: {reason}"
            failures.append(failure_reason)
            logger.error(f"Spider '{spider.name}' for user '{user.university_id}' closed unexpectedly. Reason: {reason}")

    try:
        settings = Settings()
        settings.setmodule(crawler_settings_module, priority='project')
        
        process = CrawlerProcess(settings, install_root_handler=False)
        
        crawler = process.create_crawler(spider_cls)
        
        crawler.signals.connect(spider_closed, signal=signals.spider_closed)

        process.crawl(
            crawler,
            user_pk=user.pk,
            password=password,
            login_url=login_url
        )
        
        process.start() # スパイダーの実行完了までブロック

        # 実行後、failuresリストに何か入っていれば例外を送出
        if failures:
            if any("LogoutException" in reason for reason in failures):
                raise LogoutException("WebClassからログアウトされました。再試行します。")
            raise RuntimeError("Scrapy process failed: " + "; ".join(failures))

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
