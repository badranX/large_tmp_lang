import json
import argparse
import pandas as pd
import sys

parser = argparse.ArgumentParser(description='Process three file paths.')
parser.add_argument('lemmas', type=str, help='Path to the first file')
parser.add_argument('words', type=str, help='Path to the second file')
parser.add_argument('freqs', type=str, help='Path to the third file')


args = parser.parse_args()
lemmas = pd.read_parquet(args.lemmas)
words = pd.read_table(args.words)
#freqs = pd.read_parquet(args.freqs)
with open(args.freqs, 'r', encoding='utf8') as f:
    freqs = json.load(f)
    
#restrict to high freq words
words = words[words['word'].apply(lambda x: freqs.get(x, 0)> 1000)]

dict_words = set(words['word'].unique())
all_lemma_related = set(lemmas['inflection'].explode().unique())
nolemma_group = set(dict_words) - set(all_lemma_related)
nolemma_group = words[words['word'].isin(nolemma_group)]

#print(nolemma)
print(lemmas.pos.unique())
#nolemma = sorted(nolemma, reverse=True, key=lambda x: freqs.get(x, 0))
 
rename= {'N': 'noun',
  'V': 'verb',}
  
#nolemma_group['pos'] = nolemma_group['pos'].apply(lambda x: rename.get(x, x).lower())

nolemma_group['inflection'] = nolemma_group.word.apply(lambda x: [x])
nolemma_group = nolemma_group.rename(columns={'word': 'lemma'})
nolemma_group['freq'] = nolemma_group.lemma.apply(lambda x: freqs.get(x,0))

allwords = pd.concat([lemmas, nolemma_group])
allwords['pos'] = allwords['pos'].apply(lambda x: rename.get(x, x).lower())
print(allwords)
    
#check agains freqs
    
topwords = set([k for i, k in enumerate(freqs.keys()) if i<5000])
    
notfound = topwords - dict_words
notfound = topwords - all_lemma_related
print(len(notfound))
df = pd.DataFrame(list(notfound))
df['freq'] = df[0].apply(lambda x: freqs.get(x,0))

df.sort_values(by='freq', ascending=False, axis=0)

df.to_csv('notfound.txt', sep='\t', index=None, header=None)
#print(allwords)
#nolemma = pd.DataFrame({1: list(nolemma)}) 


# nolemma.to_csv('nolemma.tsv', sep='\t', index=None, header=None)