import json
import pandas as pd
import datasets
import re
from common import pattern, filter_word




POS = ["proverb", "num", "article", "postp", "prefix", "symbol", "circumpos", "intj", "adv", "conj", "pron", "prep", "infix", "circumfix", "suffix", "name", "punct", "phrase", "det", "adj", "character", "prep_phrase", "verb", "particle", "noun", "interfix"]

IGNORE_POS = ["name", "symbol", "infix", "suffix", "punct", "phrase", "prep_phrase", "character", "interfix"]

CONTRACTION_POS = "contraction"

def filter_pos(pos):
    isnt_ignore = pos not in IGNORE_POS
    return isnt_ignore


def filter_suspect(word):
    return " " not in word

def word_gen(wikifile):
    words = set()
    suspect_words = set()
    contractions = set()
    with open(wikifile, 'r') as f:
        for line in f:
            d = json.loads(line)
            #print(d['word'])
            #print(d.get('senses')[-1])
            if filter_pos(d['pos']):
                word = d['word'].strip()
                pos = d['pos']
                if pos == CONTRACTION_POS:
                    contractions.add((word, pos))
                if filter_word(word):
                    words.add((word, pos))
                elif filter_suspect(word):
                    suspect_words.add((word, pos))

    def tmp(s):
        return [{'word': k, 'pos': v} for k, v in s]

    return tmp(words), tmp(contractions), tmp(suspect_words)

def save(out_file):
    ds = datasets.Dataset.from_generator(susgen)
    ds.to_csv(sus_OUT_FILE, sep='\t')

if __name__ == "__main__":
    import sys
    OUT_FILE = "words_wiki_out.tsv"
    sus_OUT_FILE = "suspect_words.tsv"
    contract_FILE = "contractions.tsv"

    wikifile = sys.argv[1]
    words, contractions, sus_words = word_gen(wikifile)
    pd.DataFrame(words).to_csv(OUT_FILE, sep='\t', index=False)
    pd.DataFrame(sus_words).to_csv(sus_OUT_FILE, sep='\t', index=False)
    pd.DataFrame(contractions).to_csv(contract_FILE, sep='\t', index=False)


    print("done writing to: ", OUT_FILE) 
