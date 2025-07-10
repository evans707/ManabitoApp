from celery import shared_task, group
import logging
from accounts.models import User
from .services import scrape_moodle, scrape_webclass
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

def send_status_update(user_pk, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'scraping_status_user_{user_pk}',
        {
            'type': 'scraping.update',
            'message': message
        }
    )


@shared_task
def scrape_webclass_task(user_pk, password):
    """WebClassのスクレイピングを単体で実行し、完了を通知するタスク"""
    user = User.objects.get(pk=user_pk)
    try:
        scrape_webclass(user, password)
        send_status_update(user_pk, 'WebClassの課題取得が完了しました。')
        return {'status': 'success', 'platform': 'WebClass'} 
    except Exception as e:
        logger.error(f"WebClassスクレイピング中にエラー: {e}", exc_info=True)
        send_status_update(user_pk, 'WebClassの課題取得中にエラーが発生しました。')
        return {'status': 'failure', 'platform': 'WebClass', 'error': str(e)}


@shared_task
def scrape_moodle_task(user_pk, password):
    """Moodleのスクレイピングを単体で実行し、完了を通知するタスク"""
    user = User.objects.get(pk=user_pk)
    try:
        scrape_moodle(user, password)
        send_status_update(user_pk, 'Moodleの課題取得が完了しました。')
        return {'status': 'success', 'platform': 'Moodle'}
    except Exception as e:
        logger.error(f"Moodleスクレイピング中にエラー: {e}", exc_info=True)
        send_status_update(user_pk, 'Moodleの課題取得中にエラーが発生しました。')
        return {'status': 'failure', 'platform': 'Moodle', 'error': str(e)}


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