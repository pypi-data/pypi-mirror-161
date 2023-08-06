import os
from IPython.display import Image


class BaseDemoTextProc:
    def __init__(self):
        self.text = [
            'Ini adalah pensil, tapi itu adalah pulpen',
            'Itu adalah pensil.',
            'Saya mau beli pulpen.',
            'Saya ada pulpen itu, tapi tidak ada pensil itu.',
            'Saya tidak ada pensil ini',
            'Saya mau beli pulpen dan pensil',
            'Ini adalah pulpen'
        ]


class BaseIllustrationTextProc:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.nomenklatur = Image(f"{here}/assets/nomenklatur.png", width=900)
        self.vocabulary = Image(f"{here}/assets/vocabulary.png", width=900)
        self.structured = Image(f"{here}/assets/structured.png", width=700)
        self.bag_of_words = Image(f"{here}/assets/bow.png", width=900)
        self.inverse_df = Image(f"{here}/assets/inverse_df.png", width=900)
        self.practical_idf = Image(f"{here}/assets/practical_idf.png", width=900)

