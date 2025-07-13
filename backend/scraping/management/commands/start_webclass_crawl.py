import os
import logging
from dotenv import load_dotenv

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from scraping.crawlers import settings as crawler_settings
from scraping.crawlers.spiders.webclass_spider import WebclassSpider


# 環境変数のロード
load_dotenv()

# 環境変数の読み込み
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
WEBCLASS_LOGIN_URL = os.getenv('WEBCLASS_LOGIN_URL')

# 環境変数が設定されているか確認
if not all([USERNAME, PASSWORD, WEBCLASS_LOGIN_URL]):
    logging.error("エラー: .envファイルに USERNAME, PASSWORD, WEBCLASS_LOGIN_URL のいずれか、または複数が設定されていません。")
    exit() # スクリプトを終了

User = get_user_model()

class Command(BaseCommand):
    help = '環境変数で指定されたユーザーのwebclass課題をスクレイピングします'

    def handle(self, *args, **options):
        university_id = USERNAME
        password = PASSWORD
        login_url = WEBCLASS_LOGIN_URL

        try:
            user = User.objects.get(university_id=university_id)
            self.stdout.write("="*50)
            self.stdout.write(self.style.SUCCESS(f"スクレイピング開始: Moodle for {user.university_id} (User PK: {user.pk})"))
            self.stdout.write("="*50)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'ユーザーが見つかりません: university_id={university_id}'))
            return

        settings = Settings()
        settings.setmodule(crawler_settings)
        
        process = CrawlerProcess(settings)

        # Spiderにはuser.pk (主キー) を渡す
        process.crawl(
            WebclassSpider,
            user_pk=user.pk,
            password=password,
            login_url=login_url,
        )
        process.start()

        self.stdout.write("="*50)
        self.stdout.write(self.style.SUCCESS('スクレイピングが正常に完了しました。'))
        self.stdout.write("="*50)