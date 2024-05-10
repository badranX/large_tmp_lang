import datasets
import json
from pathlib import Path
import hashlib
from db import engine


ENCODING = "utf-8"
LENGTH = 16

def langhash(text):
    text = text.encode(ENCODING)
    return hashlib.sha1(text).hexdigest()[:16]

"""
h(sent1) == h(sent2) iff max(sent1) 
"""

class TokenizerPipeline():
    def __init__(self, tokenize, langfilter=None, batch_size=64):
        self.tokenize = tokenize
        self.batch_size = batch_size
        self.langfilter = langfilter

    def start(self, ds):
        """expect a hg dataset that contain the feature 'text' """
        print("start tokenizing sentenceas...")
        ds = ds.map(self._tokenize, batch_size=64, batched=True, remove_columns=['text'])
        print("done tokenization.")
        return ds


    def _preprocess(self, batch):
        new = {}
        texts = map(lambda x: x.strip(), batch['text'])
        if self.langfilter:
            new['text'] = list(filter(lambda x: self.langfilter(x), texts))
        else:
            new['text'] = list(texts)

        new['hash'] = list(map(lambda x: langhash(x), new['text']))
        return new
    
    def _tokenize(self, batch):
        new = self._preprocess(batch)
        tokenizer_output = self.tokenize(new['text'])
        #del new['text']
        new.update(tokenizer_output)
        return new


def dataset2file(ds, outfile):
    outfile = Path(outfile)
    if outfile.exists():
        raise Exception("File already exists: {}".format(outfile.name))
    filetype = outfile.suffix[1:]
    save_to = getattr(ds, "to_" + filetype)
    save_to(outfile)

def load2db(files_folder, engine, append=False):    
    files_folder = Path(files_folder)
    
    
class SpacyHandler:
    IGNORE_POS = ['PUNCT', 'SYM', 'X', 'PROPN'] 
    @classmethod
    def get_spacy_tokenizer(cls, pipeline="en_core_web_sm"):
        import spacy

        nlp = spacy.load(pipeline)
        
        def tokenizer(batch):
            docs = nlp.pipe(batch, disable=["ner"])
            tokenbatch = [[token for token in doc] for doc in docs]
            return {
                    "tokens": [[token.text for token in tokens] for tokens in tokenbatch],
                    "lemma_": [[token.lemma_ for token in tokens] for tokens in tokenbatch],
                    "pos_": [[token.pos_ for token in tokens] for tokens in tokenbatch],
                    "idx": [[token.idx for token in tokens] for tokens in tokenbatch]
                    }
        return tokenizer
    
    @classmethod
    def get_basic_KCs(cls, item):
        itr = zip(item["lemma_"], item["pos_"], item["idx"])
        ff = lambda x: x[1] not in cls.IGNORE_POS
        itr = filter(ff, itr)
        KCs = list(map(lambda x: f"{x[0]}_{x[1]}", itr))
        idx = list(map(lambda x: x[2], itr))

        return {"hash": item["hash"],
                "KCs": json.dumps(KCs),
                "idx": json.dumps(idx),
                }


def build_Q_matrix(ds, save_file="Q.json"):
    KC2hashs = {}
    for d in ds:
        l = json.loads(d["KCs"])
        for KC in l:
            tmp = KC2hashs.get(KC, set())
            tmp.add(d["hash"])
            KC2hashs[KC] = tmp
    
    KC2hashs = {k: list(v) for k, v in KC2hashs.items()}

    with open("Q.json", 'w') as f:
        json.dump(KC2hashs, f, indent=4)
    return KC2hashs


def get_simple_tokenizer():
    f = lambda x: {'tokens': list(map(lambda txt: txt.split(), x))}
    return f


if __name__ == "__main__":
    #tokenize = get_simple_tokenizer()
    #import sys
    
    #outfolder = sys.argv[1]
    #pth = Path(outfolder)
    #if pth.exists():
    #    raise Exception("File or path provided alredy exists: " + str(pth))
    
    #pth.mkdir(exist_ok=False)
      
    tokenize = SpacyHandler.get_spacy_tokenizer()
    langfilter = lambda x: True
    ppl = TokenizerPipeline(tokenize, langfilter)

    ds = datasets.load_dataset('badranx/opus_raw', corpus="News-Commentary v16", lang="en")
    ds = ds['train']
    #ds.to_parquet("")

    #ds = ppl.start(ds.select(range(10)))
    ds = ppl.start(ds)
    #ds.to_json("spacy_results.json")
    ds.to_parquet("spacy_opus_news_en.parquet")
    #ds = ds.map(SpacyHandler.get_basic_KCs, remove_columns=ds.column_names)
    #ds.to_json('test.json')
    #build_Q_matrix(ds)
    #print(l)
