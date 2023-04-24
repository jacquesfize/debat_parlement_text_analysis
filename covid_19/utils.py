from inflection import singularize
from stop_words import get_stop_words
import re

stop_words_fr = get_stop_words("fr")

def clean(text):
    words = text.split()
    for i in [0, -1]:
        if len(words[i]) == 2 and words[i].endswith("'"):
            return False
    return True

def clean_text(text):
    return re.sub("(\.)[A-Z]",lambda x: x.group(0).replace(".",". "),text).strip()

def singularize_term(term):
    return " ".join([singularize(word) if word not in stop_words_fr else word for word in term.split()])