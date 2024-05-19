from tokenizer import tokenize
from tqdm import tqdm
import json
from collections import Counter
import datasets

def freqs(ds):
    counter = Counter()
    
    for item in tqdm(ds):
        counter.update(tokenize(item['text']))
        
    counter ={k: v for k, v in sorted(counter.items(), reverse=True, key=lambda x: x[1])}
    return counter
    
if __name__ == "__main__":
    OUT_FILE = "freqs_subtitles.json"
    ds = datasets.load_dataset('badranx/opus_raw', corpus="OpenSubtitles v2018", lang="de")
    #ds = datasets.load_dataset('badranx/opus_raw', corpus="News-Commentary v16", lang="de")
    ds = ds['train']#.select(range(1000))
    counter = freqs(ds)

    with open(OUT_FILE, 'w', encoding='utf8') as f:
        json.dump(counter, f, ensure_ascii=False, indent=4)