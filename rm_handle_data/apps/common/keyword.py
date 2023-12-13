from django.db import connection
from rm_handle_data.apps.news.master_query import MasterQuery

SENTENCE = "sentence"
NEGATE = "negate"
IS_NEGATE = "is_negate"
NEGATE_WEIGHT = "negate_weight"
NEGATE_BY = "negate_by"
FULL_NEGATE_BY = "full_negate_by"
AFTER_NEGATE = "after_negate"
BEFORE_NEGATE = "before_negate"
WEIGHT = "weight"
SENTENCE_WEIGHT = "sentence_weight"
SENTENCE_POSITIVE_WEIGHT = "positive_weight"
SENTENCE_NEGATE_WEIGHT = "negative_weight"
WEIGHTS = "weights"
TARGET_SENTENCE = "target_sentence"
KEYWORD = "keyword"
KEYWORDS = "keywords"
NAME = "name"
NICK_NAME = "nick_name"
CODE = "code"
FULL_NAME = "full_name"
BOOSTER = "booster"
ACTION = "action"
TREND = "trend"
SUBJECT = "subject"
MARKET_PLACE = "market_place"
COIN = "coin"
AREA = "area"
BEFORE_PHRASE = "before_phrase"
AFTER_PHRASE = "after_phrase"
ID = "id"
INDEX = "index"
END_INDEX = "end_index"
INDEXS = "indexs"
IS_UP_TREND = "is_up_trend"
UP_TREND_WEIGHT = "up_trend_weight"
UP_TREND_NEGATE_WEIGHT = "up_trend_negate_weight"
DOWN_TREND_WEIGHT = "down_trend_weight"
DOWN_TREND_NEGATE_WEIGHT = "down_trend_negate_weight"
MASTER = "master"
APPLY_TREND = "apply_trend"
RESET_BY = "reset_by"
BEFORE_BOOSTER = "before_booster"
BEFORE_BOOSTER_COUNT = "before_booster_count"

AFFECTED_BY_TREND = "affected_by_trend"
AFFECTED_BY_SUBJECT = "affected_by_subject"
AFFECTED_BY_ACTION = "affected_by_action"
AFFECTED_BY_BOOSTER = "affected_by_booster"
AFFECTED_BY_AREA= "affected_by_area"
AFFECTED_BY_MARKET_PLACE= "affected_by_market_place"
TOTAL_WEIGHT = "total_weight"


