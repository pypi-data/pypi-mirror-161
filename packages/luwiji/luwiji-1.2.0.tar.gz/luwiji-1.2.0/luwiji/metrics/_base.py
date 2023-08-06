import os
from IPython.display import Image


class BaseIllustrationMetrics:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.sklearn_scoring = Image(f"{here}/assets/sklearn_scoring.png", width=800)
        self.type_of_mistake = Image(f"{here}/assets/fp_fn.png", width=800)
