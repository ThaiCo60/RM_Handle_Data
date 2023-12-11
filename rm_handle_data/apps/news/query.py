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
            select t.id, t.title, t.meta_description, t.content, t.post_id 
            from news t 
            where t.id not in (select new_id from news_sentences_weight )
            order by t.`time` 
        """
        return result
    
    def insert_news(self):
        """
        Insert news
        :return:
        """
        result = """
            insert into news (source_id, category_id, title, meta_description, content, url, 
            time, post_id) 
            values (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE category_id=%s, title=%s, meta_description=%s, content=%s, 
            url=%s, time=%s
        """
        return result
