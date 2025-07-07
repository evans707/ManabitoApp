# Scrapy settings for crawlers project


# --- Django Integration Settings ---
import os
import sys
import django

# このファイルから manage.py がある階層までのパスを指定します
# (scraping/crawlers/crawlers/settings.py -> backend/)
django_project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(django_project_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()
# --- End of Django Integration Settings ---

# --- Playwright Settings ---
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"


BOT_NAME = "crawlers"

SPIDER_MODULES = ["scraping.crawlers.spiders"]
NEWSPIDER_MODULE = "scraping.crawlers.spiders"

ADDONS = {}

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

ITEM_PIPELINES = {
   "scraping.crawlers.pipelines.DjangoPipeline": 300,
}

LOG_LEVEL = 'INFO'

# # Scrapyが同時に処理するリクエストの最大数
# CONCURRENT_REQUESTS = 4

# # Playwrightが同時に開くページの最大数
# PLAYWRIGHT_MAX_CONTEXTS = 2
# PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 2