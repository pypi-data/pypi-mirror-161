import os
from IPython.display import Image


class BaseIllustrationAutoencoder:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.denoise_document = Image(f"{here}/assets/denoise_document.png", width=900)
        self.denoise_document_train = Image(f"{here}/assets/denoise_document_train.png", width=900)
        self.play_card = Image(f"{here}/assets/play_card.png", width=600)
        self.conv_ae = Image(f"{here}/assets/conv_ae.png", width=800)
