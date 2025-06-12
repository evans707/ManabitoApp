import os
import logging
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from scraping.scraper_moodle import MoodleScraper

# Djangoのモデルとプロジェクト設定をインポート
from scraping.models import Assignment
from accounts.models import User

# .envファイルをロード
load_dotenv()

# ロガーの設定
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Moodleから課題をスクレイピングし、データベースに保存する'

    def add_arguments(self, parser):
        parser.add_argument('moodle_username', type=str, help='Moodleのユーザー名')

    def handle(self, *args, **options):
        # コマンドライン引数からユーザー名を取得
        moodle_username = options['moodle_username']

        # Djangoのユーザーを取得
        try:
            user = User.objects.get(university_id=moodle_username)
        except User.DoesNotExist:
            logger.warning(f'存在しないDjangoユーザー "{moodle_username}" でコマンドが実行されました。')
            self.stdout.write(self.style.ERROR(f'Djangoユーザー "{moodle_username}" が見つかりません。'))
            return

        # 環境変数からMoodleのパスワードとURLを取得
        moodle_password = os.getenv('MOODLE_PASSWORD')
        moodle_url = os.getenv('MOODLE_LOGIN_URL')

        if not all([moodle_password, moodle_url]):
            logger.error('.envファイルに MOODLE_PASSWORD と MOODLE_URL が設定されていません。')
            self.stdout.write(self.style.ERROR('.envファイルに MOODLE_PASSWORD と MOODLE_URL を設定してください。'))
            return

        self.stdout.write(f'ユーザー "{moodle_username}" の課題をMoodleから取得します...')

        try:
            with MoodleScraper(moodle_username, moodle_password, moodle_url, logger) as scraper:
                if not scraper.login():
                    raise ConnectionError("Moodleへのログインに失敗しました。ユーザー名またはパスワードが間違っている可能性があります。")
                assignments_data = scraper.scrape_all_assignments()

                if not assignments_data:
                    logger.info(f'ユーザー "{moodle_username}" の課題をスクレイピングしましたが、取得結果は0件でした。')
                    self.stdout.write(self.style.WARNING('取得できた課題はありませんでした。'))
                    return

                # 取得した課題をデータベースに保存
                saved_count = 0
                updated_count = 0
                for item in assignments_data:
                    due_date_aware = None
                    if item['due_date']:
                        due_date_aware = item['due_date']
                    
                    # update_or_createでデータの登録・更新を自動化
                    obj, created = Assignment.objects.update_or_create(
                        user=user,
                        url=item['url'],
                        defaults={
                            'title': item['title'],
                            'content': item['content'],
                            'due_date': due_date_aware,
                        }
                    )
                    if created:
                        saved_count += 1
                    else:
                        updated_count += 1

                self.stdout.write(self.style.SUCCESS(f'処理完了: {saved_count}件の新しい課題を保存し、{updated_count}件の課題を更新しました。'))

        except Exception as e:
            logger.error(f"スクレイピング中にエラーが発生しました: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR('スクリプトの実行中にエラーが発生しました。詳細はログを確認してください。'))
