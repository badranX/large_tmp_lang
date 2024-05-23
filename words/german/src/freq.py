from tokenizer import tokenize, tokenize_middle
from toolz import compose
import argparse
from tqdm import tqdm
import json
from collections import Counter
import datasets

class Freq():
    def __init__(self, freqs, midfreqs, engfreq):
        #it always ignore upper case words, only normal words are handled
        def filter(word):
            if len(word) > 1:
                return word[1:].islower()
            elif len(word) == 1:
                return True
            else:
                return False

        freqs = {k: v for k, v in freqs.items() if filter(k)}
        freqs = {k.lower(): freqs.get(k.lower(), 0) + freqs.get(k.capitalize(), 0) for k, v in freqs.items() if filter(k)}

        engfreq = {k: v for k, v in engfreq.items() if filter(k)}
        engfreq = {k.lower(): engfreq.get(k.lower(), 0) + engfreq.get(k.capitalize(), 0) for k, v in engfreq.items() if filter(k)}
        engfreq = {kv[0]: kv[1] for i, kv in compose(enumerate, sorted)(engfreq.items(), key=lambda x: x[1], reverse=True) if i<2000}
        #self.freqs = lowercase_freqs(freqs)
        self.freqs = freqs
        self.engfreqs = engfreq

        self.midfreqs = {k: v for k, v in midfreqs.items() if filter(k)}
        #print("Ich :", self.midfreqs.get('Ich'))
        inverse_case = lambda x: x.capitalize() if x[0].islower() else x.lower()
        f_percentage = lambda x: self.midfreqs.get(x,0)/(self.midfreqs.get(inverse_case(x),0) + self.midfreqs.get(x,0.00001))
        self.midfreqs = {k: f_percentage(k) for k, v in midfreqs.items()}
        
        #mean_freq = sum(self.freqs.values())/len(self.freqs.values())
        #mean_mid = sum(self.freqs.values())/len(self.freqs.values())
        

    def is_eng(self, w):
        return w.lower() in  self.engfreqs

        
    def get_mid_diff(self, w):
        return abs(self.midfreqs.get(w.lower().capitalize(), 0) - self.midfreqs.get(w.lower(), 0))
    
    def accept_freq(self, w, low=500):
        return self.freqs.get(w,0) > low
        
    def accept_case(self, w, percent=0.95):
        if len(w) > 1 and not w[1:].islower():
            print('WARNING: word is uppper case: ', w)
            return False

        upper_freq = self.midfreqs.get(w.lower().capitalize(), 0)
        lower_freq =  self.midfreqs.get(w.lower(), 0)
        #diff = upper_freq - lowercase_freqs
        if w[0].isupper() and upper_freq > 0.5:
            return True
        if w[0].islower() and lower_freq > 0.5:
            return True
        return False

    def get_freq(self, w):
        #P_obs = P*P_correct + (1-P)*P_mistake
        #P_mistake = 0.001
        #P_correct = P_obs*(1 - P_mistake) + (1-P_obs)*(P_mistake)
        if self.is_not_mid(w):
            return self.freqs.get(w.lower(),0)# * self.midfreqs.get(w, 0)
        else:
            return self.freqs.get(w.lower(),0) * self.midfreqs.get(w, 0)

    def is_not_mid(self, w):
        return w.lower() not in self.midfreqs and w.lower().capitalize() not in self.midfreqs

    def get_lower_freq(self, w):
        return self.freqs.get(w.lower(), 0)

    def top_lower(self, num):
        return [k.lower() for i, k in enumerate(self.freqs.keys()) if i<num]
    
    def is_mistake(self, word, percent=0.1):
        #inv = inverse_case(word)
        return self.midfreqs.get(word, 0) < percent

    def is_low_freq(self, word, occured=100):
        return self.get_freq(word) < occured
        

def inverse_case(w):
    f = lambda x: x.capitalize() if x[0].islower() else x.lower()
    return f(w)

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
    
    #OUT_FILE = "freqs_subtitles.json"
    #MID_OUT_FILE = "freqs_mid_subtitles.json"
    OUT_FILE = "en_freqs_EUBooks.json"
    MID_OUT_FILE = "en_freqs_mid_EUBooks.json"

    #ds = datasets.load_dataset('badranx/opus_raw', corpus="OpenSubtitles v2018", lang="de")
    #ds = datasets.load_dataset('badranx/opus_raw', corpus="EUbookshop v2", lang="de")
    #ENGLISH
    ds = datasets.load_dataset('badranx/opus_raw', corpus="EUbookshop v2", lang="en")
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
    

def nottest_freq():
    freqs = {'a': 10000, 'A':10}
    midfreqs = {'a': 10000, 'A':1}
    f= Freq(freqs, midfreqs)
    print('freq perc: ', f.midfreqs.get('A'))
    print('freq: ', f.get_freq('A'))
    assert f != None
    
def test_freq():
    ds = datasets.load_dataset('badranx/opus_raw', corpus="EUbookshop v2", lang="de")
    #ds = datasets.load_dataset('badranx/opus_raw', corpus="News-Commentary v16", lang="de")
    ds = ds['train']#.select(range(1000))
    for item in ds:
        text = item['text']
        if "Ich" in tokenize_middle(text):
            print(text)
