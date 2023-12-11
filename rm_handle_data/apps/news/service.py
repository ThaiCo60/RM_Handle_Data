"""
Definition of news service.
"""
from rm_handle_data.apps.common.common import Common
from rm_handle_data.apps.common.keyword import KeywordHandler
from rm_handle_data.apps.common.response import Response
from django.db import connection
from rest_framework import status
from rm_handle_data.apps.news.query import NewsQuery
from rm_handle_data.message import Message
import threading


class ThreadServiceGetNews(threading.Thread):
    def __init__(self, thread_type):
        super(ThreadServiceGetNews, self).__init__()
        self.thread_type = thread_type
        
    def run(self):
        # Injection require object
        common = Common()
        news_query = NewsQuery()
        cursor = connection.cursor()

        # Get news data
        cursor.execute(news_query.get_all_news())
        news = common.dictfetchall(cursor)

        for new in news:
            news_title = ""
            news_contents = ""
            
            # Phân tách nội dung bài tin tức ra các câu nhỏ
            centences = [] 
            
            # Đánh trọng số cho từng câu
            
            # Insert DB 


class NewsService:

    def handle_data_news_past(self):
        """
        Handle data news in the past
        :return:
        """
        try:
            inline_thread = ThreadServiceGetNews("past") 
            inline_thread.start()

            response = Response(data=None, mess=Message.SUCCESS, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    def handle_data_news_daily(self):
        """
        Handle data news in the past
        :return:
        """
        try:
            inline_thread = ThreadServiceGetNews("daily")
            inline_thread.start()

            response = Response(data=None, mess=Message.SUCCESS, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response   

    def test_sentence_weight(self, args):
        """
        Test chức năng đánh trọng số câu
        :return:
        """
        sentence = (
            "Bitcoin tăng giá mạnh khiến các trader bán ra rất mạnh từ cơn sốt meme coin hồi tháng 5/2023, nhờ vào sự chuyển mình của làn sóng Bitcoin Ordinals và BRC-20."
        )
        content = args.get("content", sentence)
        keywordHandler = KeywordHandler()
        sentence_weight = keywordHandler.cal_text_weight(content)
     
        response = Response(data=sentence_weight, mess="OK", status=status.HTTP_200_OK)

        return response

