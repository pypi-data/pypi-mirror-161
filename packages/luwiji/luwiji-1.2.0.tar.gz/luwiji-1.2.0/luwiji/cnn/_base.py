import os
from IPython.display import Image
from PIL.Image import open


class BaseIllustrationCNN:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.combination = Image(f"{here}/assets/combination.png", width=300)
        self.conv_ex1 = Image(f"{here}/assets/conv_ex1.png", width=300)
        self.conv_ex2 = Image(f"{here}/assets/conv_ex2.jpg", width=400)
        self.conv_ex3 = Image(f"{here}/assets/conv_ex3.gif")
        self.conv_ex4 = Image(f"{here}/assets/conv_ex4.gif")
        self.fully_con = Image(f"{here}/assets/fully_con.png", width=600)
        self.goal = Image(f"{here}/assets/goal.png", width=800)
        self.padding = Image(f"{here}/assets/padding.png", width=600)
        self.padding_same = Image(f"{here}/assets/padding_same.png", width=600)
        self.partial_con = Image(f"{here}/assets/partial_con.png", width=600)
        self.pooling = Image(f"{here}/assets/pooling.jpg", width=600)
        self.stride = Image(f"{here}/assets/stride.png", width=800)
        self.translation = Image(f"{here}/assets/translation_invariance.png", width=800)
        self.nn_vs_cnn = Image(f"{here}/assets/nn_vs_cnn.png", width=900)
        self.blur_avg = Image(f"{here}/assets/blur_avg.png", width=800)

        self.img = open(f"{here}/assets/flower.png")
