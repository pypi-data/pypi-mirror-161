import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from ipywidgets import interact, ToggleButtons, FloatRangeSlider
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler, PowerTransformer

from luwiji.dataset.regression import make_linear

import os
from IPython.display import Image


class BaseDemoFeatureScaling:
    def __init__(self):
        state = np.random.RandomState(42)
        self._df_chi = pd.DataFrame({"x": state.chisquare(2, 1000)})
        self._df_beta = pd.DataFrame({"x": state.beta(5, 1.5, 1000) * 9})
        self._df_normal = pd.DataFrame({"x": state.normal(7, 0.5, 5000)})

    @staticmethod
    def scaling_effect():
        def _simul(scaling='None', show3D=False):
            aa = np.linspace(-10, 10, 101)
            bb = np.linspace(-10, 10, 101)
            A, B = np.meshgrid(aa, bb)

            X, y = make_linear(coef=[0.75, -10], noise=0.3, span=(5, 10), random_state=42)
            X = X.reshape(-1, 1)

            if scaling == 'MinMax':
                X = MinMaxScaler().fit_transform(X)
            elif scaling == 'Standard':
                X = StandardScaler().fit_transform(X)
            elif scaling == 'None':
                pass

            err = A.reshape(1, 1, -1) * X.reshape(-1, 1, 1) + B.reshape(1, 1, -1) - y.reshape(-1, 1, 1)
            Z = (err ** 2).mean(0).reshape(A.shape)

            if show3D:
                plt.figure(figsize=(10, 8))
                ax = plt.subplot(projection='3d')
                ax.plot_surface(A, B, Z, rstride=2, cstride=2, cmap='RdYlGn', antialiased=False)
                ax.view_init(elev=20, azim=-45)
                ax.contour(A, B, Z, zdir='z', offset=-5, cmap='RdYlGn', levels=np.logspace(-1, 2, 15))
                ax.set(xlabel="a", ylabel="b", zlabel="Cost (MSE)", zlim=-5)
                ax.grid(False)
            else:
                plt.figure(figsize=(13, 6))

                plt.subplot(121)
                plt.scatter(X, y, c="r")
                plt.title(f"scaling: {scaling}", fontsize=14)
                # plt.xlim(-4, 4)
                # plt.ylim(-4, 4)
                plt.xlabel('x')
                plt.ylabel('y')
                plt.axhline(color='k', linewidth=1)
                plt.axvline(color='k', linewidth=1)

                plt.subplot(122)
                plt.contour(A, B, Z, cmap='RdYlGn', levels=np.logspace(0, 3, 15))
                # plt.xlim(0, 2)
                # plt.ylim(0, 2)
                plt.title("Loss Plane", fontsize=14)
                plt.xlabel('a')
                plt.ylabel('b')

        interact(_simul, scaling=ToggleButtons(options=['None', 'MinMax', 'Standard'], description='scaling'));

    def standard_scaler(self):
        def _simul(mode='demo'):
            if mode == 'demo':
                df = self._df_normal.copy()
            elif mode == 'weakness':
                df = self._df_beta.copy()

            plt.figure(figsize=(16, 5))

            plt.subplot(131)
            plt.hist(df.x, bins=100, density=1, color='r')
            plt.axvline(df.x.mean(), color='k', linewidth=1, linestyle='--')
            plt.ylim(0, 1)
            plt.xlim(-10, 10)
            plt.title("Before")

            plt.subplot(132)
            plt.hist(_positioned(df.x), bins=100, density=1, color='r')
            plt.axvline(_positioned(df.x).mean(), color='k', linewidth=1, linestyle='--')
            plt.ylim(0, 1)
            plt.xlim(-10, 10)
            plt.title("Positioned")

            plt.subplot(133)
            plt.hist(_standard(df), bins=100, density=1, color='r')
            plt.axvline(_standard(df).mean(), color='k', linewidth=1, linestyle='--')
            plt.ylim(0, 1)
            plt.xlim(-10, 10)
            plt.title("Scaled")

        def _positioned(x):
            return x - x.mean()

        def _standard(x):
            return StandardScaler().fit_transform(x).ravel()

        interact(_simul, mode=ToggleButtons(options=['demo', 'weakness'], description='mode'))

    def power_tuning(self):
        def _simul(p=1, skew="positif"):
            if skew == "positif":
                df = self._df_chi.copy()
            elif skew == "negatif":
                df = self._df_beta.copy()

            df['x_transformed'] = np.power(df.astype(np.complex), p)
            df.x_transformed = df.x_transformed.apply(lambda x: x.real)

            fig, ax = plt.subplots(1, 2, figsize=(11, 5))
            ax[0].hist(df.x, bins=100, density=1, color='r')
            ax[0].set_title(f"Before | skew: {df.x.skew():.2f}")

            ax[1].hist(df.x_transformed, bins=100, density=1, color='r')
            ax[1].set_title(f"After | skew: {df.x_transformed.skew():.2f}")

        interact(_simul, p=(-1.5, 1.5, 0.1), skew=ToggleButtons(options=['positif', 'negatif'], description='skew'))

    def power_transformer(self):
        def _simul(skew="positif"):
            if skew == "positif":
                df = self._df_chi.copy()
            elif skew == "negatif":
                df = self._df_beta.copy()

            fig, ax = plt.subplots(1, 3, figsize=(16, 5))

            df['x_yeojohnson'] = PowerTransformer().fit_transform(df[['x']])
            ax[0].hist(df.x, bins=100, density=1, color='r')
            ax[0].set_title(f"Before | skew: {df.x.skew():.2f}")

            ax[1].hist(df.x_yeojohnson, bins=100, density=1, color='r')
            ax[1].set_title("Yeo-Johnson Transformation")

            try:
                df['x_boxcox'] = PowerTransformer(method='box-cox').fit_transform(df[['x']])
                ax[2].hist(df.x_boxcox, bins=100, density=1, color='r')
                ax[2].set_title("Box-Cox Transformation")
            except ValueError:
                ax[2].set_title("Box-Cox Transformation")
                ax[2].text(0.5, 0.5, "Transformasi gagal karena\nmengandung data yang negatif", ha='center',
                           fontsize=13)

        interact(_simul, skew=ToggleButtons(options=['positif', 'negatif'], description='skew'))

    def minmax_scaler(self):
        def _simul_mode(mode='demo'):
            def _simul(xrange, show_process=False):
                if xrange[0] == xrange[1]:
                    xrange = (xrange[0], xrange[1] + 1e-6)

                X_positioned = X - X.min()
                X_scaled = self.minmax(X, scale_range=xrange)

                plt.figure(figsize=(10, 6))
                plt.xlim(*xlim)
                plt.ylim(-0.02, 0.02)

                plt.scatter(X, y, s=50, c='r', zorder=1)
                plt.scatter(X_positioned, y_positioned, s=50, c='g', zorder=1)
                plt.scatter(X_scaled, y_scaled, s=50, c='b', zorder=1)

                if show_process:
                    plt.plot([X.min(), xrange[0]], [0.01, 0], 'r-', linewidth=2)
                    plt.plot([X_positioned.min(), xrange[0], xrange[0]], [0, -0.01, -0.02], 'g-', linewidth=2)
                    plt.plot([X_positioned.max(), xrange[1], xrange[1]], [0, -0.01, -0.02], 'g-', linewidth=2)

                for i, j, k in zip(X, X_positioned, X_scaled):
                    plt.plot([i[0], j[0], k], [0.01, 0, -0.01], 'k--', linewidth=1, alpha=0.3)

                plt.axhline(0.01, xmin=_hline_min(X, xlim), xmax=_hline_max(X, xlim), color='r', linewidth=1, zorder=-1)
                plt.axhline(0, xmin=_hline_min(X_positioned, xlim), xmax=_hline_max(X_positioned, xlim), color='g',
                            linewidth=1, zorder=-1)
                plt.axhline(-0.01, xmin=_hline_min(X_scaled, xlim), xmax=_hline_max(X_scaled, xlim), color='b',
                            linewidth=1, zorder=-1)

                plt.yticks([-0.01, 0, 0.01], labels=['scaled', 'positioned', 'before'], fontsize=14);
                plt.xticks([X.min(), xrange[0], xrange[1], X.max()],
                           [round(X.min(), 1), xrange[0], xrange[1], round(X.max(), 1)], fontsize=14);

            def _hline_min(X, xlim):
                return (X.min() - xlim[0]) / (xlim[1] - xlim[0])

            def _hline_max(X, xlim):
                return 1 - (xlim[1] - X.max()) / (xlim[1] - xlim[0])

            state = np.random.RandomState(3)
            xlim = (-1, 3)
            if mode == 'demo':
                X = -1 + 3 * state.rand(10, 1)
            elif mode == 'weakness':
                X = -1 + 1.5 * state.rand(10, 1)
                X = np.vstack([X, 1.8])
            y = np.ones_like(X) * 0.01
            y_positioned = np.zeros_like(X)
            y_scaled = -np.ones_like(X) * 0.01
            interact(_simul, xrange=FloatRangeSlider(value=[0, 1], min=-1, max=2, step=0.1, description='MinMax',
                                                     readout=True, readout_format='.1f'))

        interact(_simul_mode, mode=ToggleButtons(options=['demo', 'weakness'], description='mode'))

    def robust_scaler(self):
        def _simul(qrange, show_process=False):
            if qrange[0] == qrange[1]:
                qrange = (qrange[0], qrange[1] + 1e-6)

            q1, q2, q3 = _get_quantile(X, qrange)

            X_positioned = X - q2
            q1_positioned, _, q3_positioned = _get_quantile(X_positioned, qrange)

            X_scaled = self.robust(X, quantile_range=qrange)
            q1_scaled, _, q3_scaled = _get_quantile(X_scaled, qrange)

            plt.figure(figsize=(10, 6))
            plt.xlim(*xlim)
            plt.ylim(-0.02, 0.02)

            plt.scatter(X, y, s=50, c='r', zorder=1)
            plt.scatter(X_positioned, y_positioned, s=50, c='g', zorder=1)
            plt.scatter(X_scaled, y_scaled, s=50, c='b', zorder=1)

            if show_process:
                plt.plot([q2, 0], [0.01, 0], 'r-', linewidth=2)
                plt.plot([q1_positioned, q1_scaled, q1_scaled], [0, -0.01, -0.02], 'g-', linewidth=2)
                plt.plot([q3_positioned, q3_scaled, q3_scaled], [0, -0.01, -0.02], 'g-', linewidth=2)

            for i, j, k in zip(X, X_positioned, X_scaled):
                plt.plot([i[0], j[0], k], [0.01, 0, -0.01], 'k--', linewidth=1, alpha=0.3)

            plt.axhline(0.01, xmin=_hline_min(X, xlim), xmax=_hline_max(X, xlim), color='r', linewidth=1, zorder=-1)
            plt.axhline(0, xmin=_hline_min(X_positioned, xlim), xmax=_hline_max(X_positioned, xlim), color='g',
                        linewidth=1, zorder=-1)
            plt.axhline(-0.01, xmin=_hline_min(X_scaled, xlim), xmax=_hline_max(X_scaled, xlim), color='b',
                        linewidth=1, zorder=-1)

            plt.yticks([-0.01, 0, 0.01], labels=['scaled', 'positioned', 'before'], fontsize=14);
            plt.xticks([0, q1_scaled, q3_scaled], [0, round(q1_scaled, 1), round(q3_scaled, 1)], fontsize=14);

        def _hline_min(X, xlim):
            return (X.min() - xlim[0]) / (xlim[1] - xlim[0])

        def _hline_max(X, xlim):
            return 1 - (xlim[1] - X.max()) / (xlim[1] - xlim[0])

        def _get_quantile(X, qrange):
            q1 = np.quantile(X, qrange[0] / 100)
            q2 = np.quantile(X, 0.5)
            q3 = np.quantile(X, qrange[1] / 100)
            return q1, q2, q3

        state = np.random.RandomState(3)
        xlim = (-1.5, 2.5)
        X = -1 + 1.5 * state.rand(10, 1)
        X = np.vstack([X, 1.8])
        y = np.ones_like(X) * 0.01
        y_positioned = np.zeros_like(X)
        y_scaled = np.ones_like(X) * -0.01
        interact(_simul, qrange=FloatRangeSlider(value=[25, 75], min=5, max=95, step=5, description='Quantile',
                                                 readout=True, readout_format='.0f'))

    @staticmethod
    def robust(x, quantile_range=(25, 75)):
        return RobustScaler(quantile_range=quantile_range, with_centering=False, with_scaling=True).fit_transform(
            x).ravel()

    @staticmethod
    def minmax(x, scale_range=(0, 1)):
        return MinMaxScaler(feature_range=scale_range).fit_transform(x).ravel()


class BaseIllustrationFeatureScaling:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.formula = Image(f"{here}/assets/scaling_formula.png", width=900)
        self.coef_balance = Image(f"{here}/assets/coef_balance.png", width=900)
