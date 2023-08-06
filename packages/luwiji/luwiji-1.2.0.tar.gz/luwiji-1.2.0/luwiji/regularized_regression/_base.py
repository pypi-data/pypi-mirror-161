import warnings

import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, ToggleButtons
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

from luwiji.dataset.regression import make_sine

import os
from IPython.display import Image


class BaseDemoRegularization:
    def __init__(self):
        X_train, X_test, y_train, y_test = make_sine(n_samples=30, noise=0.2, test_size=0.3, span=(3, 9),
                                                     random_state=42)
        self._X_train = X_train
        self._X_test= X_test
        self._y_train = y_train
        self._y_test= y_test
        self._space = np.linspace(2.5, 9.5, 100).reshape(-1, 1)

    def ridge_lasso(self):
        def _simul_reg(regularization='L1 / LASSO / Sparsity'):
            def _simul(degree=1, alpha=0, show_coef=False):
                model_no = Pipeline([
                    ("poly", PolynomialFeatures(degree)),
                    ("lr", LinearRegression())
                ])

                if alpha == 0:
                    model_reg = Pipeline([
                        ("poly", PolynomialFeatures(degree)),
                        ("lr", LinearRegression())
                    ])
                elif reg == 'L1':
                    model_reg = Pipeline([
                        ("poly", PolynomialFeatures(degree)),
                        ("lr", Lasso(alpha=alpha, max_iter=5000, tol=1e-8))
                    ])
                elif reg == 'L2':
                    model_reg = Pipeline([
                        ("poly", PolynomialFeatures(degree)),
                        ("lr", Ridge(alpha=alpha, max_iter=5000, tol=1e-8))
                    ])

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model_no.fit(self._X_train, self._y_train)
                    model_reg.fit(self._X_train, self._y_train)

                if show_coef:
                    plt.figure(figsize=(15, 10))
                    models = [model_no, model_reg]
                    titles = ['Linear Regression', f'{regularization.split(" / ")[1]} Regression']
                    for i, (model, title) in enumerate(zip(models, titles)):
                        name = model.named_steps['poly'].get_feature_names_out(["x"])
                        coef = model.named_steps['lr'].coef_

                        plt.subplot(2, 1, i+1)
                        plt.bar(range(len(coef)), coef, color='b')
                        plt.xticks(range(len(coef)), name)
                        plt.title(title, fontsize=12);

                        if alpha != 0:
                            ymin, ymax = plt.ylim()
                            ylim = max(abs(ymin), abs(ymax))
                            plt.ylim(-ylim, ylim)
                else:
                    plt.figure(figsize=(12, 6))

                    plt.subplot(121)
                    plt.title(f"Without Regularization\nR2_train: {model_no.score(self._X_train, self._y_train):.2f} | "
                              f"R2_test: {model_no.score(self._X_test, self._y_test):.2f}", fontsize=12)
                    plt.scatter(self._X_train, self._y_train, c="b", s=10)
                    plt.scatter(self._X_test, self._y_test, c="r", marker="x", s=10)
                    plt.plot(self._space, model_no.predict(self._space), "k--", linewidth=1);
                    plt.xlim(2.5, 9.5)
                    plt.ylim(-1.5, 1.5)

                    plt.subplot(122)
                    plt.title(f"With Regularization\nR2_train: {model_reg.score(self._X_train, self._y_train):.2f} | "
                              f"R2_test: {model_reg.score(self._X_test, self._y_test):.2f}", fontsize=12)
                    plt.scatter(self._X_train, self._y_train, c="b", s=10)
                    plt.scatter(self._X_test, self._y_test, c="r", marker="x", s=10)
                    plt.plot(self._space, model_reg.predict(self._space), "k--", linewidth=1);
                    plt.xlim(2.5, 9.5)
                    plt.ylim(-1.5, 1.5)

            reg = regularization[:2]
            interact(_simul, degree=(1, 12, 1), alpha=ToggleButtons(description='alpha',
                                                                    options=[0, 0.001, 0.1, 10, 10000]))
        interact(_simul_reg, regularization=ToggleButtons(description='regularization',
                                                          options=['L1 / LASSO / Sparsity', 'L2 / Ridge / Simplicity']))

    def elastic_net(self):
        def _simul(degree=1, l1_ratio=0, alpha=0):
            alpha = float(alpha)
            if alpha == 0:
                model = Pipeline([
                    ("poly", PolynomialFeatures(degree)),
                    ("lr", LinearRegression())
                ])
            else:
                model = Pipeline([
                    ("poly", PolynomialFeatures(degree)),
                    ("lr", ElasticNet(alpha=alpha, l1_ratio=l1_ratio, tol=1e-8))
                ])

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model.fit(self._X_train, self._y_train)

            plt.figure(figsize=(6, 6))
            plt.title(f"R2_train: {model.score(self._X_train, self._y_train):.2f} | "
                      f"R2_test: {model.score(self._X_test, self._y_test):.2f}", fontsize=14)
            plt.scatter(self._X_train, self._y_train, c="b", s=10)
            plt.scatter(self._X_test, self._y_test, c="r", marker="x")
            plt.plot(self._space, model.predict(self._space), "k--", linewidth=1)
            plt.xlim(2.5, 9.5)
            plt.ylim(-1.5, 1.5);

        interact(_simul, degree=(1, 12, 1), l1_ratio=(0, 1, 0.1),
                 alpha=ToggleButtons(description='alpha', options=[0, 0.001, 0.01, 0.1, 1, 10]))


class BaseIllustrationRegularization:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.elasticnet = Image(f"{here}/assets/elasticnet.png", width=300)
