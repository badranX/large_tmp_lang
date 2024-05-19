import re

pattern = re.compile(r"[a-zA-ZäöüÄÖÜß]*")

def filter_word(word):
    is_pattern = bool(pattern.fullmatch(word))
    return is_pattern