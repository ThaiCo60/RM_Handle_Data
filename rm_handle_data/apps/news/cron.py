from rm_handle_data.apps.news.service import NewsService


def handle_news_data_daily():
    news_service = NewsService()
    news_service.handle_data_news_past()
