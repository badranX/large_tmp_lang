from tokenizers.pre_tokenizers import Whitespace
import regex as re
#import re

#You can later analyse the token freqs output 
#geht's -> geht & 's can be analysed later
ALPH = r"[a-zA-Z'äöüÄÖÜß]"
pattern = re.compile(f"{ALPH}+'?{ALPH}+")
#pattern_start = re.compile(r"(?<!^|\.) \w+'?\w+")
pattern_start = re.compile(f"(?<!^|\.)\w {ALPH}+'?{ALPH}+")

def tokenize(txt):
    return pattern.findall(txt)
    
def tokenize_middle(txt):
    itr = pattern_start.findall(txt)
    return list(map(lambda x: x[1:].lstrip(), itr))

def tokenize_itr(txt):
    return pattern.findall(txt)

if __name__ == "__main__":
    print(tokenize("wow geht's the way's"))