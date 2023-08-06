import os
from IPython.display import Image


class BaseIllustrationPandas:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.nomenklatur = Image(f"{here}/assets/nomenklatur.png", width=500)
