import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, ToggleButtons
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

from luwiji.dataset.regression import make_quadratic, make_sine

import os
from IPython.display import Image


class BaseDemoPolyRegression:
    def __init__(self):
        pass

    @staticmethod
    def data():
        X, y = make_quadratic(n_samples=40, random_state=42)
        plt.figure(figsize=(6, 6))
        plt.scatter(X, y, s=10, c='r')


    @staticmethod
    def polynomial_regression():
        def _simul(poly='Poly(1)'):
            poly = int(poly.strip("Poly(")[:-1])
            model = Pipeline([
                ("poly", PolynomialFeatures(poly)),
                ("lr", LinearRegression())
            ])
            model.fit(X, y)

            plt.figure(figsize=(6, 6))
            plt.scatter(X, y, s=10, c='r')
            plt.title(f"R2_train: {model.score(X, y):.3f}", fontsize=14)
            plt.plot(space, model.predict(space), 'k-')
            plt.ylim(0, 20)

        X, y = make_quadratic(n_samples=40, random_state=42)
        space = np.linspace(-1, 6, 100).reshape(-1, 1)
        X = X.reshape(-1, 1)

        interact(_simul, poly=ToggleButtons(options=['Poly(1)', 'Poly(2)', 'Poly(3)', 'Poly(10)', 'Poly(20)'],
                                            description='Model'))


    @staticmethod
    def nonlinear():
        def _simul(poly='Poly(1)', fit_intercept=True, show_test=False):
            poly = int(poly.strip("Poly(")[:-1])
            model = Pipeline([
                ("poly", PolynomialFeatures(poly, include_bias=fit_intercept)),
                ("lr", LinearRegression(fit_intercept=fit_intercept))
            ])
            model.fit(X_train, y_train)

            plt.figure(figsize=(15, 6))

            plt.subplot(121)
            plt.scatter(X_train, y_train, s=10, c='r')
            plt.title(f"R2_train: {model.score(X_train, y_train):.3f}", fontsize=14)
            plt.plot(space, model.predict(space), 'k-')
            plt.xlim(-1, 7)
            plt.ylim(-1.5, 1.5)

            if show_test:
                plt.subplot(122)
                plt.scatter(X_test, y_test, s=10, c='r')
                plt.title(f"R2_test: {model.score(X_test, y_test):.3f}", fontsize=14)
                plt.plot(space, model.predict(space), 'k-')
                plt.xlim(-1, 7)
                plt.ylim(-1.5, 1.5)

        X_train, X_test, y_train, y_test = make_sine(n_samples=50, coef=(0.8, 1), noise=0.2, span=(0, 6), test_size=0.2, random_state=42)
        space = np.linspace(-1, 7, 100).reshape(-1, 1)
        interact(_simul, poly=ToggleButtons(options=['Poly(1)', 'Poly(2)', 'Poly(3)', 'Poly(10)', 'Poly(20)'],
                                            description='Model'))


class BaseIllustrationPolyRegression:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.polynomial_regression = Image(f"{here}/assets/polynomial_regression.png", width=400)
