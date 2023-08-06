import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import interact, ToggleButton, ToggleButtons
from ipywidgets.widgets import SelectionSlider
from IPython.display import Image, display
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor


class BaseDemoRandomForest:
    def __init__(self):
        np.random.seed(42)
        self._X = np.linspace(0, 5, 30)
        self._y = 0.9 * self._X ** 2 + 3 * self._X + 10 * np.random.rand(len(self._X))
        self._space = np.linspace(0, 5, 250).reshape(-1, 1)
        self._X = self._X.reshape(-1, 1)
        self._state = 0

    def data(self):
        plt.figure(figsize=(6, 6))
        plt.scatter(self._X.ravel(), self._y, s=10, c='k')

    def decision_tree(self):
        def _calc_rmse(x):
            mask = X <= x
            x1, y1 = X[mask], y[mask]

            mask = X > x
            x2, y2 = X[mask], y[mask]

            mean1, mean2 = y1.mean(), y2.mean()
            rmse1 = np.sqrt(np.mean((y1 - mean1) ** 2))
            rmse2 = np.sqrt(np.mean((y2 - mean2) ** 2))
            w1 = len(y1) / len(y)
            w2 = len(y2) / len(y)
            rmse = w1 * rmse1 + w2 * rmse2
            return x1, y1, x2, y2, mean1, mean2, rmse

        def _simul(x, show_error=False):
            x1, y1, x2, y2, mean1, mean2, rmse = _calc_rmse(x)

            plt.figure(figsize=(15, 6))

            plt.subplot(121)
            plt.scatter(x1, y1, c='b', s=50)
            plt.scatter(x2, y2, c='g', s=50)
            plt.plot([minX, x, x, maxX], [mean1, mean1, mean2, mean2], 'r-')
            plt.title(f"Decision: X<={x:.2f} | error: {rmse:.2f}", fontsize=14)

            if show_error:
                plt.subplot(122)
                plt.scatter(decisions, error, c='k', s=30)
                plt.axvline(x, color='r')
                plt.ylabel("Weighted RMSE")

        X, y = self._X.ravel(), self._y
        minX, maxX = X.min(), X.max()
        decisions = [(x1 + x2) / 2 for x1, x2 in zip(X[:-1], X[1:])]
        error = [_calc_rmse(x)[-1] for x in decisions]
        interact(_simul,
                 x=SelectionSlider(options=decisions, value=decisions[10], description='decision', readout=False))

    def max_depth(self):
        def _simul(depth=1, show_tree=False):
            dt = DecisionTreeRegressor(max_depth=depth)
            dt.fit(X, y)

            if show_tree:
                if depth == 1:
                    width = 300
                elif depth == 2:
                    width = 600
                elif depth == 3:
                    width = 800
                elif depth > 3:
                    width = 1000
                display(Image(f"{here}/assets/tree_depth_{depth}.png", width=width))
            else:
                plt.figure(figsize=(6, 6))
                plt.scatter(X, y, s=10, c='k')
                plt.plot(space, dt.predict(space), 'r-')

        here = os.path.dirname(__file__)
        X, y = self._X, self._y
        space = self._space
        interact(_simul, depth=(1, 7, 1))

    def min_samples_leaf(self):
        def _simul(depth=1, min_samples_leaf=1):
            dt = DecisionTreeRegressor(max_depth=depth, min_samples_leaf=min_samples_leaf)
            dt.fit(X, y)

            plt.figure(figsize=(6, 6))
            plt.scatter(X, y, s=10, c='k')
            plt.plot(space, dt.predict(space), 'r-')

        X, y = self._X, self._y
        space = self._space
        interact(_simul, depth=(1, 7, 1), min_samples_leaf=(1, 10, 1))

    def bootstrap(self):
        def _simul(bootstrap, fit):
            st = np.random.RandomState(self._state)

            plt.figure(figsize=(6, 6))
            plt.xlim(-0.5, 5.5)
            plt.ylim(-0.5, 45)
            plt.scatter(X, y, s=10, c='b')
            X_mask, y_mask = X, y

            if bootstrap:
                mask = st.choice(len(X), size=len(X), replace=True)
                mask = list(set(mask))
                X_mask, y_mask = X[mask], y[mask]
                plt.scatter(X_mask, y_mask, s=100, facecolors='none', edgecolors='r')
            else:
                self._state += 1

            if fit:
                dt = DecisionTreeRegressor(max_depth=7)
                dt.fit(X_mask, y_mask)
                plt.plot(space, dt.predict(space), 'r-')

        X, y = self._X, self._y
        space = self._space
        interact(_simul, bootstrap=ToggleButton(value=False, description='bootstrap'),
                 fit=ToggleButton(value=False, description='fit'))

    def bagging(self):
        def _simul(n_tree=1, depth=1, phase='bootstrap'):
            rf = RandomForestRegressor(n_estimators=n_tree, max_depth=depth, random_state=42)
            rf.fit(X, y)

            if phase == "bootstrap":
                plt.figure(figsize=(13, 9))
                for idx, dt in enumerate(rf.estimators_, 1):
                    plt.subplot(2, 3, idx)
                    plt.scatter(X, y, s=10, c='k')
                    plt.plot(space, dt.predict(space), 'r-')
            elif phase == "aggregate":
                plt.figure(figsize=(13, 6))

                plt.subplot(121)
                plt.scatter(X, y, s=10, c='k')
                for idx, dt in enumerate(rf.estimators_, 1):
                    plt.plot(space, dt.predict(space), 'r-')

                plt.subplot(122)
                plt.scatter(X, y, s=10, c='k')
                plt.plot(space, rf.predict(space), 'r-')

        X, y = self._X, self._y
        space = self._space
        interact(_simul, depth=(1, 7, 1), n_tree=(1, 6, 1),
                 phase=ToggleButtons(options=['bootstrap', 'aggregate'], description='phase'))

    @staticmethod
    def grid_vs_random_search():
        def _simul(show_score=False):
            plt.figure(figsize=(13, 6))

            plt.subplot(121)
            xx, yy = np.meshgrid(np.logspace(-3, 3, 7), np.logspace(-3, 3, 7))
            plt.scatter(xx, yy, s=200, c='w', marker='*', edgecolors='k')
            if show_score:
                plt.contourf(X1, X2, Z, cmap='RdYlGn', zorder=-1, levels=np.linspace(0, 1, 10))
            plt.xlabel('C', fontsize=12)
            plt.ylabel('gamma', fontsize=12)
            plt.xscale('log')
            plt.yscale('log')
            plt.xlim(1e-3, 1e3)
            plt.ylim(1e-3, 1e3)
            plt.title('Grid Search (49 trials)', fontsize=14)

            plt.subplot(122)
            state1 = np.random.RandomState(0)
            state2 = np.random.RandomState(1)
            xx = 10 ** (-3 + 6 * state1.rand(10))
            yy = 10 ** (-3 + 6 * state2.rand(10))
            plt.scatter(xx, yy, s=200, c='w', marker='*', edgecolors='k', linewidths=1)
            if show_score:
                plt.contourf(X1, X2, Z, cmap='RdYlGn', zorder=-1, levels=np.linspace(0, 1, 10))
            plt.xlabel('C', fontsize=12)
            plt.ylabel('gamma', fontsize=12)
            plt.xscale('log')
            plt.yscale('log')
            plt.xlim(1e-3, 1e3)
            plt.ylim(1e-3, 1e3)
            plt.title('Randomized Search (10 trials)', fontsize=14);

        here = os.path.dirname(__file__)
        df = pd.read_csv(f"{here}/data/space.csv")
        X1 = df.param_svm__C.values.reshape(50, 50)
        X2 = df.param_svm__gamma.values.reshape(50, 50)
        Z = df.mean_test_score.values.reshape(50, 50)
        interact(_simul)


class BaseIllustrationRandomForest:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.nomenklatur_house = Image(f"{here}/assets/nomenklatur1.png", width=500)
        self.nomenklatur_mobile = Image(f"{here}/assets/nomenklatur2.png", width=500)
        self.grid_random_comparison = Image(f"{here}/assets/grid_random_comparison.png", width=800)
        self.fallacy1 = Image(f"{here}/assets/fallacy1.jpg", width=700)
        self.fallacy2 = Image(f"{here}/assets/fallacy2.png", width=500)
        self.max_features = Image(f"{here}/assets/max_features.png", width=800)
