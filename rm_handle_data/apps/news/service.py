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
from nltk.tokenize import RegexpTokenizer


class ThreadServiceGetNews(threading.Thread):
    def __init__(self, thread_type):
        super(ThreadServiceGetNews, self).__init__()
        self.thread_type = thread_type
        
    def run(self):
        try: 
            # Injection require object
            common = Common()
            news_query = NewsQuery()
            cursor = connection.cursor()
            key_work_handle = KeywordHandler()
            tokenizer = RegexpTokenizer(r'[^.?!]+')
    
            # Get news data
            cursor.execute(news_query.get_all_news())
            news = common.dictfetchall(cursor)
    
            for new in news:
                news_title = new['title']
                news_content = new['content'] 
                
                # Phân tách nội dung bài tin tức ra các câu nhỏ
                title_sentences = list(map(str.strip, tokenizer.tokenize(news_title)))
                content_sentences = list(map(str.strip, tokenizer.tokenize(news_content)))
                
                # Đánh trọng số cho title
                for title_sentence in title_sentences:
                    if not title_sentence:
                        break
                    item = key_work_handle.cal_sentence_weight(title_sentence)
                    sentence = item['sentence']
                    key_works = item['keywords']
                    sentence_weight = item['sentence_weight']
                    
                    coin_affect = "ALL"
                    if "weights" in key_works:
                        weights = key_works['weights']
                        if "coin" in weights:
                            coins = weights['coin']
                            if len(coins) > 0:
                                coin_affect_temp = ""
                                for coin in coins:
                                    # Xử lý để chỉ lấy coin theo bảng coins
                                    coin_affect_temp += "" # TODO
                                    
                                if coin_affect_temp:
                                    coin_affect = coin_affect_temp

                    if sentence_weight != 0:
                        # Lưu DB
                        cursor.execute(news_query.insert_news_sentences_weight(), [new['id'],
                            sentence, str(key_works), new['time'], sentence_weight, True, coin_affect])

                # Đánh trọng số cho content
                for content_sentence in content_sentences:
                    if not content_sentence:
                        break
                    item = key_work_handle.cal_sentence_weight(content_sentence)
                    sentence = item['sentence']
                    key_works = item['keywords']
                    sentence_weight = item['sentence_weight']

                    coin_affect = "ALL"
                    if "weights" in key_works:
                        weights = key_works['weights']
                        if "coin" in weights:
                            coins = weights['coin']
                            if len(coins) > 0:
                                coin_affect_temp = ""
                                for coin in coins:
                                    # Xử lý để chỉ lấy coin theo bảng coins
                                    coin_affect_temp += ""  # TODO

                                if coin_affect_temp:
                                    coin_affect = coin_affect_temp

                    if sentence_weight != 0:
                        # Lưu DB
                        cursor.execute(news_query.insert_news_sentences_weight(), [new['id'],
                            sentence, str(key_works), new['time'], sentence_weight, False, coin_affect])
                            
        except Exception as e:
            print(e)


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

