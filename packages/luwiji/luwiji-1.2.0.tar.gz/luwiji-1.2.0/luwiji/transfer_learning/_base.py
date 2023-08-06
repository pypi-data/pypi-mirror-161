import os
from IPython.display import Image


class BaseIllustrationTransferLearning:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.human_error_1 = Image(f"{here}/assets/cool1.png")
        self.human_error_2 = Image(f"{here}/assets/cool3.png")
        self.human_error_3 = Image(f"{here}/assets/cool2.png")

        self.googlenet_architecture = Image(f"{here}/assets/googlenet_architecture.png", width=800)
        self.inceptionv3_architecture = Image(f"{here}/assets/inceptionv3_architecture.png", width=800)
        self.inception_module = Image(f"{here}/assets/inception_module.png", width=800)
        self.go_deeper = Image(f"{here}/assets/go_deeper.jpg")

        self.resnet34_architecture = Image(f"{here}/assets/resnet34_architecture.png", width=200)
        self.residual_block = Image(f"{here}/assets/residual_block.png", width=300)
        self.resnet_loss_landscape = Image(f"{here}/assets/resnet_loss_landscape.png", width=600)

        self.other_cnn = Image(f"{here}/assets/other_cnn.jpeg", width=600)

        self.vgg16 = Image(f"{here}/assets/vgg16.png", width=200)
        self.vgg16_architecture = Image(f"{here}/assets/vgg16_architecture.png", width=800)

        self.transfer_learning_matrix = Image(f"{here}/assets/transfer_learning_matrix.png", width=600)

        self.mislabeled = Image(f"{here}/assets/mislabeled.png", width=800)
        self.comparison = Image(f"{here}/assets/transfer_learning_comparison.png", width=800)
