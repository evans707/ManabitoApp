import os
import logging
import time
from dotenv import load_dotenv

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from celery import group

from scraping.task import scrape_webclass_task, scrape_moodle_task


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
    help = 'celeryで指定されたユーザーのwebclass課題をスクレイピングします'

    def handle(self, *args, **options):
        university_id = USERNAME
        password = PASSWORD
        login_url = WEBCLASS_LOGIN_URL

        try:
            user = User.objects.get(university_id=university_id)
            self.stdout.write("="*50)
            self.stdout.write(self.style.SUCCESS(f"スクレイピング開始: {user.university_id} (User PK: {user.pk})"))
            self.stdout.write("="*50)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'ユーザーが見つかりません: university_id={university_id}'))
            return

        tasks_to_run = group([
            scrape_webclass_task.s(user.pk, password),
            scrape_moodle_task.s(user.pk, password)
        ])

        self.stdout.write("タスクをCeleryに投入しました。完了を待っています...")
        result = tasks_to_run.apply_async()

        try:
            while not result.ready():
                self.stdout.write('.', ending='')
                self.stdout.flush()
                time.sleep(1)
            
            self.stdout.write(self.style.SUCCESS('\nタスクが完了しました。'))
            
            # get(propagate=False)でタスク内で発生した例外を再発生させずに結果を取得
            task_results = result.get(propagate=False)

            self.stdout.write("="*50)
            self.stdout.write(self.style.SUCCESS('スクレイピング最終結果:'))
            
            for res in task_results:
                # タスクが正常に値を返せなかった場合 (例: ワーカーがクラッシュ)
                if isinstance(res, Exception):
                    self.stdout.write(self.style.ERROR(f'  [CRITICAL] タスク実行中に予期せぬエラーが発生しました: {res}'))
                    continue

                # タスクが正常に値を返した場合 (辞書)
                platform = res.get('platform', '不明なプラットフォーム')
                if res.get('status') == 'success':
                    self.stdout.write(self.style.SUCCESS(f'  [OK] {platform}'))
                else:
                    error_msg = res.get('error', '詳細不明のエラーです。')
                    self.stdout.write(self.style.ERROR(f'  [NG] {platform}'))
                    # エラー内容を表示
                    self.stdout.write(self.style.ERROR(f'     └─ エラー内容: {error_msg}'))

            self.stdout.write("="*50)

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'\nタスクの実行監視中にエラーが発生しました: {e}'))