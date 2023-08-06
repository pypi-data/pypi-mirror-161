import os
import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact
from IPython.display import Image


class BaseIllustrationDimensionalityReduction:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.dimensi_beras = Image(f"{here}/assets/dimensi_beras.png", width=700)
        self.dimensionality_reduction = Image(f"{here}/assets/dimensionality_reduction.png", width=800)
        self.pca_combination = Image(f"{here}/assets/pca_combination.png", width=900)
        self.tsne_1 = Image(f"{here}/assets/tsne_1.png", width=900)
        self.tsne_2 = Image(f"{here}/assets/tsne_2.png", width=900)
        self.tsne_3 = Image(f"{here}/assets/tsne_3.png", width=900)
        self.tsne_4 = Image(f"{here}/assets/tsne_4.png", width=900)


class BaseDemoDimensionalityReduction:
    def __init__(self):
        pass

    def pca(self, random_state=42):
        def _simul(m=0, show_answer=False):
            if show_answer:
                m = 0.5

            # Linear
            a = np.array([-10, 10])
            y = a * m

            # Projection
            theta = np.arctan(m)
            u = np.array([[np.cos(theta), np.sin(theta)]])
            projected = X @ u.T @ u

            # Visualize
            plt.figure(figsize=(13, 6))

            plt.subplot(121)
            plt.plot(a, y, 'g-')
            plt.scatter(X[:, 0], X[:, 1], s=20, c='b')
            for (x1, y1), (x2, y2), in zip(X, projected):
                plt.plot([x1, x2], [y1, y2], 'r--', linewidth=1)
            plt.axis('equal')
            plt.xlim(-5, 5)
            plt.ylim(-3.5, 3.5)
            plt.title("sebelum reduksi", fontsize=14)

            plt.subplot(122)
            r = X @ u.T
            plt.scatter(r, np.zeros_like(r), s=20, c='b')
            plt.axis('equal')
            plt.xlim(-5, 5)
            plt.yticks([])
            plt.title("setelah reduksi", fontsize=14)

        X = self.load_sample_data(random_state)
        interact(_simul, m=(-2.5, 2.5, 0.25));

    @staticmethod
    def load_sample_data(random_state=42):
        state = np.random.RandomState(random_state)
        return state.multivariate_normal([0, 0], [[3, 1.5], [1.5, 1]], size=50)
