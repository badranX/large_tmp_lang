import pandas as pd
from tqdm import tqdm
import os
from dotenv import load_dotenv
import argparse
from openai import OpenAI

POS2word = {"verb": "verb", "noun": "noun", "adj": "adjective", "adv": "adverb"}
SYSTEM_CONTENT = "You are a German language teacher and a dictionary author"
#"Give ten examples without translation to learn the German verb "gebrauchen" (inflections: "gebraucht", "gebrauchte", "gebrauchten"):


class Client():
    #PROMPT = "Give ten examples without translation to learn the German word "
    PROMPT = "Give ten usage examples without translation to learn the German " 

    #verb "gebrauchen" (inflections: "gebraucht", "gebrauchte", "gebrauchten"):

    USER_PROMPT = {"role": "user", "content": ""}
    SYSTEM_PROMPT = {"role": "system", "content": SYSTEM_CONTENT}

    MODEL = "gpt-3.5-turbo"
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI")
        )

    @classmethod
    def construct_args(cls, item):
        user_prompt =  cls.construct_content(item)
        messages = [cls.SYSTEM_PROMPT, user_prompt]
        args = {"model": cls.MODEL,
                "messages": messages}
        return args
    
    @classmethod
    def accept_item(cls, item):
        pos = item['pos'] 
        pos = POS2word.get(pos.lower(), False)
        if not pos:
            return False
        return True

    @classmethod        
    def construct_content(cls, item):
        #lemma = item['lemma']
        words = item['inflection']
        tmp = item['pos'] 
        pos = POS2word.get(tmp.lower(), None)
        if not pos:
            raise Exception('part of speech not supported: {}'.format(tmp)) 

        txt = cls.PROMPT
        txt += f"{pos} \"{words[0]}\""
        if len(words) > 1:
            tmp = ', '.join(map(lambda x: f"\"{x}\"", words[1:4]))
            txt += f" (inflections: {tmp})"
        ret = dict(cls.USER_PROMPT)
        ret.update({"content": txt})
        return ret

     

    def request(self, item, save_column):
        #return 'TEST'
        save = item[save_column]
        #TODO remove this
        #pos = item['pos'].lower()
        if save:# #and pos == 'verb':
            return item[save_column]
        args = self.construct_args(item)
        completion = self.client.chat.completions.create(**args)
        return completion.choices[0].message.content


def parse_input():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument('openai', help='parquet file')
    parser.add_argument('output', nargs='?', default="openai_response.parquet", help='parquet file')
    args = parser.parse_args()
    return args

def process(preopenai):
    df = pd.read_parquet(preopenai)
    if 'index' in df.columns:
        df = df.drop(columns=['index'])
    df = df.iloc[:5000]
    df = df.explode('pos')
    df = df[df.apply(Client.accept_item, axis=1)]
    df = df.reset_index(drop=True)
    return df

def save_df(df, outfile):
    df = df.reset_index(drop=True)
    df.to_parquet(outfile, index=False)
    df.to_csv(outfile + '.csv', sep='\t', index=False)

if __name__ == '__main__':
    save = 'openai1'
    args = parse_input()
    df = process(args.openai)
    print(df.columns)
    client = Client()
    if save not in df.columns:
        df[save] = ''
    
    idx = slice(1401, 4999)
    #tmp = df.iloc[idx]
    #df[save].iloc[idx] = tmp.apply(lambda x: str(client.construct_args(x)), axis=1)
    #df[save].iloc[idx] = tmp.apply(lambda x: client.request(x, save), axis=1)
    #save_df(df, args.output)
    for i in tqdm(range(idx.start, idx.stop)):
        item = df.iloc[i]
        response = client.request(item, save)
        lemma = item['lemma']
        print('lemma: ', lemma)
        print(response)
        df[save].iloc[i] = response
        if i % 100 == 0:
            save_df(df, args.output)
    save_df(df, args.output)

    #x = df.apply(generate_prompt, axis=1)
    #print(x)
    #for i, item in df.iterrows():
    #    #args = client.request(item)
    #    #print(args)
    #    break
    #    #if item.get('openai1', False)
#
#        if i % 30:
            
