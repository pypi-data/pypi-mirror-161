import os
from IPython.display import Image

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from ipywidgets import interact
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_process import ArmaProcess


class BaseDemoTimeSeries:
    def __init__(self):
        self._generate_data(seed=42)

    def _generate_data(self, seed):
        np.random.seed(seed)
        sample = ArmaProcess([1, -0.5], None).generate_sample(150)
        self.stnry_data = pd.Series(sample)

        sample = ArmaProcess([1, -0.8], None).generate_sample(150)
        self.trending_data = pd.Series(sample) + 0.1 * np.arange(len(sample))

    @staticmethod
    def AR_example(seed=42):
        np.random.seed(seed)
        plt.figure(figsize=(16, 7))

        sample = ArmaProcess([1, -0.6], None).generate_sample(150)
        plt.subplot(231)
        plt.plot(sample)
        plt.title("AR(1)")

        plt.subplot(232)
        sample = ArmaProcess([1, -0.8], None).generate_sample(150)
        plt.plot(sample)
        plt.title("AR(1)")

        plt.subplot(233)
        sample = ArmaProcess([1, 0.4], None).generate_sample(150)
        plt.plot(sample)
        plt.title("AR(1)")

        sample = ArmaProcess([1, -0.6, -0.3], None).generate_sample(150)
        plt.subplot(234)
        plt.plot(sample)
        plt.title("AR(2)")

        plt.subplot(235)
        sample = ArmaProcess([1, -0.8, 0.2], None).generate_sample(150)
        plt.plot(sample)
        plt.title("AR(2)")

        plt.subplot(236)
        sample = ArmaProcess([1, 0.4, -0.5], None).generate_sample(150)
        plt.plot(sample)
        plt.title("AR(2)")

    @staticmethod
    def MA_example(seed=42):
        np.random.seed(seed)
        plt.figure(figsize=(16, 7))

        sample = ArmaProcess(None, [1, 0.6]).generate_sample(150)
        plt.subplot(231)
        plt.plot(sample)
        plt.title("MA(1)")

        plt.subplot(232)
        sample = ArmaProcess(None, [1, 0.8]).generate_sample(150)
        plt.plot(sample)
        plt.title("MA(1)")

        plt.subplot(233)
        sample = ArmaProcess(None, [1, -0.4]).generate_sample(150)
        plt.plot(sample)
        plt.title("MA(1)")

        sample = ArmaProcess(None, [1, 0.6, 0.3]).generate_sample(150)
        plt.subplot(234)
        plt.plot(sample)
        plt.title("MA(2)")

        plt.subplot(235)
        sample = ArmaProcess(None, [1, 0.8, -0.2]).generate_sample(150)
        plt.plot(sample)
        plt.title("MA(2)")

        plt.subplot(236)
        sample = ArmaProcess(None, [1, 0.4, -0.5]).generate_sample(150)
        plt.plot(sample)
        plt.title("MA(2)")

    @staticmethod
    def _plot(process, diff=False):
        sample = process.generate_sample(150)
        if diff:
            sample = pd.Series(sample).diff().dropna()

        plt.figure(figsize=(15, 8))
        plt.subplot(211)
        plt.plot(sample, "b-")
        plt.title(f"Stationarity: {process.isstationary}", fontsize=14)

        ax1 = plt.subplot(223)
        plot_acf(sample, lags=50, ax=ax1, title="ACF", color="b", alpha=None);

        ax2 = plt.subplot(224)
        plot_pacf(sample, lags=50, ax=ax2, title="PACF", color="r", alpha=None);

    def AR1_simulation(self):
        def _simul(alpha1=0.6):
            process = ArmaProcess([1, -alpha1], None)
            self._plot(process)

        interact(_simul, alpha1=(-2, 2, 0.1))

    def AR2_simulation(self):
        def _simul(alpha1=0.5, alpha2=0.3):
            process = ArmaProcess([1, -alpha1, -alpha2], None)
            self._plot(process)

        interact(_simul, alpha1=(-2, 2, 0.1), alpha2=(-2, 2, 0.1))

    def MA1_simulation(self):
        def _simul(theta1=0.6):
            process = ArmaProcess(None, [1, theta1])
            self._plot(process)

        interact(_simul, theta1=(-2, 2, 0.1))

    def MA2_simulation(self):
        def _simul(theta1=0.6, theta2=0.6):
            process = ArmaProcess(None, [1, theta1, theta2])
            self._plot(process)

        interact(_simul, theta1=(-2, 2, 0.1), theta2=(-2, 2, 0.1))

    def AR2MA2_simulation(self):
        def _simul(alpha1=0.7, alpha2=-0.4, theta1=0.8, theta2=-0.5):
            process = ArmaProcess([1, -alpha1, -alpha2], [1, theta1, theta2])
            self._plot(process)

        interact(_simul, alpha1=(-2, 2, 0.1), alpha2=(-2, 2, 0.1), theta1=(-2, 2, 0.1), theta2=(-2, 2, 0.1))

    def nonstationarity_simulation(self, diff=False, seed=42):
        np.random.seed(seed)
        process = ArmaProcess([1, -0.7, -0.3], None)
        self._plot(process, diff)


class BaseIllustrationTimeSeries:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.ets_model = Image(f"{here}/assets/ets_model.png", width=800)
        self.stationarity_quiz = Image(f"{here}/assets/stationarity.png", width=850)
        self.autocorrelation = Image(f"{here}/assets/autocorrelation.png", width=850)
