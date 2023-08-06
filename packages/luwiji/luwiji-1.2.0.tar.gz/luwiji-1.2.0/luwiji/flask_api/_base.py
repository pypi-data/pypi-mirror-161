import os
from IPython.display import Image


class BaseIllustrationFlaskAPI:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.get_vs_post = Image(f"{here}/assets/get_vs_post.png", width=650)
        self.internet = Image(f"{here}/assets/internet.png", width=700)
        self.http = Image(f"{here}/assets/http.png", width=850)
