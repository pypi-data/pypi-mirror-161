import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import make_moons

import os
from IPython.display import Image


class AdaptiveBoosting():
    def __init__(self, n_iter, lr, tree_max_depth=1):
        self.n_estimator = n_iter
        self.lr = lr
        self.max_depth = tree_max_depth
        self.estimators_ = []
        self.estimator_weights_ = []
        self.sample_weights_ = []

    def fit(self, X, y):
        N = len(y)
        w = np.ones(N) / N
        self.sample_weights_.append(w.copy().tolist())

        for i in range(self.n_estimator):
            dt = DecisionTreeClassifier(max_depth=self.max_depth)
            dt.fit(X, y, sample_weight=w)
            incorrect = (dt.predict(X) != y)

            e_t = w[incorrect].sum() + 1e-6
            alpha = self.lr * np.log((1 - e_t) / e_t)

            w[incorrect] *= ((1 - e_t) / e_t) ** self.lr
            w /= w.sum()

            self.estimators_.append(dt)
            self.estimator_weights_.append(alpha)
            self.sample_weights_.append(w.copy().tolist())
        self.sample_weights_ = np.array(self.sample_weights_)

    def predict(self, X, iteration=None):
        if iteration is not None:
            if iteration > self.n_estimator:
                raise Exception(f"Iteration cannot be more than n_iter={self.n_estimator}")
            pred = [model.predict(X) for model in self.estimators_[:iteration]]
            return np.sign(self.estimator_weights_[:iteration] @ np.array(pred))
        else:
            pred = [model.predict(X) for model in self.estimators_]
            return np.sign(self.estimator_weights_ @ np.array(pred))

    def score(self, X, y):
        pred = self.predict(X)
        return np.mean(pred == y)


