import os
from IPython.display import Image


class BaseIllustrationWordVector:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.word2vec = Image(f"{here}/assets/word2vec.png", width=700)
        self.cbow_vs_skipgram = Image(f"{here}/assets/cbow_skipgram.png", width=800)
