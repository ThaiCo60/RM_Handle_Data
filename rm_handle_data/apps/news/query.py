"""
Definition of news query.
"""


class NewsQuery:

    def get_all_news(self):
        """
        Get all news on DB
        :return:
        """
        result = """
            select t.id, t.title, t.meta_description, t.content, t.post_id, time 
            from news t 
            where t.id not in (select news_id from news_sentences_weight )
            order by t.`time` 
        """
        return result
    
    def insert_news_sentences_weight(self):
        """
        Insert news
        :return:
        """
        result = """
            insert into news_sentences_weight (news_id, sentence_content, key_words, time, weight, is_title) 
            values (%s, %s, %s, %s, %s, %s) 
        """
        return result
