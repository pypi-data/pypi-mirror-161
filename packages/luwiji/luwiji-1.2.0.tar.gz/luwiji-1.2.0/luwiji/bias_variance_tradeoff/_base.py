import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.neighbors import KNeighborsClassifier
from ipywidgets import interact, FloatLogSlider
from sklearn.svm import SVC

import os
from IPython.display import Image


class BaseDemoBVTrade:
    def __init__(self):
        pass

    @staticmethod
    def knn():
        def _simul(N=1):
            model = KNeighborsClassifier(n_neighbors=N, weights='uniform').fit(X_data, y_data)

            plt.figure(figsize=(6, 6))
            plt.xlim(-12, 12)
            plt.ylim(-6, 18)
            plt.scatter(X_data[:, 0], X_data[:, 1], c=y_data, s=100, cmap='bwr', edgecolors='c')

            xx = np.linspace(-12, 12, 200)
            yy = np.linspace(-6, 18, 200)

            X1, X2 = np.meshgrid(xx, yy)
            X_grid = np.c_[X1.ravel(), X2.ravel()]

            decision = model.predict_proba(X_grid)[:, 1]
            plt.contourf(X1, X2, decision.reshape(X1.shape), levels=[0, 0.5, 1], alpha=0.3, cmap='bwr', zorder=-2)

        X_data, y_data = make_blobs(n_samples=100, centers=2, cluster_std=3, random_state=42)
        interact(_simul, N=(1, 50, 2))


    @staticmethod
    def svm_c():
        def _simul(C=0.01):
            model = SVC(kernel='rbf', C=C, gamma=0.01, probability=True).fit(X_data, y_data)

            plt.figure(figsize=(6, 6))
            plt.xlim(-12, 12)
            plt.ylim(-6, 18)
            plt.scatter(X_data[:, 0], X_data[:, 1], c=y_data, s=100, cmap='bwr', edgecolors='c')

            xx = np.linspace(-12, 12, 200)
            yy = np.linspace(-6, 18, 200)

            X1, X2 = np.meshgrid(xx, yy)
            X_grid = np.c_[X1.ravel(), X2.ravel()]

            decision = model.predict_proba(X_grid)[:, 1]
            plt.contourf(X1, X2, decision.reshape(X1.shape), levels=[0, 0.5, 1], alpha=0.3, cmap='bwr', zorder=-2)
        X_data, y_data = make_blobs(n_samples=100, centers=2, cluster_std=3, random_state=42)
        interact(_simul, C=FloatLogSlider(value=0.01, base=10, min=-1, max=3, step=0.25, description='C'))


    @staticmethod
    def svm_gamma():
        def _simul(gamma=0.001):
            model = SVC(kernel='rbf', C=0.1, gamma=gamma, probability=True).fit(X_data, y_data)

            plt.figure(figsize=(6, 6))
            plt.xlim(-12, 12)
            plt.ylim(-6, 18)
            plt.scatter(X_data[:, 0], X_data[:, 1], c=y_data, s=100, cmap='bwr', edgecolors='c')

            xx = np.linspace(-12, 12, 200)
            yy = np.linspace(-6, 18, 200)

            X1, X2 = np.meshgrid(xx, yy)
            X_grid = np.c_[X1.ravel(), X2.ravel()]

            decision = model.predict_proba(X_grid)[:, 1]
            plt.contourf(X1, X2, decision.reshape(X1.shape), levels=[0, 0.5, 1], alpha=0.3, cmap='bwr', zorder=-2)
        X_data, y_data = make_blobs(n_samples=100, centers=2, cluster_std=3, random_state=42)
        interact(_simul, gamma=FloatLogSlider(value=0.001, base=10, min=-3, max=-0.5, step=0.25, description='gamma'))


    @staticmethod
    def svm_kernel():
        X_data, y_data = make_blobs(n_samples=100, centers=2, cluster_std=3, random_state=42)

        xx = np.linspace(-12, 12, 200)
        yy = np.linspace(-6, 18, 200)

        X1, X2 = np.meshgrid(xx, yy)
        X_grid = np.c_[X1.ravel(), X2.ravel()]

        model_rbf = SVC(kernel='rbf', C=0.1, gamma=0.1, probability=True).fit(X_data, y_data)
        decision_rbf = model_rbf.predict_proba(X_grid)[:, 1]

        model_linear = SVC(kernel='linear', C=0.1, probability=True).fit(X_data, y_data)
        decision_linear = model_linear.predict_proba(X_grid)[:, 1]

        plt.figure(figsize=(13, 6))
        plt.subplot(121)
        plt.scatter(X_data[:, 0], X_data[:, 1], c=y_data, s=100, cmap='bwr', edgecolors='c')
        plt.contourf(X1, X2, decision_rbf.reshape(X1.shape), levels=[0, 0.5, 1], alpha=0.3, cmap='bwr', zorder=-2)
        plt.xlim(-12, 12)
        plt.ylim(-6, 18)
        plt.title("Kernel = RBF", fontsize=14)

        plt.subplot(122)
        plt.scatter(X_data[:, 0], X_data[:, 1], c=y_data, s=100, cmap='bwr', edgecolors='c')
        plt.contourf(X1, X2, decision_linear.reshape(X1.shape), levels=[0, 0.5, 1], alpha=0.3, cmap='bwr', zorder=-2)
        plt.xlim(-12, 12)
        plt.ylim(-6, 18)
        plt.title("Kernel = linear", fontsize=14)


class BaseIllustrationBVTrade:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.bias_variance_tradeoff = Image(f"{here}/assets/bias_var_tradeoff.png", width=800)
        self.just_right = Image(f"{here}/assets/just_right.png", width=800)
