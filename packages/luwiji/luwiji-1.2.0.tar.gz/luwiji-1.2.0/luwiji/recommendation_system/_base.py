import os
from IPython.display import Image


class BaseIllustrationRecommendationSystem:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.content_based = Image(f"{here}/assets/content-based-filtering.png", width=900)
        self.collaborative = Image(f"{here}/assets/collaborative-filtering.png", width=900)
        self.svd = Image(f"{here}/assets/svd.png", width=900)
