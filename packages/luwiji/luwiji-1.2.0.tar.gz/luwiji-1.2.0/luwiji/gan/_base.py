import os
from IPython.display import Image


class BaseIllustrationGAN:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.generative = Image(f"{here}/assets/generative.png", width=600)
        self.najwa = Image(f"{here}/assets/najwa.png", width=400)
        self.gan = Image(f"{here}/assets/gan.png", width=800)
        self.cgan = Image(f"{here}/assets/cgan.png", width=800)
        self.train_D = Image(f"{here}/assets/train_D.png", width=800)
        self.train_G = Image(f"{here}/assets/train_G.png", width=800)
        self.cyclegan_result = Image(f"{here}/assets/cyclegan.png", width=900)
        self.cyclegan = Image(f"{here}/assets/cyclegan2.png", width=600)
        self.pix2pix = Image(f"{here}/assets/pix2pix.png", width=700)
        self.progan = Image(f"{here}/assets/progan.png", width=800)
        self.progan_result = Image(f"{here}/assets/progan2.png", width=850)
        self.srgan = Image(f"{here}/assets/srgan.png", width=850)
        self.singan = Image(f"{here}/assets/singan.png", width=950)
