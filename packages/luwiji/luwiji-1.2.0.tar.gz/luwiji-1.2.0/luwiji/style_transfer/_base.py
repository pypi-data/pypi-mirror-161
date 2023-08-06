import os
from IPython.display import Image


class BaseIllustrationStyleTransfer:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.choose_layer1 = Image(f"{here}/assets/choose_layer1.png", width=800)
        self.choose_layer2 = Image(f"{here}/assets/choose_layer2.png", width=800)
        self.result = Image(f"{here}/assets/style_transfer_result.png", width=800)
        self.style_transfer = Image(f"{here}/assets/style_transfer.png", width=900)
        self.vgg16 = Image(f"{here}/assets/vgg16.png", width=600)
        self.vgg16_layers = Image(f"{here}/assets/vgg16_layers.png", width=700)
        self.content_loss = Image(f"{here}/assets/content_loss.png", width=800)
        self.style_loss = Image(f"{here}/assets/style_loss.png", width=800)
        self.total_loss = Image(f"{here}/assets/total_loss.png", width=800)
