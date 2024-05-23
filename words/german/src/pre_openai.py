import json
from functools import reduce
from collections import Counter
from freq import Freq, lowercase_freqs
import argparse
import pandas as pd
import sys

MAIN_POS = ['verb', 'noun', 'adj', 'adv']
RENAME_MORPHY= {'N': 'noun',
  'V': 'verb',}
parser = argparse.ArgumentParser(description='Process three file paths.')
parser.add_argument('lemmas', type=str, help='parquet file')
parser.add_argument('words', type=str, help='Path to the second file')
parser.add_argument('freqs', type=str, help='Path to the third file')
parser.add_argument('midfreqs', type=str, help='Path to the third file')
parser.add_argument('eng_freq', type=str, help='Path to the third file')


args = parser.parse_args()
lemmas = pd.read_parquet(args.lemmas)
dictwords = pd.read_table(args.words)
dictwords = dictwords.dropna()
#freqs = pd.read_parquet(args.freqs)
with open(args.freqs,'r', encoding='utf8') as freq, open(args.midfreqs, 'r', encoding='utf8') as fmid, open(args.eng_freq, 'r') as feng:
  f = json.load(freq)
  fmid = json.load(fmid)
  engfreq = json.load(feng)
  freqs = Freq(f, fmid, engfreq)    
#restrict to high freq words
#print(words.word.apply(lambda x: x if isinstance(x, float) else 's' ).unique())
dictwords = dictwords[dictwords['word'].apply(lambda x: freqs.get_freq(x)> 1000)]

dict_words = set(dictwords['word'].unique())
all_lemma_related = set(lemmas['inflection'].explode().unique())
nolemma_group = set(dict_words) - set(all_lemma_related)
#nolemma_group = words[words['word'].apply(lambda x: x.lower()).isin(nolemma_group)]
nolemma_group = dictwords[dictwords['word'].isin(nolemma_group)]

#print(nolemma)
#print(lemmas.pos.unique())
#nolemma = sorted(nolemma, reverse=True, key=lambda x: freqs.get(x, 0))
 
  
#nolemma_group['pos'] = nolemma_group['pos'].apply(lambda x: rename.get(x, x).lower())
nolemma_group = nolemma_group.rename(columns={'word': 'lemma'})
#nolemma_group = nolemma_group.groupby('lemma').apply(list)

nolemma_group = nolemma_group.groupby('lemma').agg(tuple).reset_index()
nolemma_group['inflection'] = nolemma_group.lemma.apply(lambda x: [x])
lemmas['pos'] = lemmas.pos.apply(lambda x: [x])
#nolemma_group['freq'] = nolemma_group.lemma.apply(lambda x: freqs.get_freq(x))

#save openai
allwords = pd.concat([lemmas, nolemma_group])
allwords.inflection = allwords.inflection.apply(list)
allwords.loc[:, 'pos'] =  allwords.pos.apply(lambda l: [RENAME_MORPHY.get(x,x) for x in l])

#filter guard
allwords = allwords[allwords.lemma.apply(freqs.accept_case)]
allwords.loc[:, 'inflection'] = allwords.inflection.apply(lambda x: list(filter(freqs.accept_case, x)))

#allwords = allwords[allwords.lemma.apply(freqs.accept_freq)]
#allwords.loc[:, 'inflection'] = allwords.inflection.apply(lambda x: list(filter(freqs.accept_freq, x)))
#done filter guard

allwords.loc[:, 'freq'] = allwords.inflection.apply(lambda x: 
                                                sum(freqs.get_freq(w) for w in x))

allwords.loc[:, 'lemma_freq'] = allwords.lemma.apply(lambda x: freqs.get_freq(x))

allwords = allwords.sort_values(by='freq', ascending=False)
allwords.to_parquet('./openai.parquet') 
allwords.to_csv('./openai.debug.csv', sep='\t', index=None) 
#DONE processing

#check english words
df = allwords
df = df[df.lemma.apply(freqs.is_eng)]
df.to_csv('eng_lemmas.csv', sep='\t', index=False)
#check conflict capitalization
df = allwords#.lemma.apply(lambda x: x.lower()).groupby('lemma').agg(list).reset_index()
df['tmp'] = df.lemma.apply(lambda x: x.lower())
print(df.columns)
df = df.groupby('tmp').agg(list).reset_index()
print(df.columns)
df = df[df.lemma.apply(lambda x: len(set(x))>1 and freqs.get_mid_diff(x[0]) > 0.95)]
df = df.sort_values(by='tmp', ascending=False, key=lambda x: x.apply(freqs.get_freq) )
df.to_csv('capitalize_problem.csv', sep='\t', index=False)


