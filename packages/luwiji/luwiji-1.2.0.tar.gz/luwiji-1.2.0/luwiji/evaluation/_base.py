import pandas as pd
from sklearn.datasets import load_iris, make_classification
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

from luwiji.dataset.regression import make_poly

import os
from IPython.display import Image


class BaseDemoEval:
    def __init__(self):
        pass

    @staticmethod
    def get_regression_data():
        X_train, X_test, y_train, y_test = make_poly(noise=0.2, test_size=0.2)

        model = Pipeline([
            ("poly", PolynomialFeatures(5)),
            ("linreg", LinearRegression())
        ])
        model.fit(X_train, y_train);
        return X_train, y_train, X_test, y_test, model

    @staticmethod
    def get_classification_data():
        X, y = load_iris(return_X_y=True)
        X = pd.DataFrame(X, columns=["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"])
        y = pd.Series(y).map({0: 'setosa', 1: 'versicolor', 2: 'virginica'})

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

        model = LogisticRegression(multi_class='ovr', solver='lbfgs', C=3)
        model.fit(X_train, y_train)
        return X_train, y_train, X_test, y_test, model

    @staticmethod
    def get_binary_class_data():
        X, y = make_classification(n_samples=1000, class_sep=0.5, n_informative=8, n_clusters_per_class=1, flip_y=0.05, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

        model = LogisticRegression(solver='lbfgs')
        model.fit(X_train, y_train)
        return X_train, y_train, X_test, y_test, model


class BaseIllustrationEval:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.avp_underfit = Image(f"{here}/assets/avp_underfit.png", width=700)
        self.avp_overfit = Image(f"{here}/assets/avp_overfit.png", width=700)
        self.overlay_regression = Image(f"{here}/assets/overlay_regression.png", width=700)
        self.overlay_classification= Image(f"{here}/assets/overlay_classification.png", width=300)
        self.roc = Image(f"{here}/assets/roc.png", width=600)
        self.roc_auc = Image(f"{here}/assets/roc_auc.png", width=600)
        self.precision_recall = Image(f"{here}/assets/pr.png", width=600)
