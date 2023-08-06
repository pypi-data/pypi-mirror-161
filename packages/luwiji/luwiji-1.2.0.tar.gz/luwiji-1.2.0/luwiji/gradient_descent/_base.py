import os
from IPython.display import Image


class BaseIllustrationGradDescent:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.minima = Image(f"{here}/assets/minima.png", width=600)
        self.narrow = Image(f"{here}/assets/narrow.gif", width=600)
        self.plateau = Image(f"{here}/assets/plateau.png", width=600)
        self.saddle = Image(f"{here}/assets/saddle.png", width=800)
