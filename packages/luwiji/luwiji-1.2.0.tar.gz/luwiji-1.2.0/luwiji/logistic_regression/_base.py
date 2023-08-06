import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from ipywidgets import interact, ToggleButtons, SelectionSlider
from sklearn.datasets import make_blobs
from sklearn.linear_model import LogisticRegression
from scipy.stats import mode
from sklearn.metrics import roc_curve, precision_recall_curve, auc, average_precision_score
from luwiji.dataset.regression import make_binary

import os
from IPython.display import Image


class BaseDemoLogisticRegression:
    def __init__(self):
        pass

    def logistic_regression(self):
        def _simul(a=1, b=0):
            plt.figure(figsize=(6, 6))
            plt.scatter(X, y, c=y, cmap='bwr')
            plt.plot(space, self.sigmoid(space, a, b), "r-")
            plt.xlabel("X")
            plt.ylabel("y")
            plt.xlim(-5, 7)
            plt.ylim(-0.1, 1.1)
            plt.title(f"$a=${a} | $b=${b}", fontsize=14)

        space = np.linspace(-10, 10, 100)
        X, y = make_binary(mean=(-2, 4), n_samples=100)
        interact(_simul, a=(0, 5, 0.5), b=(-5, 5, 0.5));

    def loss_curve(self):
        def _simul_loss(loss='MSE'):
            def _simul(a=1, show_loss_line=False, show_loss=False, show_tuning=False):
                pred = self.sigmoid(X.flatten(), a, b)
                if loss == 'MSE':
                    cost = np.mean((pred - y) ** 2)
                elif loss == 'MCE':
                    cost = -np.mean(y * np.log(pred) + (1 - y) * np.log(1 - pred))

                plt.figure(figsize=(13, 6))

                plt.subplot(121)
                plt.scatter(X, y, c=y, cmap='bwr')
                plt.plot(space, self.sigmoid(space, a, b), "r-")
                plt.xlabel("X")
                plt.ylabel("y")
                plt.xlim(-5, 8)
                plt.ylim(-0.1, 1.1)
                plt.title(fr"$y=sigmoid({a}X{b})$ | {loss}: {cost:.2f}", fontsize=15)

                if show_loss_line:
                    for x, p, d in zip(X, pred, y):
                        plt.plot([x, x], [p, d], 'g-')

                if show_loss:
                    plt.subplot(122)
                    plt.scatter(a, cost, c="r")
                    plt.title("Parameter Tuning", fontsize=15)
                    plt.xlabel("a")
                    plt.ylabel(f"{loss} Loss")
                    plt.xlim(0, 5)
                    plt.ylim(1e-5, 10)
                    plt.yscale('log')

                if show_loss & show_tuning:
                    plt.scatter(params, Z, s=10, c='r')
                    plt.yscale('log')

            space = np.linspace(-10, 10, 100)

            params = np.arange(0, 5, 0.25)

            logit = self.sigmoid(X.reshape(-1, 1), params.reshape(1, -1), b)
            if loss == 'MSE':
                err = logit - y.reshape(-1, 1)
                Z = (err ** 2).mean(0).reshape(params.shape)
            elif loss == 'MCE':
                err = y.reshape(-1, 1) * np.log(logit) + (1 - y.reshape(-1, 1)) * np.log(1 - logit)
                Z = -err.mean(0).reshape(params.shape)
            interact(_simul, a=(0, 5, 0.25));

        b = -7
        X, y = make_binary(mean=(-2, 4), n_samples=100)
        interact(_simul_loss, loss=ToggleButtons(options=['MSE', 'MCE'], description='loss'));

    def loss_plane(self):
        def _simul_loss(loss='MSE'):
            def _simul(a=1, b=0, show3d=False):
                if not show3d:
                    pred = self.sigmoid(X, a, b)
                    if loss == 'MSE':
                        cost = np.mean((pred - y) ** 2)
                    elif loss == 'MCE':
                        cost = -np.mean(y * np.log(pred) + (1 - y) * np.log(1 - pred))

                    plt.figure(figsize=(13, 6))

                    plt.subplot(121)
                    plt.scatter(X, y, c=y, cmap='bwr')
                    plt.plot(space, self.sigmoid(space, a, b), "r--")

                    plt.title(fr"$y=sigmoid({a}X{b})$ | {loss}: {cost:.2f}", fontsize=15)
                    plt.xlim(-5, 8)
                    plt.ylim(-0.1, 1.1)
                    plt.xlabel("X")
                    plt.ylabel("y")

                    plt.subplot(122)
                    plt.contour(A, B, Z, cmap='RdYlGn', levels=np.logspace(-5, 1, 10))
                    plt.scatter(a, b, c="r", s=50)
                    plt.title("Loss Plane")
                    plt.xlim(0, 5)
                    plt.ylim(-10, 0)
                    plt.xlabel("a")
                    plt.ylabel("b")
                else:
                    plt.figure(figsize=(10, 8))
                    ax = plt.subplot(projection='3d')
                    ax.plot_surface(A, B, Z, rstride=2, cstride=2, cmap='RdYlGn', antialiased=False)
                    ax.view_init(elev=20, azim=-65)
                    ax.contour(A, B, Z, zdir='z', offset=-0.1, cmap='RdYlGn', levels=np.logspace(-5, 1, 10))
                    ax.set(xlabel="a", ylabel="b", zlabel="Cost (MCE)", zlim=-0.1)
                    ax.grid(False)

            space = np.linspace(-10, 10, 100)

            aa = np.linspace(0, 5, 101)
            bb = np.linspace(-10, 0, 101)
            A, B = np.meshgrid(aa, bb)

            logit = self.sigmoid(X.reshape(-1, 1, 1), A.reshape(1, 1, -1), B.reshape(1, 1, -1))
            if loss == 'MSE':
                err = logit - y.reshape(-1, 1, 1)
                Z = (err ** 2).mean(0).reshape(A.shape)
            elif loss == 'MCE':
                err = y.reshape(-1, 1, 1) * np.log(logit) + (1 - y.reshape(-1, 1, 1)) * np.log(1 - logit)
                Z = -err.mean(0).reshape(A.shape)

            interact(_simul, a=(0, 5, 0.25), b=(-10, 0, 0.5));

        X, y = make_binary(mean=(-2, 4), n_samples=100)
        interact(_simul_loss, loss=ToggleButtons(options=['MSE', 'MCE'], description='loss'));

    def threshold(self):
        def _simul(a=1, b=0, threshold=0.5, highlight=False):
            x_t = (np.log(threshold / (1 - threshold)) - b) / a

            space_1 = np.linspace(-10, x_t, 100)
            space_2 = np.linspace(x_t, 10, 100)
            pred_1 = self.sigmoid(space_1, a, b)
            pred_2 = self.sigmoid(space_2, a, b)

            plt.figure(figsize=(6, 6))
            plt.scatter(X, y, c=y, cmap='bwr')
            plt.plot(space_1, pred_1, "b-")
            plt.plot(space_2, pred_2, "r-")
            plt.axhline(threshold, color='k', linewidth=1, linestyle='--', alpha=0.5)

            if highlight:
                plt.fill_between(space_1, 0, pred_1, color='b', alpha=0.5)
                plt.fill_between(space_2, 1, pred_2, color='r', alpha=0.5)

            plt.title(f"$a=${a} | $b=${b}", fontsize=14)
            plt.xlabel("X")
            plt.ylabel("y")
            plt.xlim(-4, 8)
            plt.ylim(-0.1, 1.1)

        X, y = make_binary(mean=(-2, 4), n_samples=100)
        interact(_simul, a=(0.5, 5, 0.5), b=(-10, 10, 1), threshold=(0.05, 0.96, 0.05));

    @staticmethod
    def sigmoid(x, a, b):
        return 1 / (1 + np.exp(-(a * x + b)))

    @staticmethod
    def one_vs_rest():
        X, y = make_blobs(cluster_std=(1.5, 1.5, 1.5), random_state=42)

        xx = np.linspace(-15, 15, 200)
        yy = np.linspace(-15, 15, 200)
        XX, YY = np.meshgrid(xx, yy)
        X_grid = np.c_[XX.ravel(), YY.ravel()]

        plt.figure(figsize=(12, 12))

        plt.subplot(332)
        plt.scatter(X[:, 0], X[:, 1], c=y, s=30, cmap='cool')
        plt.title("One vs Rest\n", fontsize=25)
        plt.xlim(-15, 15)
        plt.ylim(-15, 15)

        Z = []
        for i in range(3):
            model = LogisticRegression(solver='lbfgs').fit(X, (y == i))
            Z.append(model.predict_proba(X_grid)[:, 1].reshape(XX.shape))
        pred = np.stack(Z).argmax(0)

        for idx, title in enumerate(['A vs non A', 'B vs non B', 'C vs non C']):
            plt.subplot(3, 3, idx + 4)
            plt.scatter(X[:, 0], X[:, 1], c=y, s=30, cmap='cool')
            plt.contourf(XX, YY, Z[idx], levels=[0, 0.5, 1], cmap='bwr', alpha=0.5, zorder=-1)
            plt.title(title)
            plt.xlim(-15, 15)
            plt.ylim(-15, 15)

        plt.subplot(338)
        plt.scatter(X[:, 0], X[:, 1], c=y, s=30, cmap='cool')
        plt.contourf(XX, YY, pred, levels=3, cmap='cool', alpha=0.5, zorder=-1)
        plt.xlim(-15, 15)
        plt.ylim(-15, 15)

    @staticmethod
    def one_vs_one():
        X, y = make_blobs(cluster_std=(1.5, 1.5, 1.5), random_state=42)

        xx = np.linspace(-15, 15, 200)
        yy = np.linspace(-15, 15, 200)
        XX, YY = np.meshgrid(xx, yy)
        X_grid = np.c_[XX.ravel(), YY.ravel()]

        plt.figure(figsize=(12, 12))

        plt.subplot(332)
        plt.scatter(X[:, 0], X[:, 1], c=y, s=30, cmap='cool')
        plt.title("One vs One\n", fontsize=25)
        plt.xlim(-15, 15)
        plt.ylim(-15, 15)

        Z = []
        for i in range(3):
            mask = (y != i)
            model = LogisticRegression(solver='lbfgs').fit(X[mask], y[mask])
            Z.append(model.predict(X_grid).reshape(XX.shape))
        pred = mode(np.stack(Z))[0]
        pred = pred.squeeze()

        for idx, title in enumerate(['B vs C', 'A vs C', 'A vs B']):
            mask = (y != idx)
            plt.subplot(3, 3, idx + 4)
            plt.scatter(X[mask, 0], X[mask, 1], c=y[mask], s=30, cmap='cool', vmin=0, vmax=2)
            plt.contourf(XX, YY, Z[idx], levels=2, cmap='bwr', alpha=0.5, zorder=-1)
            plt.title(title)
            plt.xlim(-15, 15)
            plt.ylim(-15, 15)

        plt.subplot(338)
        plt.scatter(X[:, 0], X[:, 1], c=y, s=30, cmap='cool')
        plt.contourf(XX, YY, pred, levels=3, cmap='cool', alpha=0.5, zorder=-1)
        plt.xlim(-15, 15)
        plt.ylim(-15, 15)

    @staticmethod
    def multinomial():
        def _simul(data='Mimic OVR'):
            if data == 'Mimic OVR':
                X, y = make_blobs(n_samples=200, centers=[[0, 3], [2, -2], [-2, -2]],
                                  cluster_std=(0.5, 0.5, 0.5), random_state=40)
            elif data == 'Mimic OVO':
                X, y = make_blobs(n_samples=200, centers=[[3, -1], [0, 1], [-3, -1]],
                                  cluster_std=((0.5, 1), (0.3, 2), (0.5, 1)), random_state=40)
            elif data == 'In between':
                X, y = make_blobs(n_samples=200, centers=[[0, 1], [3, -1], [-3, -1]],
                                  cluster_std=(0.5, 0.5, 0.5), random_state=40)

            plt.figure(figsize=(16, 5))

            model = LogisticRegression(multi_class='multinomial', solver='lbfgs').fit(X, y)
            Z1 = model.predict(X_grid).reshape(XX.shape)

            model = LogisticRegression(multi_class='ovr', solver='lbfgs').fit(X, y)
            Z2 = model.predict(X_grid).reshape(XX.shape)

            Z3 = []
            for i in range(3):
                mask = (y != i)
                model = LogisticRegression(solver='lbfgs').fit(X[mask], y[mask])
                Z3.append(model.predict(X_grid).reshape(XX.shape))
            Z3 = mode(np.stack(Z3))[0].squeeze()

            plt.subplot(131)
            plt.scatter(X[:, 0], X[:, 1], c=y, s=30, cmap='cool')
            plt.contourf(XX, YY, Z2, levels=3, cmap='cool', alpha=0.5, zorder=-1)
            plt.xlim(-5, 5)
            plt.ylim(-5, 5)
            plt.title("One-vs-Rest", fontsize=14)

            plt.subplot(132)
            plt.scatter(X[:, 0], X[:, 1], c=y, s=30, cmap='cool')
            plt.contourf(XX, YY, Z1, levels=3, cmap='cool', alpha=0.5, zorder=-1)
            plt.xlim(-5, 5)
            plt.ylim(-5, 5)
            plt.title("Multinomial", fontsize=14)

            plt.subplot(133)
            plt.scatter(X[:, 0], X[:, 1], c=y, s=30, cmap='cool')
            plt.contourf(XX, YY, Z3, levels=3, cmap='cool', alpha=0.5, zorder=-1)
            plt.xlim(-5, 5)
            plt.ylim(-5, 5)
            plt.title("One-vs-One", fontsize=14)

        xx = np.linspace(-5, 5, 200)
        yy = np.linspace(-5, 5, 200)
        XX, YY = np.meshgrid(xx, yy)
        X_grid = np.c_[XX.ravel(), YY.ravel()]
        interact(_simul, data=ToggleButtons(options=['Mimic OVR', 'Mimic OVO', 'In between'], description='data'));

    @staticmethod
    def ss_pr_tradeoff():
        def _simul(threshold=0.5, show_curve=False):
            x_t = (np.log(threshold / (1 - threshold)) - model.intercept_[0]) / model.coef_[0, 0]
            x_t = np.maximum(-5, np.minimum(10, x_t))
            prec, rcll, FP, FN = _calc_metric(prob, y, threshold)

            plt.figure(figsize=(16, 5))

            plt.subplot(131)
            plt.scatter(X, y, c=y, s=20, cmap='bwr')
            plt.plot(space, pred, "k-")
            plt.axvline(x_t, color='k', alpha=0.2, linewidth=1, linestyle='--')
            plt.axhline(threshold, color='k', alpha=0.2, linewidth=1, linestyle='--')
            plt.axvspan(-10, x_t, color='b', alpha=0.1)
            plt.axvspan(x_t, 10, color='r', alpha=0.1)
            plt.title(f"FP: {FP} | FN: {FN}\nPrec: {prec:.2f} | Rcll: {rcll:.2f}", fontsize=14)
            plt.xlabel("X");
            plt.ylabel("y");
            plt.xlim(-10, 10)

            if show_curve:
                plt.subplot(132)
                plt.plot(1 - fpr, tpr, 'b-', zorder=-1)
                fpr_roc = np.interp(threshold, t_roc[::-1], fpr[::-1])
                tpr_roc = np.interp(threshold, t_roc[::-1], tpr[::-1])
                plt.scatter(1 - fpr_roc, tpr_roc, c='r', s=50)
                plt.plot([0, 1], [1, 0], 'k--')
                plt.title("Sensitivity vs Specificity", fontsize=14)
                plt.xlim(-0.05, 1.05)
                plt.ylim(-0.05, 1.05)
                plt.xlabel("Specificity")
                plt.ylabel("Sensitivity")

                plt.subplot(133)
                plt.plot(r, p, 'b-', zorder=-1)
                p_pr = np.interp(threshold, t_pr, p[:-1])
                r_pr = np.interp(threshold, t_pr, r[:-1])
                plt.scatter(r_pr, p_pr, c='r', s=50)
                plt.plot([0, 0, 1], [1, 0.5, 0.5], 'k--')
                plt.title("Precision vs Recall", fontsize=14)
                plt.xlim(-0.05, 1.05)
                plt.ylim(0.45, 1.05)
                plt.xlabel("Recall")
                plt.ylabel("Precision")

        def _calc_metric(prob, y, threshold):
            pred = (prob > threshold).ravel()
            TP = np.sum((pred == 1) & (y == 1))
            FP = np.sum((pred == 1) & (y == 0))
            FN = np.sum((pred == 0) & (y == 1))
            prec = TP / (TP + FP)
            rcll = TP / (TP + FN)
            return prec, rcll, FP, FN

        space = np.linspace(-10, 10, 201)
        X, y = make_binary(std=(2, 2))
        model = LogisticRegression(solver='lbfgs').fit(X, y)
        pred = model.predict_proba(space.reshape(-1, 1))[:, 1]
        prob = model.predict_proba(X)[:, 1]
        fpr, tpr, t_roc = roc_curve(y, prob)
        p, r, t_pr = precision_recall_curve(y, prob)
        interact(_simul, threshold=SelectionSlider(value=0.5,
                                                   options=[0.01] + [round(0.05 * i, 2) for i in range(1, 20)] + [0.99],
                                                   description='pos sample', readout=True));

    @staticmethod
    def roc_pr_imbalance():
        def _simul(pos_sample=0.5, sep='separable', dat='many data', show_regression=False):
            sep = cond1[sep]
            dat = cond2[dat]

            X, y = make_binary(n_samples=dat, mean=(-sep / 2, sep / 2), pos_weight=pos_sample)
            model = LogisticRegression(solver='lbfgs').fit(X, y)
            prob = model.predict_proba(X)[:, 1]
            coef = model.coef_[0, 0]
            x_t = -model.intercept_[0] / coef
            fpr, tpr, t_roc = roc_curve(y, prob)
            p, r, t_pr = precision_recall_curve(y, prob)
            AP = average_precision_score(y, prob)

            plt.figure(figsize=(16, 5))

            plt.subplot(131)
            plt.scatter(X, y, s=5, c=y, cmap='bwr')
            xmin, xmax = plt.xlim()
            plt.axvline(x_t, color='k', linestyle='--', linewidth=1, alpha=0.5)

            if coef > 0:
                plt.axvspan(xmin, x_t, color='b', alpha=0.1)
                plt.axvspan(x_t, xmax, color='r', alpha=0.1)
            else:
                plt.axvspan(xmin, x_t, color='r', alpha=0.1)
                plt.axvspan(x_t, xmax, color='b', alpha=0.1)

            if show_regression:
                space = np.linspace(xmin, xmax, 100).reshape(-1, 1)
                plt.plot(space, model.predict_proba(space)[:, 1], 'k-')
            plt.xlim(xmin, xmax)
            plt.xlabel("X")
            plt.ylabel("y")

            plt.subplot(132)
            plt.plot(fpr, tpr, 'b-')
            plt.plot([0, 1], [0, 1], 'k--')
            plt.title(f"ROC_AUC: {auc(fpr, tpr):.3f}", fontsize=14)
            plt.xlim(-0.05, 1.05)
            plt.ylim(-0.05, 1.05)
            plt.xlabel("FPR")
            plt.ylabel("TPR")

            plt.subplot(133)
            plt.plot(r, p, 'b-')
            plt.plot([0, 0, 1], [1, pos_sample, pos_sample], 'k--')
            plt.title(f"PR_AUC: {auc(r, p):.3f} | AP: {AP:.3f}", fontsize=14);
            plt.xlim(-0.05, 1.05)
            plt.ylim(pos_sample - 0.05, 1.05)
            plt.xlabel("Recall")
            plt.ylabel("Precision")

        cond1 = {'separable': 10, 'slightly mixed': 3, 'mixed': 0}
        cond2 = {'many data': 3000, 'lack data': 100}
        pos_button = SelectionSlider(value=0.5, options=[0.01, 0.05, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 0.95, 0.99],
                                     description='pos sample', readout=True)
        sep_button = ToggleButtons(value='separable', options=['separable', 'slightly mixed', 'mixed'],
                                   description='Condition 1')
        data_button = ToggleButtons(value='many data', options=['lack data', 'many data'], description='Condition 2')
        interact(_simul, pos_sample=pos_button, sep=sep_button, dat=data_button)


class BaseIllustrationLogisticRegression:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.predict_proba = Image(f"{here}/assets/predict_proba.png", width=800)
        self.one_vs_rest = Image(f"{here}/assets/ovr.png", width=800)
        self.one_vs_one = Image(f"{here}/assets/ovo.png", width=800)
        self.multinomial = Image(f"{here}/assets/multinomial.png", width=900)
        self.mushroom= Image(f"{here}/assets/mushroom.png", width=600)
