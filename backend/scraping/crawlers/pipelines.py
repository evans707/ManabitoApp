from itemadapter import ItemAdapter
from scraping.models import Assignment, Course
from accounts.models import User

class DjangoPipeline:

    async def process_item(self, item, spider):
        """
        Spiderから渡されたItemを、一件ずつ非同期でDBに保存する。
        """
        adapter = ItemAdapter(item)
        
        try:
            # Djangoの非同期ORMメソッドを使用してDB操作を行う
            user = await User.objects.aget(pk=adapter.get('user_pk'))
            
            course, _ = await Course.objects.aget_or_create(
                user=user,
                title=adapter.get('course_name'),
                defaults={'day_of_week': None, 'period': None}
            )

            await Assignment.objects.aupdate_or_create(
                user=user,
                url=adapter.get('url'),
                defaults={
                    'course': course,
                    'title': adapter.get('title'),
                    'content': adapter.get('content', ''),
                    'due_date': adapter.get('due_date'),
                    'start_date': adapter.get('start_date'),
                    'is_submitted': adapter.get('is_submitted', False),
                    'platform': adapter.get('platform'),
                }
            )
            
            spider.logger.info(f"DB保存成功: {adapter.get('title')}")

        except User.DoesNotExist:
            spider.logger.error(f"Pipeline Error: User with pk={adapter.get('user_pk')} not found.")
        except Exception as e:
            spider.logger.error(f"Pipeline Error for item '{adapter.get('title')}': {e}", exc_info=True)
            
        return item