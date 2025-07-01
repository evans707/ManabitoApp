import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ScrapingStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        # ユーザーごとに一意なグループ名を作成し、そのグループに参加
        self.group_name = f'scraping_status_user_{self.user.pk}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # グループから退出
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    # Celeryタスクから呼び出されるメソッド
    async def scraping_update(self, event):
        message = event['message']
        # WebSocket経由でクライアントにメッセージを送信
        await self.send(text_data=json.dumps({
            'message': message
        }))