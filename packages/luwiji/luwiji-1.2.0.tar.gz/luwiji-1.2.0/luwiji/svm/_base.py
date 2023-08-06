import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from ipywidgets import interact, FloatLogSlider, ToggleButtons
from sklearn.svm import SVC
from sklearn.preprocessing import PolynomialFeatures
from jcopml.plot import plot_svc
from luwiji.dataset.svm import gen_data_1, gen_data_2, gen_data_3

import os
from IPython.display import Image


class BaseDemoSVM:
    def __init__(self):
        pass

    def problem(self, problem):
        X, y = self.get_data(problem)
        plt.figure(figsize=(6, 6))
        plt.scatter(X.x_1, X.x_2, c=y, s=5, cmap='bwr');

    def C(self, problem):
        def _simul(C=10):
            model = SVC(kernel='linear', C=C).fit(X, y)
            plot_svc(X, y, model)

        X, y = self.get_data(problem)
        interact(_simul, C=FloatLogSlider(value=100, base=10, min=-2, max=1, step=0.25, description='C'))

    def kernel(self, problem):
        def _simul(kernel='linear', C=10, support=False):
            model = SVC(kernel=kernel, C=C, gamma='scale').fit(X, y)
            if support:
                plot_svc(X, y, model)
            else:
                plot_svc(X, y, model, support=support)

        X, y = self.get_data(problem)
        interact(_simul, kernel=ToggleButtons(options=['linear', 'rbf'], description='Kernel'),
                 C=FloatLogSlider(value=100, base=10, min=-2, max=1, step=0.25, description='C'))

    def rbf(self):
        def _simul(elevation=90, sigma=0):
            r = np.exp(-(X ** 2).sum(1) / 2 / sigma ** 2)
            plt.figure(figsize=(8, 8))
            ax = plt.subplot(projection='3d')
            ax.scatter3D(X.x_1, X.x_2, r, c=y, s=50, cmap='bwr')
            ax.view_init(elev=elevation, azim=30)
            ax.set(xlabel="x", ylabel="y", zlabel="r")

        X, y = self.get_data(2)
        interact(_simul, elevation=(0, 90, 15), sigma=(0, 2, 0.2))

    def svm(self):
        def _simul_problem(problem):
            def _simul(gamma=0.01, plot_3d=False):
                model = SVC(kernel='rbf', C=1, gamma=gamma).fit(X, y)
                if plot_3d:
                    plt.figure(figsize=(8, 8))
                    val = model.decision_function(X_grid)
                    Z = val.reshape(X1.shape)

                    ax = plt.subplot(projection='3d')
                    ax.plot_surface(X1, X2, Z, cstride=2, rstride=2, antialiased=False)
                else:
                    plot_svc(X, y, model, support=False)

            X, y = self.get_data(problem)

            xx = np.linspace(X.x_1.min(), X.x_1.max(), 100)
            yy = np.linspace(X.x_2.min(), X.x_2.max(), 100)
            X1, X2 = np.meshgrid(xx, yy)

            X_grid = np.c_[X1.ravel(), X2.ravel()]

            interact(_simul, gamma=FloatLogSlider(value=1, base=10, min=0, max=4, step=0.25, description='gamma'))

        interact(_simul_problem, problem=ToggleButtons(options=[1, 2, 3], description='Problem'))

    @staticmethod
    def get_data(problem):
        if problem == 1:
            df = gen_data_1()
        elif problem == 2:
            df = gen_data_2()
        elif problem == 3:
            df = gen_data_3()
        else:
            raise Exception("Please choose either sample 1, 2 or 3")
        X = df.drop(columns="label")
        y = df.label
        return X, y

    @staticmethod
    def gamma():
        def _simul(gamma):
            plt.figure(figsize=(6, 5))
            plt.plot(space, gaussian(space, gamma=gamma))
            plt.xlim(-6, 6)
            plt.ylim(0, 1.1)

        def gaussian(x, gamma):
            return np.exp(-gamma * x ** 2)

        space = np.linspace(-10, 10, 500)
        interact(_simul, gamma=FloatLogSlider(value=100, base=10, min=-1.5, max=1.5, step=0.25, description='gamma'))

    @staticmethod
    def poly_features():
        def _simul(degree=1, interaction_only=False, include_bias=True):
            X = pd.DataFrame({"x_1": [1, 1, 1], "x_2": [2, 2, 2], "x_3": [3, 3, 3]})
            poly = PolynomialFeatures(degree=degree, interaction_only=interaction_only, include_bias=include_bias).fit(
                X)
            print(poly.get_feature_names_out(X.columns))

        interact(_simul, degree=ToggleButtons(options=[1, 2, 3], description='degree'))


class BaseIllustrationSVM:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.choose_one = Image(f"{here}/assets/choose_one.png", width=900)
        self.maximum_margin = Image(f"{here}/assets/maximum_margin.png", width=900)
        self.nomenklatur_carprice = Image(f"{here}/assets/nomenklatur_carprice.png", width=600)
        self.nomenklatur_cc_fraud = Image(f"{here}/assets/nomenklatur_cc_fraud.png", width=600)
