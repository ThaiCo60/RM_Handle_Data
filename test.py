def trim_end_sentence_symbols(source, removeAll=False):
    """Loại bỏ dấu kết thúc câu (,.,?,..)"""
    text = source
    characters_to_remove = ['“', '”', ',']
    for char in characters_to_remove:
        text = text.replace(char, '')
    return text    


print(trim_end_sentence_symbols('Avalanche (AVAX) tăng gần 120% trong tháng và đang ở ngưỡng “quá mua”'))