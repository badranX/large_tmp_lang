import json

def all_pos(wikifile):
    poses = set()
    with open(wikifile, 'r') as f:
        for line in f:
            d = json.loads(line)
            poses.add(d['pos'])
        return poses


if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    poss = all_pos(file)
    json.dump(list(poss), open("pos.json", 'w'))
    print("done writing")

    
