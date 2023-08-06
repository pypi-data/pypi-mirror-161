import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from ipywidgets import interact, ToggleButtons
from sklearn.linear_model import LinearRegression

from luwiji.dataset.regression import mountain, make_linear, dZ

import os
from IPython.display import Image


class BaseDemoLinearRegression:
    def __init__(self):
        pass

    @staticmethod
    def slope_and_bias():
        def _simul(a=0, b=0):
            plt.figure(figsize=(6, 6))
            plt.plot(space, a*space+b, "r--")
            plt.axis('equal')
            plt.xlabel("X"); plt.ylabel("y")
            plt.xlim(-2.5, 2.5); plt.ylim(-2.5, 2.5)
            plt.title(f"$y = {a}x + {b}$")
            plt.scatter(0, b, c='r', s=30)
            plt.axhline(color='k', linewidth=1)
            plt.axvline(color='k', linewidth=1)
        space = np.linspace(-2.5, 2.5, 10)
        interact(_simul, a=(-2, 2, 0.1), b=(-2, 2, 0.1));

    @staticmethod
    def play_linear_regression():
        def _simul(a=1, b=0):
            plt.figure(figsize=(6,6))
            plt.scatter(X, y, c="b")
            plt.plot(space, a*space+b, "r--")
            plt.axis('equal')
            plt.xlabel("X"); plt.ylabel("y")
            plt.xlim(0, 5); plt.ylim(0, 5)
            plt.title(f"$y = {a}x + {b}$")
        space = np.linspace(0, 5, 10)
        X, y = make_linear(coef=[-0.5, 3], noise=0.2, random_state=42)
        interact(_simul, a=(-3, 3, 0.1), b=(-3, 3, 0.1));

    @staticmethod
    def loss():
        def _simul(a=1, b=0):
            plt.figure(figsize=(6,6))
            plt.scatter(X, y, c="b")
            plt.plot(space, a*space+b, "r--")
            pred = a*X+b
            cost = np.mean((pred-y)**2)
            plt.title(fr"$y={a}X+{b}$ | MSE: {cost:.2f}", fontsize=15)
            for x, p, d in zip(X, pred, y):
                plt.plot([x, x], [p, d], 'g-')
            plt.axis('equal')
            plt.xlabel("X"); plt.ylabel("y")
            plt.xlim(0, 5); plt.ylim(0, 5)
        space = np.linspace(0, 5, 10)
        X, y = make_linear(n_samples=30, coef=[0.5, 1], noise=0.5, random_state=42)
        interact(_simul, a=(0, 2, 0.1), b=(0, 2, 0.1));

    @staticmethod
    def loss_curve():
        def _simul(a=0.1, show_loss_line=False, show_loss=False, show_tuning=False):
            plt.figure(figsize=(13, 6))

            plt.subplot(121)
            plt.scatter(X, y, c="b")
            plt.plot(space, a * space, "r--")
            pred = a * X
            cost = np.mean((pred - y) ** 2)
            plt.title(fr"$y={a}X$ | MSE: {cost:.2f}", fontsize=15)
            plt.xlabel("X"); plt.ylabel("y")
            plt.xlim(0, 5); plt.ylim(0, 5)

            if show_loss_line:
                for x, p, d in zip(X, pred, y):
                    plt.plot([x, x], [p, d], 'g-')

            if show_loss:
                plt.subplot(122)
                plt.scatter(a, cost, c="r")
                plt.title("Parameter Tuning", fontsize=15)
                plt.xlabel("a"); plt.ylabel("MSE")
                plt.xlim(0, 3); plt.ylim(0, 40)

            if show_loss & show_tuning:
                params = np.arange(0, 3, 0.1)
                cost_list = [np.mean((a * X - y) ** 2) for a in params]
                plt.scatter(params, cost_list, s=10, c='r')

        X, y = make_linear(coef=[1, 0], noise=0.2, random_state=42)
        space = np.linspace(0, 6, 10)
        interact(_simul, a=(0, 3, 0.1));

    @staticmethod
    def loss_plane():
        def _simul(a=0, b=2.5, show3d=False):
            if not show3d:
                cost = np.mean(((a * X + b) - y) ** 2)

                plt.figure(figsize=(13, 6))

                plt.subplot(121)
                plt.scatter(X, y, c="r")
                plt.plot(space, a * space + b, "b-")
                plt.title(fr"$y={a}X+{b}$ | MSE: {cost:.2f}", fontsize=14)
                plt.xlim(-4, 4)
                plt.ylim(-4, 4)
                plt.xlabel('x')
                plt.ylabel('y')
                plt.axhline(color='k', linewidth=1)
                plt.axvline(color='k', linewidth=1)

                plt.subplot(122)
                plt.contour(A, B, Z, cmap='RdYlGn', levels=np.logspace(-1, 2, 15))
                plt.scatter(a, b, c="b", s=50)
                plt.title("Loss Plane", fontsize=14)
                plt.xlim(-1, 2)
                plt.ylim(0, 3)
                plt.xlabel('a')
                plt.ylabel('b')
            else:
                plt.figure(figsize=(10, 8))
                ax = plt.subplot(projection='3d')
                ax.plot_surface(A, B, Z, rstride=2, cstride=2, cmap='RdYlGn', antialiased=False)
                ax.view_init(elev=20, azim=-45)
                ax.contour(A, B, Z, zdir='z', offset=-5, cmap='RdYlGn', levels=np.logspace(-1, 2, 15))
                ax.set(xlabel="a", ylabel="b", zlabel="Cost (MSE)", zlim=-5)
                ax.grid(False)

        space = np.linspace(-4, 4, 10)

        aa = np.linspace(-1, 2, 101)
        bb = np.linspace(0, 3, 101)
        A, B = np.meshgrid(aa, bb)

        X, y = make_linear(coef=[0.75, 1], noise=0.3, span=(-3, 3), random_state=42)
        err = A.reshape(1, 1, -1) * X.reshape(-1, 1, 1) + B.reshape(1, 1, -1) - y.reshape(-1, 1, 1)
        Z = (err ** 2).mean(0).reshape(A.shape)

        interact(_simul, a=(-1, 2, 0.25), b=(0, 3, 0.25));


    @staticmethod
    def gradient_descent():
        def _simul(example='1', plot='3D'):
            if example == '1':
                x_init = -20
                y_init = 0.1
            elif example == '2':
                x_init = -20
                y_init = -5
            elif example == '3':
                x_init = -20
                y_init = -10

            x_plot = [x_init]
            y_plot = [y_init]
            z_plot = [mountain(x_plot[-1], y_plot[-1])]

            for _ in range(1000):
                dx, dy = dZ(x_plot[-1], y_plot[-1])
                x_plot.append(x_plot[-1] - lr * dx)
                y_plot.append(y_plot[-1] - lr * dy)
                z_plot.append(mountain(x_plot[-1], y_plot[-1]))

            if plot == '3D':
                plt.figure(figsize=(8, 8), dpi=100)
                ax = plt.subplot(projection='3d')
                ax.plot_surface(X1, X2, Z, cmap='RdYlGn', alpha=0.4)
                ax.plot(x_plot, y_plot, z_plot, 'r-', linewidth=1)

                xmin, xmax = ax.get_xlim3d()
                ymin, ymax = ax.get_ylim3d()
                zmin, zmax = ax.get_zlim3d()
                ax.set_xlim3d(xmin * 0.7, xmax * 0.7)
                ax.set_ylim3d(ymin * 0.7, ymax * 0.7)
                ax.set_zlim3d(zmin * 2, zmax * 2)
                ax.view_init(elev=35, azim=-70)
                ax.set(xlabel='x', ylabel='y', zlabel='z')
                plt.axis('off')
            elif plot == 'kontur':
                plt.figure(figsize=(6, 6))
                plt.contourf(X1, X2, Z, cmap='RdYlGn', levels=np.linspace(Z.min(), Z.max(), 20))
                plt.plot(x_plot, y_plot, 'k-', linewidth=2, zorder=1)
                plt.xticks([])
                plt.yticks([])

        xx = np.linspace(-50, 50, 100)
        yy = np.linspace(-50, 50, 100)

        X1, X2 = np.meshgrid(xx, yy)

        Z = mountain(X1.ravel(), X2.ravel())
        Z = Z.reshape(X1.shape)
        lr = 50
        interact(_simul, example=ToggleButtons(options=['1', '2', '3'], description='Contoh'),
                 plot=ToggleButtons(options=['kontur', '3D'], description='Plot'))


    @staticmethod
    def learning_rate():
        def _simul_lr(lr=0.1):
            def _simul(iteration=0):
                plt.figure(figsize=(6, 6))
                plt.plot(X, y, 'k-', zorder=-1)
                plt.scatter(1, 0, c='b', marker='*', s=100)
                plt.scatter(x[:iteration + 1], y_plot[:iteration + 1], c='r')
                if 0.95 < x[iteration] < 1.05:
                    plt.title(f'Minimum is reached')
                plt.xlabel('slope')
                plt.ylabel('Loss')

            x = [-50]
            for i in range(50):
                x.append(x[-1] - lr * dfunc(x[-1]))
            y_plot = [func(item) for item in x]
            interact(_simul, iteration=(0, 15, 1))

        func = lambda x: 0.1 * x ** 2 - 0.2 * x
        dfunc = lambda x: 0.2 * x - 0.2

        X = np.linspace(-70, 60, 150)
        y = func(X)
        interact(_simul_lr, lr=ToggleButtons(options=[0.1, 1, 3, 5, 8, 10, 11], description='l_rate'))

    @staticmethod
    def linear_regression():
        def _simul_lr(lr=0.05):
            def _simul(iteration=0):
                plt.figure(figsize=(13, 6))

                plt.subplot(121)
                plt.scatter(X, y, c="r")
                plt.plot(space, a[iteration] * space + b[iteration], "b-")
                cost = np.mean(((a[iteration] * X + b[iteration]) - y) ** 2)
                plt.title(fr"$y={a[iteration]:.2f}X+{b[iteration]:.2f}$ | MSE: {cost:.2f}", fontsize=14)
                plt.xlim(-4, 4)
                plt.ylim(-4, 4)
                plt.xlabel('x')
                plt.ylabel('y')
                plt.axhline(color='k', linewidth=1)
                plt.axvline(color='k', linewidth=1)

                plt.subplot(122)
                plt.contour(A, B, Z, cmap='RdYlGn', levels=np.logspace(-1, 2, 15))
                plt.plot(a[:iteration + 1], b[:iteration + 1], "b-o")
                plt.title("Loss Plane", fontsize=14)
                plt.xlim(-1, 2)
                plt.ylim(0, 3)
                plt.xlabel('a')
                plt.ylabel('b')

            def da(a, b):
                return np.mean(2 * (a * X + b - y) * X)

            def db(a, b):
                return np.mean(2 * (a * X + b - y))

            space = np.linspace(-4, 4, 10)
            aa = np.linspace(-1, 2, 101)
            bb = np.linspace(0, 3, 101)
            A, B = np.meshgrid(aa, bb)

            X, y = make_linear(coef=[0.75, 1], noise=0.3, span=(-3, 3), random_state=42)
            err = A.reshape(1, 1, -1) * X.reshape(-1, 1, 1) + B.reshape(1, 1, -1) - y.reshape(-1, 1, 1)
            Z = (err ** 2).mean(0).reshape(A.shape)

            a = [0]
            b = [2.5]
            for i in range(25):
                a.append(a[-1] - lr * da(a[-1], b[-1]))
                b.append(b[-1] - lr * db(a[-1], b[-1]))

            interact(_simul, iteration=(0, 25, 1));
        interact(_simul_lr, lr=ToggleButtons(options=[0.05, 0.1, 0.3], description='l_rate'))


    @staticmethod
    def intercept():
        def _simul(reg_model='y = Ax + b'):

            if reg_model == 'y = Ax + b':
                fit_intercept = True
            elif reg_model == 'y = Ax':
                fit_intercept = False

            model = LinearRegression(fit_intercept=fit_intercept)
            model.fit(X.reshape(-1, 1), y)

            plt.figure(figsize=(13, 6))

            plt.subplot(121)
            plt.scatter(X, y, s=10, c='r')
            if reg_model == 'y = Ax + b':
                plt.title(fr"$y = {model.coef_[0]:.2f} * berat\_beras {model.intercept_:.2f}$", fontsize=14)
            elif reg_model == 'y = Ax':
                plt.title(fr"$y = {model.coef_[0]:.2f} * berat\_beras$", fontsize=14)
            plt.plot(space, model.predict(space), 'b-')
            plt.xlabel('berat (kg)')
            plt.ylabel('harga (ribu rupiah)')

            plt.subplot(122)
            plt.plot(space, model.predict(space), 'b-')
            plt.scatter(0, model.intercept_, c='r', s=30)
            plt.annotate("bias / intercept", xy=(0, model.intercept_), xytext=(50, -20), textcoords="offset points",
                         horizontalalignment='left', verticalalignment='center', arrowprops={"arrowstyle": "->", 'connectionstyle':"arc,rad=-0.3"}, fontsize=10)
            plt.xlabel('berat (kg)')
            plt.ylabel('harga (ribu rupiah)')
            plt.xlim(-0.5, 1)
            plt.ylim(-0.5, 1)
            plt.axhline(color='k', linewidth=1)
            plt.axvline(color='k', linewidth=1)

        X, y = make_linear(coef=[9.5, 0], noise=1.5, span=(3, 8), random_state=42)

        space = np.linspace(0, 10, 100).reshape(-1, 1)
        interact(_simul, reg_model=ToggleButtons(options=['y = Ax + b', 'y = Ax'], description='Model'))


class BaseIllustrationLinearRegression:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.straight_line = Image(f"{here}/assets/straight_line_eq.png", width=700)
        self.pso = Image(f"{here}/assets/non_grad_based.gif", width=350)
        self.analogy = Image(f"{here}/assets/grad_descent_analogy.jpg", width=350)
