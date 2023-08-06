import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact


class BaseDemoMinibatch:
    def __init__(self):
        pass

    def gradient_descent(self):
        def _simul(batch_size=100):
            ans = self.mbgd(x, y, batch_size)
            if batch_size == 100:
                title = "Gradient Descent (GD)"
            elif batch_size == 1:
                title = "Stochastic Gradient Descent (SGD)"
            else:
                title = "Minibatch Gradient Descent"
            plt.figure(figsize=(6, 6))
            plt.contourf(AA, BB, err, levels=30, cmap="Greens")
            plt.contour(AA, BB, err, levels=30)
            plt.plot(ans[:, 0], ans[:, 1], "r-")
            plt.title(f"Method: {title}", fontsize=14)

        a, b = 2, 5
        X = 6 * np.random.RandomState(42).rand(100, 1) - 3
        y = a * X + b + (2 * np.random.random(X.shape) - 1)

        A = np.linspace(a - 3, a + 3, 100)
        B = np.linspace(b - 3, b + 3, 100)
        AA, BB = np.meshgrid(A, B)

        w = np.c_[AA.ravel(), BB.ravel()]
        x = np.hstack([X, np.ones_like(X)])
        err = ((x @ w.T - y) ** 2).mean(0).reshape(AA.shape)
        interact(_simul, batch_size=(1, 100, 5))

    @staticmethod
    def mbgd(x, y, bs, alpha=0.03):
        ans = []
        guess = np.array([[0, 7]])
        for _ in range(100):
            n_batch = 100 // bs
            for i in range(n_batch):
                start = i * bs
                end = (i + 1) * bs
                ans.append(guess[0])
                guess = guess - alpha * 2 * ((x[start:end] @ guess.T - y[start:end]) * x[start:end]).mean(0)
        return np.array(ans)

    @staticmethod
    def gd(alpha=0.03):
        ans = []
        guess = np.array([[0, 7]])
        for _ in range(100):
            ans.append(guess[0])
            guess = guess - alpha * 2 * ((x @ guess.T - y) * x).mean(0)
        return np.array(ans)

    def sgd(self, alpha=0.03):
        return self.mbgd(1, alpha)
