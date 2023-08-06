import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.neighbors import KNeighborsClassifier
from ipywidgets import interact, ToggleButtons

import os
from IPython.display import Image


class BaseDemoKNN:
    def __init__(self):
        pass

    @staticmethod
    def knn():
        def _simul(N=1, x=-5, y=0, show_decision=False, weight='uniform'):
            X_test = np.array([[x, y]])
            distance = np.linalg.norm(X_data - X_test, axis=1)
            closest = distance.argsort()
            clf = KNeighborsClassifier(n_neighbors=N, weights=weight).fit(X_data, y_data)
            y_pred = clf.predict(X_test)
            y_pred = 'r' if y_pred[0] else 'b'

            plt.figure(figsize=(7, 7))
            plt.xlim(-13, 4)
            plt.ylim(-8, 9)
            for idx in closest[:N]:
                fmt = 'b-' if y_data[idx] == 0 else 'r-'
                w = 2 if weight == 'uniform' else min(3 / distance[idx], 5)
                plt.plot((X_test[0, 0], X_data[idx, 0]), (X_test[0, 1], X_data[idx, 1]), fmt, zorder=-1, linewidth=w)
            plt.scatter(X_data[:, 0], X_data[:, 1], c=y_data, s=100, cmap='bwr', edgecolors='c')
            plt.scatter(X_test[:, 0], X_test[:, 1], c=y_pred, s=100, cmap='bwr', edgecolors='k', marker='D')

            if show_decision:
                xx = np.linspace(-13, 4, 200)
                yy = np.linspace(-8, 9, 200)

                X1, X2 = np.meshgrid(xx, yy)
                X_grid = np.c_[X1.ravel(), X2.ravel()]

                decision = clf.predict_proba(X_grid)[:, 1]
                plt.contourf(X1, X2, decision.reshape(X1.shape), levels=[0, 0.5, 1], alpha=0.3, cmap='bwr', zorder=-2)

        X_data, y_data = make_blobs(n_samples=20, centers=2, cluster_std=3, random_state=1)
        interact(_simul, N=(1, 11, 2), x=(-10, 0, 0.5), y=(-5, 6, 0.5),
                 weight=ToggleButtons(options=['uniform', 'distance'], description='weight'))

    @staticmethod
    def knn_scaling():
        def _simul(N=1, gaji=7e6, n_anak=1):
            X_test = np.array([[gaji, n_anak]])
            distance = np.linalg.norm(X_data - X_test, axis=1)
            closest = distance.argsort()
            clf = KNeighborsClassifier(n_neighbors=N).fit(X_data, y_data)
            y_pred = clf.predict(X_test)
            y_pred = 'r' if y_pred[0] else 'b'

            plt.figure(figsize=(15, 6))
            plt.xlim(0, 20e6)
            plt.ylim(-50, 50)
            plt.xlabel("Gaji", fontsize=12)
            plt.ylabel("Jumlah anak", fontsize=12)
            for idx in closest[:N]:
                fmt = 'b-' if y_data[idx] == 0 else 'r-'
                plt.plot((X_test[0, 0], X_data[idx, 0]), (X_test[0, 1], X_data[idx, 1]), fmt, zorder=-1)
            plt.scatter(X_data[:, 0], X_data[:, 1], c=y_data, s=100, cmap='bwr', edgecolors='c')
            plt.scatter(X_test[:, 0], X_test[:, 1], c=y_pred, s=100, cmap='bwr', edgecolors='k', marker='D')

        X_data, y_data = make_blobs(n_samples=20, centers=2, cluster_std=3, random_state=1)
        X_data[:, 0] = (X_data[:, 0] + 15) * 1e6
        X_data[:, 1] = (X_data[:, 1] + 8) // 4
        interact(_simul, N=(1, 11, 2), gaji=(5e6, 12e6, 1e6), n_anak=(0, 3, 1))


class BaseIllustrationKNN:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.train_test_split = Image(f"{here}/assets/train_test_split.png", width=900)
        self.kfold_cv = Image(f"{here}/assets/kfold.png", width=700)
        self.strat_kfold_cv = Image(f"{here}/assets/strat_kfold.png", width=500)
        self.train_val_test = Image(f"{here}/assets/train_val_test.png", width=900)
        self.nomenklatur = Image(f"{here}/assets/nomenklatur.png", width=400)
        self.knn_scaling = Image(f"{here}/assets/knn_scaling.png", width=900)
        self.knn_distance = Image(f"{here}/assets/knn_distance.png", width=900)
        self.jack_and_rose = Image(f"{here}/assets/jack_and_rose.png", width=1000)
        self.simple_model_advantage = Image(f"{here}/assets/simple_model_advantage.png", width=900)
        self.data_leakage = Image(f"{here}/assets/data_leakage.png", width=800)
