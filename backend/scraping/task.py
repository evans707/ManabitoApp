from celery import shared_task
import logging
from accounts.models import User
from .services import scrape_moodle, scrape_webclass

logger = logging.getLogger(__name__)


@shared_task
def run_all_scrapes_task(user_pk, password):
    """MoodleとWebClassの両方のスクレイピングを実行するタスク"""
    try:
        user = User.objects.get(pk=user_pk)

        logger.info(f"バックグラウンドタスク開始: 全スクレイピング for {user.university_id}")

        try:
            scrape_webclass(user, password)
            logger.info(f"WebClassスクレイピング完了 for {user.university_id}")
        except Exception as e:
            logger.error(f"WebClassスクレイピングタスク中にエラー: {e}", exc_info=True)

        try:
            scrape_moodle(user, password)
            logger.info(f"Moodleスクレイピング完了 for {user.university_id}")
        except Exception as e:
            logger.error(f"Moodleスクレイピングタスク中にエラー: {e}", exc_info=True)

        logger.info(f"バックグラウンドタスク完了: 全スクレイピング for {user.university_id}")

    except User.DoesNotExist:
        logger.error(f"タスク実行エラー: User with pk={user_pk} が見つかりません。")