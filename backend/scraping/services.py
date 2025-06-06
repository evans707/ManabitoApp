import os
import logging
from dotenv import load_dotenv
from .scraper_moodle import MoodleScraper
from .models import Assignment
from accounts.models import User

load_dotenv()
logger = logging.getLogger(__name__)

def scrape_moodle(user: User, password: str):
    """
    指定されたユーザーの課題をスクレイピングし、DBに保存する。
    成功した場合は (保存件数, 更新件数) のタプルを返す。
    失敗した場合は例外を発生させる。
    """
    moodle_username = user.university_id
    moodle_url = os.getenv('MOODLE_LOGIN_URL')

    logger.info(f"ユーザー'{moodle_username}'のスクレイピング処理を開始します。")

    if not moodle_url:
        logger.error("環境変数 MOODLE_LOGIN_URL が設定されていません。")
        raise ValueError("MoodleのURLが設定されていません。")

    saved_count = 0
    updated_count = 0

    try:
        with MoodleScraper(moodle_username, password, moodle_url, logger) as scraper:
            # ログイン処理
            if not scraper.login():
                logger.warning(f"ユーザー'{moodle_username}'のMoodleへのログインに失敗しました。")
                raise ConnectionError("Moodleへのログインに失敗しました。ユーザー名またはパスワードが間違っている可能性があります。")
            logger.info(f"ユーザー'{moodle_username}'のログイン成功。課題の取得を開始します。")

            # 課題データの取得
            assignments_data = scraper.scrape_all_assignments()
            if not assignments_data:
                logger.warning(f"ユーザー'{moodle_username}'の課題をスクレイピングしましたが、取得結果は0件でした。")

            # データベースに保存
            for item in assignments_data:
                due_date_aware = item.get('due_date')
                
                obj, created = Assignment.objects.update_or_create(
                    user=user,
                    url=item['url'],
                    defaults={
                        'title': item['title'],
                        'due_date': due_date_aware,
                    }
                )
                if created:
                    saved_count += 1
                else:
                    updated_count += 1
        
        logger.info(f"ユーザー'{moodle_username}'の処理完了: {saved_count}件の新規保存、{updated_count}件の更新。")
        return (saved_count, updated_count)
    
    except Exception as e:
        # 予期せぬ例外が発生した場合、詳細をログに出力
        logger.error(f"ユーザー'{moodle_username}'のスクレイピング中に予期せぬエラーが発生しました。", exc_info=True)
        # エラーを再度発生させ、呼び出し元のビューに処理の失敗を伝える
        raise e