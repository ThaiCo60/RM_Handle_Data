"""
Definition of common function.
"""
from rm_handle_data.const import Const


class Common:

    def dictfetchall(self, cursor):
        "Returns all rows from a cursor as a dict"
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]

    def handle_created_at(self, created_at):
        """
        Handle giá trị created_at
        :return: 
        """
        created_at = str(created_at)
        items = created_at.split(" ")
        if len(items) == 2:
            hms = str(items[1]).split(":")
            if len(hms) == 3:
                hour = hms[0]
                minute = hms[1]
                
                if int(minute) > 0:
                    hour = int(hour) + 1
                    if hour == 24:
                        hour = 23
                    hour = str(hour).zfill(2)
                    
                return items[0] + " " + hour + ":00:00"
        
        return created_at
    
    def check_key_word_for_big_cap(self, weight, new_title, new_content):
        """
        Check key word 
        :return: 
        """
        result = weight
        if "tăng" in new_title or "giảm" in new_title \
                or "tăng" in new_content or "giảm" in new_content:
            result += 0.1

        if "lên sàn" in new_title or "lên sàn" in new_content:
            result += 0.2

        if "đầu tư" in new_title or "đầu tư" in new_content:
            result += 0.1
            
        if "bán" in new_title or "mua" in new_title \
                or "bán" in new_content or "mua" in new_content:
            result += 0.1
            
        return result

    def check_key_word_for_defi(self, weight, new_title, new_content):
        """
        Check key word 
        :return: 
        """
        result = weight

        if "lỗi" in new_title or "lỗi" in new_content:
            result += 0.1

        if "hack" in new_title or "hack" in new_content:
            result += 0.1
            
        if "tấn công" in new_title or "tấn công" in new_content:
            result += 0.1
            
        if "đóng cửa" in new_title or "đóng cửa" in new_content:
            result += 0.2

        return result
    
    def check_key_word_for_nft(self, weight, new_title, new_content):
        """
        Check key word 
        :return: 
        """
        result = weight
        if "tăng" in new_title or "giảm" in new_title \
                or "tăng" in new_content or "giảm" in new_content:
            result += 0.1

        if "giao dịch" in new_title or "giao dịch" in new_content:
            result += 0.1

        if "đầu tư" in new_title or "đầu tư" in new_content:
            result += 0.1
            
        if "hack" in new_title or "hack" in new_content:
            result += 0.1

        return result
    
    def check_key_word_for_juridical(self, weight, new_title, new_content):
        """
        Check key word 
        :return: 
        """
        result = weight

        if "cấp phép" in new_title or "cấp phép" in new_content \
                or "cho phép" in new_content or "cho phép" in new_content:
            result += 0.2
            
        if "thông qua" in new_title or "thông qua" in new_content \
                or "công nhận" in new_content or "công nhận" in new_content:
            result += 0.2

        if "cấm" in new_title or "cấm" in new_content:
            result += 0.2

        return result
    
    def check_key_word_for_synthetic(self, weight, new_title, new_content):
        """
        Check key word 
        :return: 
        """
        result = weight
        if "tăng" in new_title or "giảm" in new_title \
                or "tăng" in new_content or "giảm" in new_content:
            result += 0.1

        if "đánh cắp" in new_title or "đánh cắp" in new_content:
            result += 0.2

        if "đầu tư" in new_title or "đầu tư" in new_content:
            result += 0.2
            
        if "mua lại" in new_title or "mua lại" in new_content:
            result += 0.1
            
        if "đóng cửa" in new_title or "đóng cửa" in new_content:
            result += 0.2
            
        if "tấn công" in new_title or "tấn công" in new_content:
            result += 0.1

        return result

    def get_news_weight(self, source, new):
        """
        Đánh trọng số cho bài đăng
        :param source: 
        :param new: 
        :return: 
        """
        weight = 0
        new_title = new['title']
        new_content = new['meta_description']
        
        # Check theo category
        source_code = source['code']
        if Const.CATEGORY_CODE_BIG_CAP in source_code:
            weight = 0.3
            # Check theo từ khoá
            weight = self.check_key_word_for_big_cap(weight, new_title, new_content)
                
        if Const.CATEGORY_CODE_DEFI in source_code:
            weight = 0.2
            # Check theo từ khoá
            weight = self.check_key_word_for_defi(weight, new_title, new_content)
        if Const.CATEGORY_CODE_NFT_GAMEFI in source_code:
            weight = 0.1
            # Check theo từ khoá
            weight = self.check_key_word_for_nft(weight, new_title, new_content)
        if Const.CATEGORY_CODE_JURIDICAL in source_code:
            weight = 0.5
            # Check theo từ khoá
            weight = self.check_key_word_for_juridical(weight, new_title, new_content)
        if Const.CATEGORY_CODE_SYNTHETIC in source_code:
            weight = 0.3
            # Check theo từ khoá
            weight = self.check_key_word_for_synthetic(weight, new_title, new_content)
            
        if weight > 1:
            weight = 1
            
        return weight
