import os
from IPython.display import Image


class BaseIllustrationEnsemble:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.ensemble = Image(f"{here}/assets/ensemble_learning.png", width=900)
        self.bagging= Image(f"{here}/assets/bagging.png", width=700)
        self.boosting = Image(f"{here}/assets/boosting.png", width=700)
