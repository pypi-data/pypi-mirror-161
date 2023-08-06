import numpy as np
from sklearn.model_selection import train_test_split


def make_linear(n_samples=100, coef=(3, 0), noise=0.1, span=(0, 5), test_size=0, random_state=None):
    assert len(coef) == 2
    return make_poly(n_samples, coef, noise, span, test_size, random_state=random_state)


def make_quadratic(n_samples=100, coef=(1, -3.5, 10), noise=0.1, span=(0, 5), test_size=0, random_state=None):
    assert len(coef) == 3
    return make_poly(n_samples, coef, noise, span, test_size, random_state=random_state)


def make_poly(n_samples=100, coef=(-0.2, 2, -6, 4.5, 20), noise=0.01, span=(0, 5), test_size=0, random_state=None):
    assert test_size >= 0
    if random_state is not None:
        np.random.seed(random_state)
    X = np.linspace(span[0], span[1], n_samples)
    y = noise * np.random.randn(n_samples)
    for i, c in enumerate(coef, 1):
        y += c * X ** (len(coef) - i)
    if test_size > 0:
        if random_state is not None:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
        X_train = X_train.reshape(-1, 1)
        X_test = X_test.reshape(-1, 1)
        return X_train, X_test, y_train, y_test
    else:
        return X, y


def make_sine(n_samples=100, coef=(1, 1), noise=0.5, span=(0, 5), test_size=0, random_state=None):
    assert len(coef) == 2
    assert test_size >= 0
    if random_state is not None:
        np.random.seed(random_state)
    X = np.linspace(span[0], span[1], n_samples)
    y = noise * np.random.randn(n_samples)
    y += coef[0] * np.sin(coef[1] * X)
    if test_size > 0:
        if random_state is not None:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
        X_train = X_train.reshape(-1, 1)
        X_test = X_test.reshape(-1, 1)
        return X_train, X_test, y_train, y_test
    else:
        return X, y


def mountain(x, y):
    Z = peak(x, y, shift=(-20, 0), c=(0.004, 0, 0.002), A=1.0)
    Z -= peak(x, y, shift=(20, 0), c=(0.002, 0, 0.002), A=1.0)
    return Z


def peak(x, y, shift=(5, 5), c=(0, 0, 0), A=1., b=0):
    x = x - shift[0]
    y = y - shift[1]
    return b + A * np.exp(-(c[0]*x**2 + 2*c[1]*x*y + c[2]*y**2))


def dZ(x, y):
    dx = (mountain(x+1e-5, y) - mountain(x-1e-5, y)) / 2e-5
    dy = (mountain(x, y+1e-5) - mountain(x, y-1e-5)) / 2e-5
    return dx, dy


def make_binary(mean=(-3, 3), std=(1, 1), n_samples=500, pos_weight=0.5, random_state=42):
    c1, c2 = mean
    std1, std2 = std
    state = np.random.RandomState(random_state)

    x1 = std1 * state.randn(int((1 - pos_weight) * n_samples)) + c1
    y1 = np.zeros_like(x1)
    x2 = std2 * state.randn(int(pos_weight * n_samples)) + c2
    y2 = np.ones_like(x2)

    X = np.hstack([x1, x2]).reshape(-1, 1)
    y = np.hstack([y1, y2])
    return X, y
