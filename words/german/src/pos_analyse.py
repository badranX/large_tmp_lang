import pandas as pd


def analyse(file):
    df = pd.read_table(file)
    tmp = df.groupby('word').count()
    tmplist = df.groupby('word')['pos'].apply(list)
    tmp = tmplist[tmp['pos'] > 1]
    print(tmp)


if __name__ == "__main__":
    import sys
    
    file = sys.argv[1] 
    analyse(file)
