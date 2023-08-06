import os
from IPython.display import Image
from sklearn.datasets.samples_generator import make_blobs, make_circles, make_moons


class BaseIllustrationCluster:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.ahc = Image(f"{here}/assets/ahc.png", width=800)
        self.dendrogram = Image(f"{here}/assets/dendrogram.png", width=600)
        self.cluster_distance = Image(f"{here}/assets/cluster_distance.png", width=800)


class BaseDemoCluster:
    def __init__(self):
        pass

    @staticmethod
    def blob_data(n=400):
        return make_blobs(n_samples=n, centers=4, cluster_std=0.5, random_state=42)

    @staticmethod
    def moon_data(n=400):
        return make_moons(n_samples=n, noise=0.1, random_state=42)

    @staticmethod
    def circle_data(n=400):
        return make_circles(n_samples=n, noise=0.1, random_state=42, factor=0.3)
