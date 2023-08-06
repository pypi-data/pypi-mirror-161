import os
from IPython.display import Image


class BaseIllustrationXGBoost:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.nomenklatur = Image(f"{here}/assets/nomenklatur.png", width=600)