class KeywordHandler:
    """
    Xử lý từ khóa cho câu
    booster_dict: bộ từ điển định nghĩa cường độ
    action_dict: bộ từ điển các hành động liên quan đến từ khóa
    keyword_dict: bộ từ khóa
    """
    def __init__(self, **args):
        self.master_query = MasterQuery()

        # Muc do tac dong cua tu khoa
        self.booster_dict = args.get("booster_dict", self.get_master_data(self.master_query.select_all(BOOSTER)))

        # Hanh dong thuc hien
        self.action_dict = args.get("action_dict", self.get_master_data(self.master_query.select_all(ACTION)))

        # Tu khoa
        self.keyword_dict = args.get("keyword_dict", self.get_master_data(self.master_query.select_all(KEYWORD)))

        # Xu huong: tang, giam, ... 
        self.trend_dict = args.get("trend_dict", self.get_master_data(self.master_query.select_all(TREND)))

        # Doi tuong: vis du: coi masster db 
        self.subject_dict = args.get("subject_dict", self.get_master_data(self.master_query.select_all(SUBJECT)))

        # San 
        self.market_place_dict = args.get("market_place_dict", self.get_master_data(self.master_query.select_all(MARKET_PLACE)))

        # Khu vuc
        self.area_dict = args.get("area_dict", self.get_master_data(self.master_query.select_all(AREA)))

        # Coins
        self.coin_dict = args.get("coin_dict", self.get_master_data(self.master_query.select_all(COIN)))

        # Tap tu khoa phu? dinhj
        negate_dict = args.get("negate_dict")
        if negate_dict is None:
            negate_dict = self.get_master_data(self.master_query.select_all("negate")).keys()
            self.negate_dict = negate_dict

    @staticmethod
    def get_master_data(query):
        """
        Lấy tất cả data từ table master
        """
        cursor = connection.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        _dict = {}
        for item in data:
            _dict[item[NAME]] = item
        return _dict
    
    def get_keywords_group(self, text, dict):
        matchers = {}
        for keyword, keyword_property in dict.items():
            append_item = None
            if keyword in text:
                append_item = {
                    "code" : keyword_property.get(CODE, None),
                    "equal_mode" : NAME,
                    "parent_name" : keyword,
                    NAME : keyword,
                    WEIGHT : keyword_property[WEIGHT]
                }
                matchers[keyword]  = append_item
            else:
                nick_names = keyword_property.get(NICK_NAME, "").lower().split(",")
                for nick_name in nick_names:
                    if nick_name in text:
                        append_item = {
                            "code" : keyword_property.get(CODE, None),
                            "equal_mode" : NICK_NAME,
                            "parent_name" : keyword,
                            NAME : nick_name,
                            WEIGHT : keyword_property[WEIGHT]
                        }
                        matchers[nick_name]  = append_item

        return matchers

    def get_keywords_by(self, text, dict):
        """
        Lấy tất cả từ khóa trong câu dựa vào tập dict
        dict: Tập dữ liệu nguồn
        text: văn bản cần xử lý
        """
        matchers = []
        for keyword, keyword_property in dict.items():
            matchers += self.get_keywords_from_sentence(text, keyword, keyword_property)
        return matchers
    
    def get_action_keywords(self, text, keyword):
        """
        Lấy tất cả từ khóa trong dict<action>
        """
        return self.get_keywords_by(text, self.action_dict)
    
    def get_subject_keywords(self, text):
        """
        Lấy tất cả từ khóa trong dict<subject>
        """
        return self.get_keywords_by(text, self.subject_dict)
    
    def get_trend_keywords(self, text):
        """
        Lấy tất cả từ khóa trong dict<trend>
        """
        return self.get_keywords_by(text, self.trend_dict)
    
    def get_booster_keywords(self, text):
        """
        Lấy tất cả từ khóa trong dict<booster>
        """
        boosters = self.get_keywords_by(text, self.booster_dict)
        choose_boosters = []
        for booster in boosters:
            first_index = booster[TARGET_SENTENCE].find(booster[NAME])
            before_booster = booster[TARGET_SENTENCE][:first_index].strip()
            before_booster_words = before_booster.split()
            booster[BEFORE_BOOSTER] = before_booster
            booster[BEFORE_BOOSTER_COUNT] = len(before_booster_words)
            ## chỉ cho phép tối đa 2 từ được chen vào trước booster
            max_allow_word = 2
            if booster[BEFORE_BOOSTER_COUNT] < max_allow_word:
               choose_boosters.append(booster) 

        return choose_boosters

    def get_keyword_keywords(self, text):
        """
        Lấy tất cả từ khóa trong dict<keyword>
        """
        res = self.get_keywords_by(text, self.keyword_dict)
        filtered_data = [item for item in res if not any(set(item[INDEXS]).issubset(set(other_item[INDEXS])) for other_item in res if item != other_item)]
        filtered_data = self.merge_linear_keywords(filtered_data)
        return filtered_data
    
    def get_coin_keywords(self, text):
        """
        Lấy tất cả từ khóa trong dict<coin>
        """
        dict = self.get_keywords_group(text, self.coin_dict)
        result = self.get_keywords_by(text, dict)
        if len(result) > 0:
            aa = result
        return result
    
    def get_area_keywords(self, text):
        """
        Lấy tất cả từ khóa trong dict<area>
        """
        dict = self.get_keywords_group(text, self.area_dict)
        return self.get_keywords_by(text, dict)
    
    def get_market_place_keywords(self, text):
        """
        Lấy tất cả từ khóa trong dict<market_place>
        """
        dict = self.get_keywords_group(text, self.market_place_dict)
        return self.get_keywords_by(text, dict)
    
    def trim_end_sentence_symbols(self, source):
        """Loại bỏ dấu kết thúc câu (,.,?,..)"""
        punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~“”"""
        return source.rstrip(punctuation)
    
    def remove_all_special_chars(self, source):
        """Loại bỏ các kí tự đặc biệt"""
        text = source
        characters_to_remove = ['“', '”', ',']
        for char in characters_to_remove:
            text = text.replace(char, '')
        return text  

    def copy_properties(self, target, dict, keys = None):
        """
        Sao chép thuộc tính của <dict> qua <target>
        """
        if target is None:
            target = {}
        _keys = keys if keys is not None else dict.keys()
        exclude_keys = [ID, INDEXS]
        for key in _keys:
            if key not in exclude_keys:
                target[key] = dict.get(key, None)

    def get_keywords_from_sentence(self, text, target_keyword, target_keyword_property):
        """
        lấy tất cả vị trí xuất hiện của từ khóa <target_keyword> trong chuỗi <text>
        Thông tin bao gồm:
            - index: vị trí xuất hiện,
            - keyword: từ khóa,
            - is_negate : từ khóa tại vị trí xuất hiện ở thể phủ định hay không
        :return dict    
        """
        _text = self.remove_all_special_chars(text.lower())
        words = _text.split()
        target_keyword_lower = target_keyword.lower()
        matchers = []
        phrase = ""
        start_index = None
        indexs = []
        word_len = len(words)
        for i in range(word_len):
            if words[i] in target_keyword_lower:
                if phrase == "":
                    if start_index is None:
                        start_index = i
                    phrase += words[i]
                else:
                    phrase += " " + words[i]    
                indexs.append(i)
                if phrase == target_keyword_lower:
                    after_phrase = ""
                    before_phrase = ""
                    if start_index > 0:
                        before_phrase = " ".join(words[:start_index])
                    if i < word_len:
                        after_phrase = " ".join(words[i+1:])

                    keyword_matching = {
                        INDEX: start_index,
                        END_INDEX: i,
                        INDEXS : indexs,
                        TARGET_SENTENCE : text,
                        BEFORE_PHRASE : before_phrase,
                        AFTER_PHRASE : after_phrase
                    }
                    self.copy_properties(keyword_matching, target_keyword_property)
                    negate = self.check_negate(before_phrase)
                    self.copy_properties(keyword_matching, negate, [IS_NEGATE, NEGATE_BY, AFTER_NEGATE, FULL_NEGATE_BY])
                    keyword_matching[NEGATE_WEIGHT] = target_keyword_property.get(NEGATE_WEIGHT, None)
                        
                    matchers.append(keyword_matching)
                    phrase = ""
                    start_index = None
                    indexs = []
            else:
                start_index = None
                phrase = "" 
                indexs = []
        matchers = self.merge_linear_keywords(matchers)                  
        return matchers
    
    def words_tokenize(self, sentence):
        """
        Lấy danh sách "từ" trong câu
        """
        _sentence = self.remove_all_special_chars(sentence)
        words = _sentence.split()
        result = []
        for word in words:
            word = word.strip(".,?!")
            if len(word) > 0:
               result.append(word) 

        return result
    
    def count_words(self, text):
        return len(self.words_tokenize(text))

    def split_text_into_sentences(self, text):
        """
        Lấy danh sách câu trong văn bản dựa vào dấu câu (.)
        """
        end_sentence_chars = ["."]
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in end_sentence_chars:
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        if current_sentence:
            sentences.append(current_sentence.strip())
        
        return sentences

    def check_conflict_negate(self, text):
        """Kiểm tra xung đột phủ định(phủ định của phủ định)"""
        for sub_negate in self.negate_dict:
            if sub_negate in text:
                return True
        return False    

    def check_negate(self, text):
        """
        Xác định vị trí xuất hiện của từ khóa trong câu ở thể phủ định hay không
        :return boolean
        """
        negates = []
        for negate in self.negate_dict:
            if negate in text:
                last_index = text.rfind(negate)
                index = last_index + len(negate)
                after_negate = ""
                before_negate = ""
                is_conflict_after = False
                is_conflict_before = False
                after_negate_word_count = 0 
                before_negate_word_count = 0 
                if last_index > 0:
                    before_negate = text[: last_index].strip()
                    before_negate_word_count = self.count_words(before_negate)
                if index < len(text):
                    after_negate = text[index:].strip()
                    after_negate_word_count = self.count_words(after_negate)
                
                # Xử lý phủ định của phủ định đối với vế trước của từ khóa phủ định
                if before_negate_word_count > 0:  
                    is_conflict_before = self.check_conflict_negate(before_negate) 

                # Xử lý phủ định của phủ định đối với vế sau của từ khóa phủ định
                if after_negate_word_count > 0:
                    is_conflict_after = self.check_conflict_negate(after_negate)

                # chỉ có phép tối đa 3 từ chen vào giữa từ phủ định và từ khóa
                if is_conflict_after == False and is_conflict_before == False and after_negate_word_count <= 3:
                    negates.append({
                        NEGATE_BY: negate,
                        "after_negate_word_count" : after_negate_word_count,
                        "before_negate_word_count" : before_negate_word_count,
                        AFTER_NEGATE: after_negate,
                        BEFORE_NEGATE: before_negate
                    }) 

        result = {
            IS_NEGATE : False,
            AFTER_NEGATE: None,
            NEGATE_BY : None,
            FULL_NEGATE_BY : None
        }
        if len(negates) == 0:
            return result
        
        negates = sorted(negates, key=lambda x: x["after_negate_word_count"])
        choose_negates = [
            negates[0]
        ]
        for index, value in enumerate(negates):
            if index > 0 and value["after_negate_word_count"] == choose_negates[0]["after_negate_word_count"]:
               choose_negates.append(value) 

        choose_negates = sorted(choose_negates, key=lambda x: len(x[NEGATE_BY]), reverse=True)

        choose_negates = choose_negates[0]
        result[IS_NEGATE] = True
        result[NEGATE_BY] = choose_negates[NEGATE_BY]
        result[AFTER_NEGATE] = choose_negates[AFTER_NEGATE]
        if result[AFTER_NEGATE] != "":
           result[FULL_NEGATE_BY] = f"{result[NEGATE_BY]} {result[AFTER_NEGATE]}"
        return result
    
    def drop_properties(self, dict, properties):
        """Xóa bớt thuộc tính của từ điển <dict>"""
        clone_dict = dict.copy()
        for property in properties:
            if clone_dict.get(property, None) is not None:
                del clone_dict[property]
        return clone_dict     

    def cal_trend_weight(self, refs, keyword, weights):
        """trọng số của trend"""
        if weights[KEYWORD][MASTER][AFFECTED_BY_TREND] != 1:
            return None
        sentence_trend = keyword[NAME]
        if keyword[BEFORE_PHRASE] != "":
            sentence_trend = f'{keyword[BEFORE_PHRASE]} {sentence_trend}'
        if keyword[AFTER_PHRASE] != "":
            sentence_trend = f'{sentence_trend} {keyword[AFTER_PHRASE]}'
        trend = self.get_trend_keywords(sentence_trend)
    
        if len(trend) > 0 :
            weights[TREND] = {
                MASTER: {},
                WEIGHT : 0,
                IS_NEGATE : False,
            }
            trend = trend[0]
            trend_weight = trend[NEGATE_WEIGHT] if trend[IS_NEGATE] else trend[WEIGHT]
            weights[TREND][TARGET_SENTENCE] = trend[NAME]
            self.copy_properties(weights[TREND][MASTER], trend, [NAME, IS_UP_TREND, WEIGHT, NEGATE_WEIGHT])
            self.copy_properties(weights[TREND], trend, [IS_NEGATE, NEGATE_BY, AFTER_NEGATE, FULL_NEGATE_BY])
            weights[TREND][WEIGHT] = trend_weight     

    def cal_subject_weight(self, refs, keyword, weights):
        """trọng số của subject"""
        if weights[KEYWORD][MASTER][AFFECTED_BY_SUBJECT] != 1:
            return None
        sentence_subject = keyword[NAME]
        if keyword[BEFORE_PHRASE] != "":
            sentence_subject = f'{keyword[BEFORE_PHRASE]} {keyword[NAME]}'
        subjects = self.get_subject_keywords(sentence_subject)
        subject_len = len(subjects)
        if subject_len > 0:
            weights[SUBJECT] = {
                MASTER: {},
                WEIGHT: 0,
                IS_NEGATE: False,
            }
            subject = subjects[0]
            subject_weight = subject[NEGATE_WEIGHT] if subject[IS_NEGATE] else subject[WEIGHT] 
            self.copy_properties(weights[SUBJECT][MASTER], subject, [NAME, WEIGHT, NEGATE_WEIGHT, UP_TREND_WEIGHT, DOWN_TREND_WEIGHT, UP_TREND_NEGATE_WEIGHT, DOWN_TREND_NEGATE_WEIGHT])
            
            if weights[TREND][MASTER] is not None:
                if weights[TREND][MASTER][IS_UP_TREND] == 1:
                    if weights[TREND][IS_NEGATE]:
                        weights[SUBJECT][APPLY_TREND] = "UP_TREND__NEGATE"
                        subject_weight = weights[SUBJECT][MASTER][UP_TREND_NEGATE_WEIGHT]
                    else:
                        weights[SUBJECT][APPLY_TREND] = "UP_TREND"
                        subject_weight = weights[SUBJECT][MASTER][UP_TREND_WEIGHT]
                else:
                    if weights[TREND][IS_NEGATE]:
                        weights[SUBJECT][APPLY_TREND] = "DOWN_TREND__NEGATE"
                        subject_weight = weights[SUBJECT][MASTER][DOWN_TREND_NEGATE_WEIGHT]
                    else:
                        weights[SUBJECT][APPLY_TREND] = "DOWN_TREND"
                        subject_weight = weights[SUBJECT][MASTER][DOWN_TREND_WEIGHT] 
            else:
                weights[SUBJECT][APPLY_TREND] = "NONE"

            weights[SUBJECT][WEIGHT] = subject_weight

    def cal_booster_weight(self, refs, keyword, weights):
        if weights[KEYWORD][MASTER][AFFECTED_BY_SUBJECT] != 1:
            return None
        """trọng số của booster"""
        boosters = self.get_booster_keywords(keyword[AFTER_PHRASE])
        boosters = sorted(boosters, key=lambda x: x[INDEX], reverse=False)
        if len(boosters) > 0:
            weights[BOOSTER] = {
                MASTER: {},
                WEIGHT : 0,
                NAME : "",
                IS_NEGATE : False,
            }
            boosters = boosters[0]
            booster_weight = boosters.get(NEGATE_WEIGHT, 0) if boosters[IS_NEGATE] else boosters.get(WEIGHT, 0)
            self.copy_properties(weights[BOOSTER][MASTER], boosters, [NAME, WEIGHT, NEGATE_WEIGHT])
            self.copy_properties(weights[BOOSTER], boosters, [NAME, IS_NEGATE, NEGATE_BY, BEFORE_BOOSTER, INDEX, END_INDEX, INDEXS])
            weights[BOOSTER][WEIGHT] = booster_weight
    
    def cal_action_weight(self, refs, keyword, weights):
        """trọng số của action"""
        if weights[KEYWORD][MASTER][AFFECTED_BY_ACTION] != 1:
            return None
        actions = self.get_action_keywords(refs.get(SENTENCE, ""), keyword)
        action_len = len(actions)
        if action_len > 0:
            action_weight = 0
            action = actions[0]
            weights[ACTION] = {
                MASTER: {},
                WEIGHT : 0,
                KEYWORDS : [],
                IS_NEGATE : False,
            }
            self.copy_properties(weights[ACTION][MASTER], action, [NAME, WEIGHT, NEGATE_WEIGHT])
            action_weight = action.get(NEGATE_WEIGHT, 0) if action[IS_NEGATE] else action[WEIGHT]
            weights[ACTION][WEIGHT] = action_weight
    
    def cal_coin_weight(self, refs, keyword, weights):
        """trọng số của coin"""
        coins = self.get_coin_keywords(refs.get(SENTENCE, ""))
        if len(coins) > 0:
            weights[COIN] = []
            for coin in coins:
                coin_weight_item = {}
                self.copy_properties(coin_weight_item, coin, [NAME, NICK_NAME, CODE, WEIGHT, IS_NEGATE, NEGATE_BY])
                weights[COIN].append(coin_weight_item)

    def cal_area_weight(self, refs, keyword, weights):
        """trọng số của khu vực"""
        areas = self.get_area_keywords(refs.get(SENTENCE, ""))
        return self.cal_group_mean_weight(areas, weights, AREA)

    def cal_market_place_weight(self, refs, keyword, weights):
        """trọng số của sàn"""
        market_places = self.get_market_place_keywords(refs.get(SENTENCE, ""))
        return self.cal_group_mean_weight(market_places, weights, MARKET_PLACE)

    def cal_group_mean_weight(self, data, weights, ref_dict):
        """trọng số theo giá trị trung bình"""
        if len(data) > 0:
            weights[ref_dict] = {
                "items" : [],
                WEIGHT : 0
            }
            weight = 0
            valid_len = 0
            for data_item in data:
                if data_item.get(IS_NEGATE, False) == False:
                    data_weight_item = {}
                    self.copy_properties(data_weight_item, data_item, [NAME, NICK_NAME, "equal_mode", CODE, WEIGHT, IS_NEGATE, NEGATE_BY])
                    weights[ref_dict]["items"].append(data_weight_item) 
                    weight += data_item[WEIGHT]
                    valid_len += 1
            if valid_len > 0:
                weight = weight / valid_len
                weights[ref_dict][WEIGHT] = weight
                print("")

    def build_keyword_negate(self, keyword, weights, weight_queue):
        """ Kết trọng số từ khóa với tính phủ định """
        weight_queue.append(weights[KEYWORD][WEIGHT])
        if weights[KEYWORD].get(IS_NEGATE, False) == False or weights[KEYWORD].get(NEGATE_BY, "") == "":
            return None
        keyword_negate_append = weights[KEYWORD][NEGATE_BY].strip()
        if weights[KEYWORD].get(AFTER_NEGATE, "") != "":
            keyword_negate_append = f'{keyword_negate_append} {weights[KEYWORD][AFTER_NEGATE]}'.strip()
        keyword[FULL_NAME] = f'{keyword_negate_append} {keyword[FULL_NAME]}'.strip()

    def build_subject_weight(self, keyword, weights, weight_queue):
        """ Kết trọng số từ khóa với <subject> """
        try:
            affected = weights[KEYWORD][MASTER][AFFECTED_BY_SUBJECT] \
                and weights.get(SUBJECT) is not None and weights[SUBJECT][MASTER] is not None \
               and weights[SUBJECT][MASTER][NAME] != weights[KEYWORD][MASTER][NAME]
        
            if affected == False:
                return None
            
            subject_affected_weight = weights[KEYWORD][WEIGHT] * weights[SUBJECT][WEIGHT]
            keyword[AFFECTED_BY_SUBJECT] = f"{subject_affected_weight} ==> keyword_weight({weights[KEYWORD][WEIGHT]}) * subject_weight({weights[SUBJECT][WEIGHT]})"
            weight_queue.append(subject_affected_weight)
        except Exception as e:
            print(e)

    def build_booster_weight(self, keyword, weights, weight_queue):
        """ Kết trọng số từ khóa với <booster> """
        affected = weights[KEYWORD][MASTER][AFFECTED_BY_BOOSTER] == 1 \
            and weights.get(BOOSTER, None) is not None \
            and weights[BOOSTER][NAME] is not None \
            and weights[BOOSTER][NAME] != ""
        
        if affected == False:
            return None
        
        booster_keyword = weights[BOOSTER][NAME]
        if weights[BOOSTER].get(BEFORE_BOOSTER, None) is not None and weights[BOOSTER][BEFORE_BOOSTER] != "":
            booster_keyword = f'{weights[BOOSTER][BEFORE_BOOSTER]} {booster_keyword}'.strip()
        if weights[BOOSTER][IS_NEGATE] == True and weights[BOOSTER][NEGATE_BY] != "":
            booster_keyword = f'{weights[BOOSTER][NEGATE_BY]} {booster_keyword}'.strip()
        booster_affected_weight = weights[KEYWORD][WEIGHT] * weights[BOOSTER][WEIGHT]
        keyword[AFFECTED_BY_BOOSTER] = f"{booster_affected_weight} ==> keyword_weight({weights[KEYWORD][WEIGHT]}) * booster_weight({weights[BOOSTER][WEIGHT]})"
        weight_queue.append(booster_affected_weight)

    def build_trend_weight(self, keyword, weights, weight_queue):
        """ Kết trọng số từ khóa với <trend> """
        affected = weights[KEYWORD][MASTER][AFFECTED_BY_TREND] == 1 \
            and weights[TREND][MASTER] is not None and weights[TREND][MASTER][NAME] != ""
        
        if affected == False:
            return None

        trend_affected_weight = weights[KEYWORD][WEIGHT] * weights[TREND][WEIGHT]
        keyword[AFFECTED_BY_TREND] = f"{trend_affected_weight} ==> keyword_weight({weights[KEYWORD][WEIGHT]}) * trend_weight({weights[TREND][WEIGHT]})"
        weight_queue.append(trend_affected_weight)
    
    def build_area_weight(self, keyword, weights, extra_weight_queue):
        if weights.get(AREA) is None:
            return None
        extra_weight_queue[AREA] = weights['keyword'][WEIGHT]
        keyword[AFFECTED_BY_AREA] = weights['keyword'][WEIGHT]

    def build_market_place_weight(self, keyword, weights, extra_weight_queue):
        if weights.get(MARKET_PLACE) is None:
            return None
        extra_weight_queue[MARKET_PLACE] = weights['keyword'][WEIGHT]
        keyword[AFFECTED_BY_MARKET_PLACE] = weights['keyword'][WEIGHT] 

    def cal_keyword_weight(self, keyword, refs):
        """ Tính toán trọng số của 1 từ khóa """
        weights = {
            KEYWORD: {
                MASTER: {},
                WEIGHT: 0,
                IS_NEGATE: False,
            }
        }

        # Trọng số của từ khóa chính
        keyword_weight = keyword.get(NEGATE_WEIGHT, 0) if keyword[IS_NEGATE] else keyword[WEIGHT]
        weights[KEYWORD][MASTER] = {}
        self.copy_properties(weights[KEYWORD][MASTER], keyword, [NAME, WEIGHT, NEGATE_WEIGHT, AFFECTED_BY_TREND, AFFECTED_BY_SUBJECT, AFFECTED_BY_ACTION, AFFECTED_BY_BOOSTER])
        self.copy_properties(weights[KEYWORD], keyword, [IS_NEGATE, NEGATE_BY, AFTER_NEGATE, BEFORE_PHRASE, AFTER_PHRASE, INDEX, END_INDEX, INDEXS])
        weights[KEYWORD][WEIGHT] = keyword_weight   
        # cals = [
        #    self.cal_action_weight, 
        #    self.cal_trend_weight, 
        #    self.cal_subject_weight, 
        #    self.cal_booster_weight, 
        #    self.cal_coin_weight, 
        #    self.cal_area_weight, 
        #    self.cal_market_place_weight, 
        # ]
        # for cal in cals:
        #     cal(refs, keyword, weights)

        self.cal_action_weight(refs, keyword, weights)
        self.cal_trend_weight(refs, keyword, weights)
        self.cal_subject_weight(refs, keyword, weights)
        self.cal_booster_weight(refs, keyword, weights)
        self.cal_coin_weight(refs, keyword, weights)
        self.cal_area_weight(refs, keyword, weights)
        self.cal_market_place_weight(refs, keyword, weights)
        
        keyword, weights = self.build_keyword_weight(keyword, weights)
        return {
            KEYWORD: keyword,
            WEIGHT: keyword[WEIGHT],
            WEIGHTS: weights
        }
    
    def build_keyword_weight(self, keyword, weights):
        """
        Cập nhật lại từ khóa & tính toán điểm so với các yếu tố phụ thuộc
        """
        keyword = self.drop_properties(keyword, [AFFECTED_BY_TREND, AFFECTED_BY_SUBJECT, AFFECTED_BY_ACTION, AFFECTED_BY_BOOSTER])
        keyword[FULL_NAME] = keyword[NAME]
        del weights[KEYWORD][BEFORE_PHRASE]
        del weights[KEYWORD][AFTER_PHRASE]
        weight_queue = []
        extra_weight_queue = {
            AREA : 0.3,
            MARKET_PLACE : 0.3
        }
        # builds = [
        #     self.build_keyword_negate,
        #     self.build_subject_weight,
        #     self.build_booster_weight,
        #     self.build_trend_weight
        # ]
        # for build in builds:
        #     build(keyword, weights, weight_queue)

        self.build_keyword_negate(keyword, weights, weight_queue)
        self.build_subject_weight(keyword, weights, weight_queue)
        self.build_booster_weight(keyword, weights, weight_queue)
        self.build_trend_weight(keyword, weights, weight_queue)

        # builds_extra = [
        #     self.build_area_weight,
        #     self.build_market_place_weight,
        # ]
        # for build in builds_extra:
        #     build(keyword, weights, extra_weight_queue)

        self.build_area_weight(keyword, weights, extra_weight_queue)
        self.build_market_place_weight(keyword, weights, extra_weight_queue)

        keyword_weight = sum(weight_queue)
        keyword_weight = keyword_weight * (extra_weight_queue[AREA] + extra_weight_queue[MARKET_PLACE])
        keyword[WEIGHT] = keyword_weight
        keyword[TOTAL_WEIGHT] = f"(<<keyword_weight>> + <<{AFFECTED_BY_ACTION}>> + <<{AFFECTED_BY_SUBJECT}>> + <<{AFFECTED_BY_BOOSTER}>> + <<{AFFECTED_BY_TREND}>>) * (<<area_weight>> + <<market_place_weight>>)"
        return keyword, weights

    def merge_linear_keywords(self, keywords):
        """
        Nối các từ khóa liên tục với nhau thành 1
        """
        result = []
        current_item = None
        _keywords = sorted(keywords, key=lambda x: x["index"])
        for item in _keywords:
            if current_item is None:
                current_item = item
            elif current_item["end_index"] == item["index"]:
                current_item["end_index"] = item["end_index"]
                item_indexs = item["indexs"][1:]
                item_words = item["name"].split()[1:]
                if len(item_words) > 0:
                    item_words = " ".join(item_words)
                    current_item["name"] += f' {item_words}'
                if current_item.get(AFFECTED_BY_TREND) is not None:
                    current_item[AFFECTED_BY_TREND] = 1 if (current_item[AFFECTED_BY_TREND] == 1 or item[AFFECTED_BY_TREND] == 1) else 0 
                    current_item[AFFECTED_BY_SUBJECT] = 1 if (current_item[AFFECTED_BY_SUBJECT] == 1 or item[AFFECTED_BY_SUBJECT] == 1) else 0 
                    current_item[AFFECTED_BY_ACTION] = 1 if (current_item[AFFECTED_BY_ACTION] == 1 or item[AFFECTED_BY_ACTION] == 1) else 0 
                    current_item[AFFECTED_BY_BOOSTER] = 1 if (current_item[AFFECTED_BY_BOOSTER] == 1 or item[AFFECTED_BY_BOOSTER] == 1) else 0 
                current_item["indexs"].extend(item_indexs)
            else:
                result.append(current_item)
                current_item = item

        if current_item is not None:
            result.append(current_item)
        return result 
             
    def cal_sentence_weight(self, sentence):
        """
        Tính toán trọng số của câucal_sentence_weight
        """
        refs = {}
        keywords = self.get_keyword_keywords(sentence)
        refs[SUBJECT] = self.get_subject_keywords(sentence)
        refs[SENTENCE] = sentence
        keyword_len = len(keywords)
        result = {
            SENTENCE: sentence,
            KEYWORDS: [],
            SENTENCE_WEIGHT: 0
        }
        if keyword_len == 0:
            return result
        
        negative_weight = 0
        positive_weight = 0
        if keyword_len > 0:
            for i in range(keyword_len):
                cal_keyword_weight = self.cal_keyword_weight(keywords[i], refs)
                keyword_item = {}
                self.copy_properties(keyword_item, cal_keyword_weight[KEYWORD], [NAME, FULL_NAME, 
                    INDEX, END_INDEX, AFFECTED_BY_TREND, AFFECTED_BY_SUBJECT, AFFECTED_BY_BOOSTER, 
                    AFFECTED_BY_AREA, AFFECTED_BY_MARKET_PLACE,  TOTAL_WEIGHT])
                self.copy_properties(keyword_item, cal_keyword_weight, [WEIGHT, WEIGHTS])
                
                result[KEYWORDS].append(keyword_item)
                if keyword_item[WEIGHT] < 0:
                    negative_weight += keyword_item[WEIGHT]
                else:
                    positive_weight += keyword_item[WEIGHT]   

            result[SENTENCE_POSITIVE_WEIGHT] = round(positive_weight, 3)    
            result[SENTENCE_NEGATE_WEIGHT] = round(negative_weight, 3)
            sentence_len = 2 if negative_weight != 0 and positive_weight != 0 else 1
            result[SENTENCE_WEIGHT] = round((negative_weight + positive_weight) / sentence_len, 3)    
        return result
    
    def cal_text_weight(self, text):
        """
        Dau vao co the la 1 cau, 1 doan, 1 bai
        """
        positive_weight = 0 
        negative_weight = 0 

        # Split text dau vao thanh cac cau
        sentences = self.split_text_into_sentences(self.trim_end_sentence_symbols(text))
        result = {
            SENTENCE_POSITIVE_WEIGHT: 0, # Diem tich cuc (diem +)
            SENTENCE_NEGATE_WEIGHT: 0, # Diem tieu cuc (diem -)
            SENTENCE_WEIGHT: 0, # trong so cua cau 
            "items": [] # Chi tiet tung cau
        }
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence != "":
                sentence_weight = self.cal_sentence_weight(sentence)
                positive_weight += sentence_weight.get(SENTENCE_POSITIVE_WEIGHT, 0)
                negative_weight += sentence_weight.get(SENTENCE_NEGATE_WEIGHT, 0)
                result["items"].append(sentence_weight)
                
        sentence_len = 2 if negative_weight != 0 and positive_weight !=0 else 1
        result[SENTENCE_POSITIVE_WEIGHT] = positive_weight
        result[SENTENCE_NEGATE_WEIGHT] = negative_weight
        result[SENTENCE_WEIGHT] = round((negative_weight + positive_weight) / sentence_len, 3)    
        return result   
 