#check  bags conflicts
df = allwords.groupby('lemma').agg(list).reset_index()
def tmp(x):
  test = [x[0]==y for y in x]
  return not all(test)
boolidx =df.inflection.apply(tmp) 

#save conflicts
df[boolidx].to_csv('conflict_pos.csv', sep='\t', index=False)
def tmp(x):
  test = [x[0]==y for y in x]
  return all(test) and len(x) > 1 and len(x[0])>1
#save conflicts
boolidx = df.inflection.apply(tmp) 
df[boolidx].to_csv('match_bags.csv', sep='\t', index=False)


#
#allwords['tmp'] = allwords.pos.apply(lambda w: w if w in MAIN_POS else 'same')
#allwords = allwords.groupby(['lemma', 'tmp']).agg(list).reset_index()
#allwords = allwords.drop(columns=['tmp'])
#allwords.inflection.apply(lambda x: list(set([w for w in y for y in x])))

#allwords.inflection = allwords.inflection.apply(lambda x: list(set([w for y in x for w in y])))


#check pos
print('openai pos: ', set(allwords.pos.explode().unique()))

def check_similar_inflections():
  word2lemma = dict()
  for infs, lemma in zip(allwords.inflection, allwords.lemma):
    word2lemma.update({k: word2lemma.get(k, []) + [lemma] for k in infs})
  word2lemma = {k: set(v) for k, v in word2lemma.items()}
  word2lemma = {k: list(v) for k, v in word2lemma.items() if len(v) > 1}
  json.dump(word2lemma, open("multilemma.txt", 'w'), ensure_ascii=False, indent=4)
check_similar_inflections()



#check against freqs 
def check_not_in_dict():
  topwords = set(freqs.top_lower(5000))
      
  notfound = topwords - set(map(lambda x: x.lower(), dict_words))
  notfound = notfound - set(map(lambda x: x.lower(), all_lemma_related))
  print(len(notfound))
  df = pd.DataFrame(list(notfound))
  df['freq'] = df[0].apply(lambda x: freqs.get_lower_freq(x))

  df = df.sort_values(by='freq', ascending=False, axis=0)

  df.to_csv('notfound.txt', sep='\t', index=None, header=None)
check_not_in_dict()

#check for informal
def check_informal():
  df = allwords[allwords.lemma.apply(freqs.is_not_mid)]
  df['lemfreq'] = df.lemma.apply(freqs.get_freq)
  df['lowcasefreq'] = df.lemma.apply(lambda x: freqs.freqs.get(x.lower(),0))
  df.to_csv('informal.csv', sep='\t', index=False)
check_informal()

  #check for very low freqs lemmas
def check_lowfreq_lemmas():
  df = allwords[allwords.lemma.apply(freqs.is_low_freq)]
  df['lemfreq'] = df.lemma.apply(freqs.get_freq)
  df['lowcasefreq'] = df.lemma.apply(lambda x: freqs.freqs.get(x.lower(),0))
  df.to_csv('lowfreq.csv', sep='\t', index=False)
check_lowfreq_lemmas()



#check for capitalized mistakes
def check_capitalize():
  all_lemmas = set(allwords.iloc[:5000,:].lemma.unique())
  lemma_dublicate = [{'lemma': w,
                      'midpercent': freqs.midfreqs.get(w, 0),
                      'freq': freqs.freqs.get(w.lower(),0),
                      'final_freq': freqs.get_freq(w)} for w in all_lemmas if freqs.is_mistake(w)]
  #lemma_dublicates = Counter([w.lower() for w in all_lemmas])
  #dublicates  = sorted([w for w, c in lemma_dublicates.items() if c> 1], reverse=True, key=lambda x: freqs.get_lower_freq(x))
  #dublicates = [w for w in dublicates if freqs.is_mistake(w)]
  pd.DataFrame(lemma_dublicate).to_csv('dublicates.csv', sep='\t')
check_capitalize()
#open('dublicates.txt', 'w', encoding='utf8').write('\n'.join(lemma_dublicate))
#print(allwords)
#nolemma = pd.DataFrame({1: list(nolemma)}) 


# nolemma.to_csv('nolemma.tsv', sep='\t', index=None, header=None)