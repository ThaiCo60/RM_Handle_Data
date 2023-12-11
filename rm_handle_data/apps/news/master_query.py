"""
Definition of news query.
"""


class MasterQuery:

    def __init__(self):    
        self.tables = {
            "negate" : "master_negate",
            "booster" : "master_booster_weight",
            "action" : "master_action_weight",
            "subject" : "master_subject_weight",
            "keyword" : "master_keyword_weight",
            "trend" : "master_trend_weight",
            "market_place" : "master_market_place_weight",
            "area" : "master_area_weight",
            "coin" : "master_coin_weight",
        }

    def select_all(self, table_name):
        return f"SELECT * FROM {self.tables[table_name]}"