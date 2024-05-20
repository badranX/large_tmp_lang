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
    
words = words[words['word'].apply(lambda x: freqs.get(x, 0)> 1000)]
lemmawords = lemmas.explode('inflection')#['inflection']
lemmawords = lemmawords[['inflection', 'pos']].drop_duplicates().reset_index()
lemmawords = lemmawords['inflection'].unique()
#print(lemmas.columns)
words = words['word'].unique()
nolemma = set(words) - set(lemmawords)
nolemma = sorted(nolemma, reverse=True, key=lambda x: freqs.get(x, 0))
nolemma = pd.DataFrame({1: list(nolemma)}) 


nolemma.to_csv('nolemma.tsv', sep='\t', index=None, header=None)