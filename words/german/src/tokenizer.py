from tokenizers.pre_tokenizers import Whitespace
import re

#You can later analyse the token freqs output 
#geht's -> geht & 's can be analysed later
pattern = re.compile(r"\w+'*\w+")

def tokenize(txt):
    return pattern.findall(txt)

if __name__ == "__main__":
    print(tokenize("wow geht's the way's"))