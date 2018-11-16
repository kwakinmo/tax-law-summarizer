import networkx
import re


class RawSentenceReader:

    def __init__(self, filepath):
        self.filepath = filepath
        #         self.rgxSplitter = re.compile('([.!?:](?:["\']|(?![0-9])))')
        self.rgxSplitter = re.compile('\n')

    def __iter__(self):
        for line in open(self.filepath, encoding='utf-8'):
            ch = self.rgxSplitter.split(line)
            for s in map(lambda a, b: a + b, ch[::2], ch[1::2]):
                if not s: continue
                yield s


class TextRank:

    def __init__(self, **kargs):
        self.graph = None
        self.window = kargs.get('window', 5)
        self.coef = kargs.get('coef', 1.0)
        self.threshold = kargs.get('threshold', 0.005)
        self.dictCount = {}
        self.dictBiCount = {}
        self.dictNear = {}
        self.nTotal = 0

    def loadSents(self, sentenceIter, tokenizer=None):  # 문장 추출.
        import math

        def similarity(a, b):
            n = len(a.intersection(b))
            return n / float(len(a) + len(b) - n) / (math.log(len(a) + 1) * math.log(len(b) + 1))

        if not tokenizer: rgxSplitter = re.compile('[\\s.,:;-?!()"\']+')
        sentSet = []
        for sent in filter(None, sentenceIter):
            if type(sent) == str:
                if tokenizer:
                    s = set(filter(None, tokenizer(sent)))
                else:
                    s = set(filter(None, rgxSplitter.split(sent)))
            else:
                s = set(sent)
            if len(s) < 2: continue
            self.dictCount[len(self.dictCount)] = sent
            sentSet.append(s)

        for i in range(len(self.dictCount)):
            for j in range(i + 1, len(self.dictCount)):
                s = similarity(sentSet[i], sentSet[j])
                if s < self.threshold: continue
                self.dictBiCount[i, j] = s

    def build(self):
        self.graph = networkx.Graph()
        self.graph.add_nodes_from(self.dictCount.keys())
        for (a, b), n in self.dictBiCount.items():
            self.graph.add_edge(a, b, weight=n * self.coef + (1 - self.coef))

    def rank(self):
        return networkx.pagerank(self.graph, weight='weight')

    def summarize(self, ratio=0.333):  # summarize by ratio
        r = self.rank()
        ks = sorted(r, key=r.get, reverse=True)[:int(len(r) * ratio)]
        return ' '.join(map(lambda k: self.dictCount[k], sorted(ks)))

if __name__ == '__main__':
    tr = TextRank(window=5, coef=1.0, threshold=0.001)
    topN = 20
    print('Load...')
    # from konlpy.tag import Komoran
    print(tr.threshold)
    # tagger = Komoran()
    # stopword = set([('있', 'VV'), ('하', 'VV'), ('되', 'VV') ])
    tr.loadSents(RawSentenceReader(
        'matchingData1.txt'))  # , lambda sent: filter(lambda x:x not in stopword and x[1] in ('NNG', 'NNP', 'VV', 'VA'), tagger.pos(sent)))
    print('Build...')
    tr.build()
    ranks = tr.rank()
    for k in sorted(ranks, key=ranks.get, reverse=True)[:topN]:
        print("\t".join([str(k), str(ranks[k]), str(tr.dictCount[k])]))