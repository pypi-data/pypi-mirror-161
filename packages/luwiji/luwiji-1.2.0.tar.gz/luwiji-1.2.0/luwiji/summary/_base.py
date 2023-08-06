import os
from IPython.display import Image


class BaseIllustrationSummary:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.machine_learning = Image(f"{here}/assets/machine_learning.png", width=900)
        self.metrics_evaluation = Image(f"{here}/assets/metrics_evaluation.png", width=900)
