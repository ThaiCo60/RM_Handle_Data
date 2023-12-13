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

    def remove_duplicate_coin_code(self, codes):
        """
        Handle giá trị created_at
        :return: 
        """
        result = ""
        if codes and len(codes) > 0:
            new_codes = list(dict.fromkeys(codes))
            for code in new_codes:
                result += code + ","
        if result:
            result = result[:-1]
        return result
