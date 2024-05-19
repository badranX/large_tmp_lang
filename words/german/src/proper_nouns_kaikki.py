import json

def word_gen(wikifile):
    words = set()
    with open(wikifile, 'r') as f:
        for line in f:
            d = json.loads(line)
            if d['pos'] == "name":
                word = d['word'].strip()
                if " " not in word and word not in words:
                    words.add(word)
                    yield d['word']


if __name__ == "__main__":
    import sys
    OUT_FILE = "proper_nouns.txt"
    file = sys.argv[1]
    BUFFER = ""
    with open(OUT_FILE, 'w') as f:
        for x in word_gen(file):
            BUFFER += x + '\n'
            if len(BUFFER) > 1000:
                f.write(BUFFER)
                BUFFER = ""
        f.write(BUFFER)

    print("done writing to: ", OUT_FILE) 
    
