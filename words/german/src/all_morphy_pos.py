import pandas as pd
import sys

file = sys.argv[1]

df = pd.read_table(file, header=None)

first = df[2].unique()
second = df[3].unique()
print(first)