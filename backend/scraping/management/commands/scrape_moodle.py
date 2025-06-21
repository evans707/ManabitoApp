import os
import logging
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from scraping.scraper_moodle import MoodleScraper

# Djangoのモデルとプロジェクト設定をインポート
from scraping.models import Assignment, Course
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
                # ログイン処理
                if not scraper.login():
                    logger.warning(f"ユーザー'{moodle_username}'のMoodleへのログインに失敗しました。")
                    raise ConnectionError("Moodleへのログインに失敗しました。ユーザー名またはパスワードが間違っている可能性があります。")
                logger.info(f"ユーザー'{moodle_username}'のログイン成功。課題の取得を開始します。")

                # 課題データの取得
                assignments_data = scraper.scrape_all_assignments()
                if not assignments_data:
                    logger.warning(f"ユーザー'{moodle_username}'の課題をスクレイピングしましたが、取得結果は0件でした。")

                saved_count = 0
                updated_count = 0
                
                # データベースに保存
                for item in assignments_data:
                    url = item.get('url')
                    course_title = item.get('course', '不明なコース')
                    
                    # URLがない場合はスキップ（キーとなるデータのため）
                    if not url:
                        logger.warning(f"URLが含まれていないため、課題データをスキップしました: {item}")
                        continue

                    # Courseを取得または作成
                    course, _ = Course.objects.get_or_create(
                        user=user,
                        title=course_title
                    )

                    obj, created = Assignment.objects.update_or_create(
                        user=user,
                        url=url,
                        defaults={
                            'course': course,
                            'title': item.get('title', 'タイトルなし'),
                            'content': item.get('content'), # contentはnull許容なのでデフォルト値なしでもOK
                            'due_date': item.get('due_date'),
                            'is_submitted': item.get('is_submitted', False)
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
