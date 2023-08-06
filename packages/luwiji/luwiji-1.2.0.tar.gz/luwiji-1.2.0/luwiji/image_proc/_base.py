import matplotlib.pyplot as plt
from ipywidgets import interact, ToggleButtons

import os
from IPython.display import Image


class BaseDemoImgProc:
    def __init__(self):
        self.here = os.path.dirname(__file__)

    def grayscale_image(self):
        def _simul(mode="0 - 255"):
            plt.figure(figsize=(8, 8))
            plt.imshow(image, cmap='gray')

            img = (image * 255).astype(int) if mode == "0 - 255" else image
            th = 128 if mode == "0 - 255" else 0.5

            for i in range(15):
                for j in range(15):
                    z = img[j, i]
                    c = 'k' if z > th else 'w'
                    if mode == "0 - 255":
                        plt.text(i, j, z, ha='center', va='center', fontdict={'color': c, 'size': 10})
                    else:
                        plt.text(i, j, f"{z:.1f}", ha='center', va='center', fontdict={'color': c, 'size': 10})
            plt.title(mode, fontsize=14)
            plt.axis('off');

        image = plt.imread(f"{self.here}/assets/zero.png")
        interact(_simul, mode=ToggleButtons(value="0 - 255", options=["0 - 255", "0.0 - 1.0"], description="pixel value"))


class BaseIllustrationImgProc:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.rgb_display = Image(f"{here}/assets/rgb_display.png", width=500)
        self.rgb_image = Image(f"{here}/assets/rgb_image.png", width=900)
        self.flattening = Image(f"{here}/assets/flatten.png", width=900)
        self.structured = Image(f"{here}/assets/structured.png", width=700)
        self.interpolation = Image(f"{here}/assets/interpolation.png", width=700)
        self.clipping_mask = Image(f"{here}/assets/clipping_mask.png", width=900)
