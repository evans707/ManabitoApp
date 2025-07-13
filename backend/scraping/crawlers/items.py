import scrapy

class AssignmentItem(scrapy.Item):
    # DjangoのAssignmentモデルと対応するフィールドを定義
    # 加えて、処理に必要な中間データも定義する
    user_pk = scrapy.Field()
    course_name = scrapy.Field()
    
    title = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    start_date = scrapy.Field() 
    due_date = scrapy.Field()
    is_submitted = scrapy.Field()
    platform = scrapy.Field()        # 'moodle' や 'webclass' などを識別