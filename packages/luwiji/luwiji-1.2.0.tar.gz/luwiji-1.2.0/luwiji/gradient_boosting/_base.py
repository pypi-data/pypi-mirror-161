import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact
from sklearn.tree import DecisionTreeRegressor


import os
from IPython.display import Image


class GradientBoosting:
    def __init__(self, n_iter, lr, tree_max_depth=1):
        self.n_estimator = n_iter
        self.lr = lr
        self.max_depth = tree_max_depth
        self.estimators_ = []
        self.residuals_ = []

    def fit(self, X, y):
        self._mean = y.mean()
        fit_err = self._mean * np.ones_like(y)
        err = y - fit_err
        self.residuals_.append(err)

        for i in range(self.n_estimator):
            dt = DecisionTreeRegressor(max_depth=self.max_depth, random_state=42)
            dt.fit(X, err)

            fit_err += self.lr * dt.predict(X)
            err = y - fit_err

            self.estimators_.append(dt)
            self.residuals_.append(err)

    def predict(self, X, iteration=None):
        result = self._mean * np.ones_like(X.ravel())
        if iteration is not None:
            if iteration > self.n_estimator:
                raise Exception(f"Input iterasi melebihi n_iter={self.n_estimator}")
            for tree in self.estimators_[:iteration]:
                result += self.lr * tree.predict(X)
            return result
        else:
            for tree in self.estimators_:
                result += self.lr * tree.predict(X)
            return result

    def fit_residual(self, X, iteration):
        return self.lr * self.estimators_[iteration].predict(X)


class BaseDemoGradBoost:
    def __init__(self):
        np.random.seed(42)
        self._X = np.linspace(0, 5, 30)
        self._y = 0.9 * self._X ** 2 + 3 * self._X + 10 * np.random.rand(len(self._X))
        self._space = np.linspace(0, 5, 250).reshape(-1, 1)
        self._X = self._X.reshape(-1, 1)

    def gradient_boosting(self):
        def _simul(iterasi=0):
            plt.figure(figsize=(16, 5))

            plt.subplot(131)
            plt.scatter(self._X.ravel(), self._y, s=10, c='b')
            plt.plot(self._space, model.predict(self._space, iterasi), 'r-')
            plt.title("Ensemble Prediction")

            plt.subplot(132)
            plt.scatter(self._X.ravel(), model.residuals_[iterasi], s=10, c='k')
            plt.axhline(color='k', linewidth=1)
            plt.ylim(-25, 25)
            plt.title(f"Residual (R{iterasi+1})")

            plt.subplot(133)
            plt.scatter(self._X.ravel(), model.residuals_[iterasi], s=10, c='k')
            plt.plot(self._space, model.fit_residual(self._space, iterasi), 'r-')
            plt.axhline(color='k', linewidth=1)
            plt.ylim(-25, 25)
            plt.title(f"Fitted Residual (P{iterasi+1})")

        model = GradientBoosting(10, 1)
        model.fit(self._X, self._y)
        interact(_simul, iterasi=(0, model.n_estimator - 1, 1))

    def max_depth(self):
        def _simul(max_depth=1, iterasi=0):
            model = GradientBoosting(15, lr=1, tree_max_depth=max_depth)
            model.fit(self._X, self._y)

            plt.figure(figsize=(16, 5))

            plt.subplot(131)
            plt.scatter(self._X.ravel(), self._y, s=10, c='b')
            plt.plot(self._space, model.predict(self._space, iterasi), 'r-')
            plt.title("Ensemble Prediction")

            plt.subplot(132)
            plt.scatter(self._X.ravel(), model.residuals_[iterasi], s=10, c='k')
            plt.axhline(color='k', linewidth=1)
            plt.ylim(-25, 25)
            plt.title(f"Residual (R{iterasi+1})")

            plt.subplot(133)
            plt.scatter(self._X.ravel(), model.residuals_[iterasi], s=10, c='k')
            plt.plot(self._space, model.fit_residual(self._space, iterasi), 'r-')
            plt.axhline(color='k', linewidth=1)
            plt.ylim(-25, 25)
            plt.title(f"Fitted Residual (P{iterasi+1})")
        interact(_simul, max_depth=(1, 3, 1), iterasi=(0, 14, 1))

    def learning_rate(self):
        def _simul(lr=1, iterasi=0):
            model = GradientBoosting(5, lr=lr)
            model.fit(self._X, self._y)

            plt.figure(figsize=(16, 5))

            plt.subplot(131)
            plt.scatter(self._X.ravel(), self._y, s=10, c='b')
            plt.plot(self._space, model.predict(self._space, iterasi), 'r-')
            plt.title("Ensemble Prediction")

            plt.subplot(132)
            plt.scatter(self._X.ravel(), model.residuals_[iterasi], s=10, c='k')
            plt.axhline(color='k', linewidth=1)
            plt.ylim(-25, 25)
            plt.title(f"Residual (R{iterasi+1})")

            plt.subplot(133)
            plt.scatter(self._X.ravel(), model.residuals_[iterasi], s=10, c='k')
            plt.plot(self._space, model.fit_residual(self._space, iterasi), 'r-')
            plt.axhline(color='k', linewidth=1)
            plt.ylim(-25, 25)
            plt.title(f"Fitted Residual (P{iterasi+1})")
        interact(_simul, lr=(0, 2, 0.5), iterasi=(0, 4, 1))

    def max_depth_and_lr(self):
        def _simul(lr=0.5, max_depth=1, iterasi=0):
            model = GradientBoosting(5, lr=lr, tree_max_depth=max_depth)
            model.fit(self._X, self._y)

            plt.figure(figsize=(16, 5))

            plt.subplot(131)
            plt.scatter(self._X.ravel(), self._y, s=10, c='b')
            plt.plot(self._space, model.predict(self._space, iterasi), 'r-')
            plt.title("Ensemble Prediction")

            plt.subplot(132)
            plt.scatter(self._X.ravel(), model.residuals_[iterasi], s=10, c='k')
            plt.axhline(color='k', linewidth=1)
            plt.ylim(-25, 25)
            plt.title(f"Residual (R{iterasi+1})")

            plt.subplot(133)
            plt.scatter(self._X.ravel(), model.residuals_[iterasi], s=10, c='k')
            plt.plot(self._space, model.fit_residual(self._space, iterasi), 'r-')
            plt.axhline(color='k', linewidth=1)
            plt.ylim(-25, 25)
            plt.title(f"Fitted Residual (P{iterasi+1})")

        model = GradientBoosting(10, 1)
        model.fit(self._X, self._y)
        interact(_simul, lr=(0.1, 0.5, 0.1), max_depth=(1, 3, 1), iterasi=(0, 4, 1))


class BaseIllustrationGradBoost:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.golf = Image(f"{here}/assets/golf_boosting.png", width=900)
        self.algoritma = Image(f"{here}/assets/algoritma.png", width=900)
