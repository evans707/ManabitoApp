from celery import shared_task, group
import logging
from accounts.models import User
from .services import scrape_moodle, scrape_webclass

logger = logging.getLogger(__name__)


@shared_task
def run_all_scrapes_task(user_pk, password):
    """MoodleとWebClassのスクレイピングタスクを並列で実行する親タスク"""
    logger.info(f"並列スクレイピングタスクを開始します for user_pk={user_pk}")

    # 並列実行したいタスクのリストを、groupを使って作成します。
    # .s() は「シグネチャ」を作成するメソッドで、タスクの呼び出しと引数を定義します。
    tasks_to_run = group([
        scrape_webclass_task.s(user_pk, password),
        scrape_moodle_task.s(user_pk, password)
    ])

    # groupを実行します。これにより、2つのタスクが同時にワーカーに送られます。
    tasks_to_run.apply_async()

    logger.info(f"並列スクレイピングタスクをキューに登録しました for user_pk={user_pk}")


@shared_task
def scrape_webclass_task(user_pk, password):
    """WebClassのスクレイピングを単体で実行するタスク"""
    try:
        user = User.objects.get(pk=user_pk)
        logger.info(f"WebClassスクレイピングタスク開始 for {user.university_id}")
        scrape_webclass(user, password)
        logger.info(f"WebClassスクレイピングタスク完了 for {user.university_id}")
    except User.DoesNotExist:
        logger.error(f"タスク実行エラー: User with pk={user_pk} が見つかりません。")
    except Exception as e:
        logger.error(f"WebClassスクレイピング中に予期せぬエラー: {e}", exc_info=True)


@shared_task
def scrape_moodle_task(user_pk, password):
    """Moodleのスクレイピングを単体で実行するタスク"""
    try:
        user = User.objects.get(pk=user_pk)
        logger.info(f"Moodleスクレイピングタスク開始 for {user.university_id}")
        scrape_moodle(user, password)
        logger.info(f"Moodleスクレイピングタスク完了 for {user.university_id}")
    except User.DoesNotExist:
        logger.error(f"タスク実行エラー: User with pk={user_pk} が見つかりません。")
    except Exception as e:
        logger.error(f"Moodleスクレイピング中に予期せぬエラー: {e}", exc_info=True)