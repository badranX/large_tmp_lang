from tokenizer import tokenize, tokenize_middle
import argparse
from tqdm import tqdm
import json
from collections import Counter
import datasets

class Freq():
    def __init__(self, freqs, midfreqs):
        #it always ignore upper case words, only normal words are handled
        def filter(word):
            if len(word) > 1:
                return word[1:].islower()
            else:
                return True

        freqs = {k: v for k, v in freqs.items() if filter(k)}
        freqs = {k.lower(): freqs.get(k.lower(), 0) + freqs.get(k.capitalize(), 0) for k, v in freqs.items() if filter(k)}
        #self.freqs = lowercase_freqs(freqs)
        self.freqs = freqs

        self.midfreqs = {k: v for k, v in midfreqs.items() if filter(k)}
        inverse_case = lambda x: x.capitalize() if x[0].islower() else x.lower()
        f_percentage = lambda x: midfreqs.get(x,0)/(midfreqs.get(inverse_case(x),0) + midfreqs.get(x,0.00001))
        self.midfreqs = {k: f_percentage(k) for k, v in midfreqs.items()}
        
    def get_freq(self, w):
        print(self.freqs)
        print(self.midfreqs)
        return self.freqs.get(w.lower(),0) * self.midfreqs.get(w, 0)
        

def freqs(ds):
    counter = Counter()
    
    for item in tqdm(ds):
        counter.update(tokenize(item['text']))
        
    counter ={k: v for k, v in sorted(counter.items(), reverse=True, key=lambda x: x[1])}
    return counter
    

def mid_freqs(ds):
    counter = Counter()
    for item in tqdm(ds, desc='middle frequency..'):
        counter.update(tokenize_middle(item['text']))
        
    counter ={k: v for k, v in sorted(counter.items(), reverse=True, key=lambda x: x[1])}
    return counter

def lowercase_freqs(jsonfile):
    with open(jsonfile, 'r', encoding='utf8') as f:
        freqs = json.load(f)
    #get rid of all capitals
    def filter(word):
        return word[1:].islower()
    freqs = {k: v for k, v in freqs.items() if filter(k)}
    freqs = {k.lower(): freqs.get(k.lower(), 0) + freqs.get(k.capitalize(), 0) for k, v in freqs.items() if filter(k)}
    return freqs

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--middle", action='store_true', default=False, help="If set, run eval")
    args = parser.parse_args()
    
    OUT_FILE = "freqs_subtitles.json"
    MID_OUT_FILE = "freqs_mid_subtitles.json"

    ds = datasets.load_dataset('badranx/opus_raw', corpus="OpenSubtitles v2018", lang="de")
    #ds = datasets.load_dataset('badranx/opus_raw', corpus="News-Commentary v16", lang="de")
    ds = ds['train']#.select(range(1000))
    if not args.middle:
        counter = freqs(ds)
        with open(OUT_FILE, 'w', encoding='utf8') as f:
            json.dump(counter, f, ensure_ascii=False, indent=4)
    else:

        counter = mid_freqs(ds)
        with open(MID_OUT_FILE, 'w', encoding='utf8') as f:
            json.dump(counter, f, ensure_ascii=False, indent=4)
    
    
def test_freq():
    freqs = {'a': 1}
    midfreqs = {'a': 1, 'A':2}
    f= Freq(freqs, midfreqs)
    print('freq: ', f.get_freq('a'))
    print("yahooo")
    assert True    