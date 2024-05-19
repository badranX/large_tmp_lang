import pandas as pd
import re
import sys

pattern = re.compile(r"[|;]")

file = sys.argv[1]

df = pd.read_table(file, header=None)
df['pos'] = df[2].apply(lambda x: pattern.split(x)[0])
df = df.drop(columns=[2,3])
df = df.rename(columns={0: "lemma", 1: "word"})

#map(lambda x: pattern.split(x)[0], df[2].unique())#.apply(lambda x: pattern.split(x))
print(df)