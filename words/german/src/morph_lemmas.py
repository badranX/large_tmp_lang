import pandas as pd
import sys
from common import filter_word
import re
import json


pattern = re.compile(r"[;|]")
file = sys.argv[1]
freqfile = sys.argv[2]

with open(freqfile, 'r', encoding='utf8') as f:
    freq = json.load(f)

df = pd.read_table(file, header=None)
df = df[df[0].apply(filter_word)]
df = df[df[1].apply(filter_word)]
df['pos'] = df[2].apply(lambda x: pattern.split(x)[0])
df = df.rename(columns={0: 'lemma', 1: 'inflection'})
print(df.columns)
setf = lambda x: list(set([word for word in x if filter_word(word)]))
df = df.groupby(['lemma', 'pos'])['inflection'].apply(setf).reset_index()
print(df.columns)
df['inflection'] = df.apply(lambda x: list(set(
    [x.lemma] + x.inflection
    )), axis=1)

df['inflection'] = df['inflection'].apply(lambda x: sorted(x, reverse=True, key=lambda w: freq.get(w, -1)) )
#newdf['freq'] = newdf['lemma'].apply(lambda x: freq.get(x, 0))
#print(df.columns)
df['freq'] = df['inflection'].apply(lambda x: sum([freq.get(w, 0) for w in x]))

df = df.sort_values(by='freq', ascending=False)
#newdf = newdf[]
df.to_csv("lemmas.tsv", sep='\t', index=False)