class BaseDemoBoosting:
    def __init__(self):
        X, y = make_moons(n_samples=500, noise=0.05, random_state=42)
        y[y < 1] = -1

        xx = np.linspace(1.05 * X[:, 0].min(), 1.05 * X[:, 0].max(), 100)
        yy = np.linspace(1.05 * X[:, 1].min(), 1.05 * X[:, 1].max(), 100)

        X1, X2 = np.meshgrid(xx, yy)

        self._X, self._y = X, y
        self._X_grid = np.c_[X1.ravel(), X2.ravel()]
        self._X1, self._X2 = X1, X2

    def adaboost(self):
        def _simul(iteration=1):
            plt.figure(figsize=(11, 5))
            Z = model.estimators_[iteration-1].predict(self._X_grid)
            Z = Z.reshape(self._X1.shape)

            plt.subplot(121)
            multiplier = 100 ** (2 / 3) / max(model.sample_weights_[iteration-1])
            size = (model.sample_weights_[iteration-1] * multiplier) ** 1.5
            plt.scatter(self._X[:, 0], self._X[:, 1], c=self._y, s=size, cmap='bwr')
            plt.contourf(self._X1, self._X2, Z, levels=[-1, 0, 1], alpha=0.8, cmap='bwr', zorder=-2)
            plt.title(f"Classifier iter: {iteration}")

            plt.subplot(122)
            multiplier = 100 ** (2 / 3) / max(model.sample_weights_[iteration])
            size = (model.sample_weights_[iteration] * multiplier) ** 1.5
            plt.scatter(self._X[:, 0], self._X[:, 1], c=self._y, s=size, cmap='bwr')
            plt.title(f"Sample weight for next iteration")

        model = AdaptiveBoosting(n_iter=5, lr=1.5)
        model.fit(self._X, self._y)
        interact(_simul, iteration=(1, model.n_estimator, 1))

    def adaboost_prediction(self):
        def _simul(iteration=1):
            plt.figure(figsize=(10, 8))
            grid = plt.GridSpec(4, 5, wspace=0.3, hspace=0.3)

            for i in range(iteration):
                plt.subplot(grid[0, i])
                Z = model.estimators_[i].predict(self._X_grid)
                Z = Z.reshape(self._X1.shape)
                plt.contourf(self._X1, self._X2, Z, levels=[-1, 0, 1], cmap='bwr', zorder=-2)
                plt.text(np.mean(plt.xlim()), np.mean(plt.ylim()), f"{model.estimator_weights_[i]:.2f}",
                         ha='center', va='center', fontsize=30)
                plt.xticks([])
                plt.yticks([])

            plt.subplot(grid[1:4, 1:4])
            Z = model.predict(self._X_grid, iteration)
            Z = Z.reshape(self._X1.shape)
            plt.scatter(self._X[:, 0], self._X[:, 1], c=self._y, s=5, cmap='bwr')
            plt.contourf(self._X1, self._X2, Z, levels=[-1, 0, 1], alpha=0.8, cmap='bwr', zorder=-2);

        model = AdaptiveBoosting(n_iter=5, lr=1.5)
        model.fit(self._X, self._y)
        interact(_simul, iteration=(1, model.n_estimator, 1))

    def max_depth(self, n_maks=10):
        def _simul(iteration=1, max_depth=1):
            model = AdaptiveBoosting(n_iter=n_maks, lr=1.5, tree_max_depth=max_depth)
            model.fit(self._X, self._y)
            plt.figure(figsize=(10, 10))
            grid = plt.GridSpec(5, 5, wspace=0.3, hspace=0.3)

            for i in range(iteration):
                row = i // 5
                col = i % 5
                plt.subplot(grid[row, col])
                Z = model.estimators_[i].predict(self._X_grid)
                Z = Z.reshape(self._X1.shape)
                plt.contourf(self._X1, self._X2, Z, levels=[-1, 0, 1], cmap='bwr', zorder=-2)
                plt.text(np.mean(plt.xlim()), np.mean(plt.ylim()), f"{model.estimator_weights_[i]:.2f}",
                         ha='center', va='center', fontsize=30)
                plt.xticks([])
                plt.yticks([])

            pad = (iteration - 1) // 5
            plt.subplot(grid[1+pad:4+pad, 1:4])
            Z = model.predict(self._X_grid, iteration)
            Z = Z.reshape(self._X1.shape)
            plt.scatter(self._X[:, 0], self._X[:, 1], c=self._y, s=5, cmap='bwr')
            plt.contourf(self._X1, self._X2, Z, levels=[-1, 0, 1], alpha=0.8, cmap='bwr', zorder=-2);

        interact(_simul, max_depth=(1, 3, 1), iteration=(1, n_maks, 1))

    def learning_rate(self, n_maks=10):
        def _simul(iteration=1, lr=1):
            model = AdaptiveBoosting(n_iter=n_maks, lr=lr)
            model.fit(self._X, self._y)
            plt.figure(figsize=(10, 10))
            grid = plt.GridSpec(5, 5, wspace=0.3, hspace=0.3)

            for i in range(iteration):
                row = i // 5
                col = i % 5
                plt.subplot(grid[row, col])
                Z = model.estimators_[i].predict(self._X_grid)
                Z = Z.reshape(self._X1.shape)
                plt.contourf(self._X1, self._X2, Z, levels=[-1, 0, 1], cmap='bwr', zorder=-2)
                plt.text(np.mean(plt.xlim()), np.mean(plt.ylim()), f"{model.estimator_weights_[i]:.2f}",
                         ha='center', va='center', fontsize=30)
                plt.xticks([])
                plt.yticks([])

            pad = (iteration - 1) // 5
            plt.subplot(grid[1+pad:4+pad, 1:4])
            Z = model.predict(self._X_grid, iteration)
            Z = Z.reshape(self._X1.shape)
            plt.scatter(self._X[:, 0], self._X[:, 1], c=self._y, s=5, cmap='bwr')
            plt.contourf(self._X1, self._X2, Z, levels=[-1, 0, 1], alpha=0.8, cmap='bwr', zorder=-2);

        interact(_simul, lr=(0, 2, 0.5), iteration=(1, n_maks, 1))

    def max_depth_and_lr(self, n_maks=10):
        def _simul(iteration=1, lr=1, max_depth=1):
            model = AdaptiveBoosting(n_iter=n_maks, lr=lr, tree_max_depth=max_depth)
            model.fit(self._X, self._y)
            plt.figure(figsize=(10, 10))
            grid = plt.GridSpec(5, 5, wspace=0.3, hspace=0.3)

            for i in range(iteration):
                row = i // 5
                col = i % 5
                plt.subplot(grid[row, col])
                Z = model.estimators_[i].predict(self._X_grid)
                Z = Z.reshape(self._X1.shape)
                plt.contourf(self._X1, self._X2, Z, levels=[-1, 0, 1], cmap='bwr', zorder=-2)
                plt.text(np.mean(plt.xlim()), np.mean(plt.ylim()), f"{model.estimator_weights_[i]:.2f}",
                         ha='center', va='center', fontsize=30)
                plt.xticks([])
                plt.yticks([])

            pad = (iteration - 1) // 5
            plt.subplot(grid[1+pad:4+pad, 1:4])
            Z = model.predict(self._X_grid, iteration)
            Z = Z.reshape(self._X1.shape)
            plt.scatter(self._X[:, 0], self._X[:, 1], c=self._y, s=5, cmap='bwr')
            plt.contourf(self._X1, self._X2, Z, levels=[-1, 0, 1], alpha=0.8, cmap='bwr', zorder=-2);

        interact(_simul, lr=(0, 2, 0.5), max_depth=(1, 3, 1), iteration=(1, n_maks, 1))


class BaseIllustrationBoosting:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.algoritma = Image(f"{here}/assets/algoritma.png", width=750)
