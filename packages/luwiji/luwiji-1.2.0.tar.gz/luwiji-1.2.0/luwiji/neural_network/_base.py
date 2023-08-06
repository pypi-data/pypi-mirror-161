import numpy as np
import matplotlib.pyplot as plt
import os
import torch
from IPython.display import Image, display, clear_output
from collections import deque
torch.manual_seed(42)


class BaseDemoNeuralNetwork:
    def __init__(self):
        self._space = np.linspace(0, 6, 100)
        self._lr = 0.01
        self._m = 0.95

        self.example_data_1 = np.random.randint(0, 255, size=(3, 5, 5))
        self.example_data_2 = torch.tensor(5)

        tmp = torch.rand(15, 3).exp()
        self.example_data_3 = tmp / tmp.sum(1, keepdim=True)

    @staticmethod
    def _f(x):
        x = np.array(x)
        return 40 - 36*x + 26.4*x**2 - 7*x**3 + 0.6*x**4

    @staticmethod
    def _df(x):
        x = np.array(x)
        return -36 + 52.84*x - 21*x**2 + 2.4*x**3

    def momentum(self):
        guess = deque(maxlen=5)
        guess_m = deque(maxlen=5)
        guess.append(0)
        guess_m.append(0)

        v = 0

        plt.figure(figsize=(7, 5))
        plt.plot(self._space, self._f(self._space), 'b')
        a = plt.scatter([], [], c='r', label='GD')
        a_m = plt.scatter([], [], c='g', label='GD+Mom')
        plt.legend()

        for i in range(100):
            guess.append(guess[-1] - self._lr * self._df(guess[-1]))
            a.set_offsets(np.array([guess, self._f(guess)]).T)

            v = self._m * v + self._df(guess_m[-1])
            guess_m.append(guess_m[-1] - self._lr * v)
            a_m.set_offsets(np.array([guess_m, self._f(guess_m)]).T)

            display(plt.gcf())
            clear_output(wait=True)


class BaseIllustrationNeuralNetwork:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.deep_learning = Image(f"{here}/assets/deep_learning.png", width=800)
        self.node_linear = Image(f"{here}/assets/node_linear.png", width=300)
        self.node_representation= Image(f"{here}/assets/node_representation.png", width=800)
        self.regressor = Image(f"{here}/assets/nn_regressor.png", width=500)
        self.classifier = Image(f"{here}/assets/nn_classifier.png", width=500)
        self.vocab = Image(f"{here}/assets/nn_vocab.png", width=600)
        self.layer = Image(f"{here}/assets/nn_layer.png", width=600)
        self.quiz = Image(f"{here}/assets/nn_quiz.png", width=900)
        self.activation = Image(f"{here}/assets/activation.png", width=900)
        self.think_wide = Image(f"{here}/assets/think_wide.png", width=800)
        self.think_deep = Image(f"{here}/assets/think_deep.png", width=800)
        self.less_feature = Image(f"{here}/assets/less_feature.png", width=800)
        self.spiral_genius = Image(f"{here}/assets/spiral_genius.png", width=800)
        self.dropout_idea = Image(f"{here}/assets/dropout0.png", width=800)
        self.dropout = Image(f"{here}/assets/dropout1.png", width=800)
        self.dropout_balance = Image(f"{here}/assets/dropout2.png", width=400)
        self.regression_loop = Image(f"{here}/assets/regression_loop.png", width=800)
        self.neural_network_loop = Image(f"{here}/assets/neural_network_loop.png", width=800)
        self.pytorch = Image(f"{here}/assets/pytorch.png", width=900)
        self.pytorch_testimony = Image(f"{here}/assets/pytorch_testimony.jpg", width=700)
        self.nomenklatur = Image(f"{here}/assets/nomenklatur.png", width=800)
        self.minibatch = Image(f"{here}/assets/minibatch.png", width=800)
        self.minibatch_training = Image(f"{here}/assets/minibatch_training.png", width=800)
