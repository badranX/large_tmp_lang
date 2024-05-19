def intersect(words_f, ppn_f):
    with open(words_f, 'r') as wf, open(ppn_f, 'r') as ppn_f:
        ppn = set([w for w in ppn_f])
        for w in wf:
            if w in ppn:
                print(w)

if __name__ == "__main__":
    import sys
    words_f = sys.argv[1]
    ppn_f = sys.argv[2]
    intersect(words_f, ppn_f)
