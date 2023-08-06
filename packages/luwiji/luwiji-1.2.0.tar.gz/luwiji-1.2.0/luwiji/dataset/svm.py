import numpy as np
import pandas as pd


def gen_data_1():
    st1 = np.random.RandomState(0)
    st2 = np.random.RandomState(1)

    tmp = [(i, j) for i, j in zip(0.2 + 2.8 * st1.rand(1000), 0.2 + 2.8 * st2.rand(1000)) if (i + j) < 2.5][:60]
    x1 = [i[0] for i in tmp]
    x2 = [i[1] for i in tmp]

    tmp = [(i, j) for i, j in zip(0.2 + 2.8 * st1.rand(1000), 0.2 + 2.8 * st2.rand(1000)) if (i + j) < 3.25][:10]
    x1 += [i[0] for i in tmp]
    x2 += [i[1] for i in tmp]
    l1 = [0] * len(x1)

    tmp = [(i, j) for i, j in zip(1 + 2.8 * st1.rand(1000), 1 + 2.8 * st2.rand(1000)) if (i + j) > 5.5][:60]
    x3 = [i[0] for i in tmp]
    x4 = [i[1] for i in tmp]

    tmp = [(i, j) for i, j in zip(1 + 2.8 * st1.rand(1000), 1 + 2.8 * st2.rand(1000)) if (i + j) > 4.75][:10]
    x3 += [i[0] for i in tmp]
    x4 += [i[1] for i in tmp]
    l2 = [1] * len(x3)

    x = np.array(x1 + x3)
    y = np.array(x2 + x4)
    label = np.array(l1 + l2)
    return _create_df(x, y, label)


def gen_data_2():
    st1 = np.random.RandomState(0)
    st2 = np.random.RandomState(1)

    theta = 2 * np.pi * st1.rand(100)
    R = 2 * st2.rand(100)

    x1 = R * np.cos(theta)
    x2 = R * np.sin(theta)
    l1 = np.zeros_like(x1)

    theta = 2 * np.pi * st2.rand(200)
    R = 2.5 + 0.5 * st1.rand(200)

    x3 = R * np.cos(theta)
    x4 = R * np.sin(theta)
    l2 = np.ones_like(x3)

    x = np.hstack([x1, x3])
    y = np.hstack([x2, x4])
    label = np.hstack([l1, l2]).astype(int)
    return _create_df(x, y, label)


def gen_data_3():
    x1, x2 = _flower()
    l1 = np.zeros_like(x1)

    x3, x4 = _blob(0.24, 0.08)
    l2 = np.ones_like(x3)

    x5, x6 = _blob(0.08, 0.24)
    l3 = np.ones_like(x5)

    x = np.hstack([x1, x3, x5])
    y = np.hstack([x2, x4, x6])
    label = np.hstack([l1, l2, l3]).astype(int)
    return _create_df(x, y, label)


def _create_df(x, y, label):
    df = pd.DataFrame({"x_1": x, "x_2": y, "label": label})
    df = df.sample(frac=1).reset_index(drop=True)
    return df


def _blob(std_x, std_y, n_data=200):
    st1 = np.random.RandomState(0)
    st2 = np.random.RandomState(1)

    theta = 2 * np.pi * st1.rand(n_data)
    R = st2.rand(n_data)

    x = std_x * R * np.cos(theta)
    y = std_y * R * np.sin(theta)
    return x, y


def _flower(bias=0.2, std=0.12, mult=0.06, n_petal=4, n_data=500):
    st1 = np.random.RandomState(0)
    st2 = np.random.RandomState(1)

    theta = 2 * np.pi * st1.rand(n_data)
    noise = std * st2.rand(n_data) + bias
    R = noise + mult * np.cos(n_petal * theta)

    x = R * np.cos(theta)
    y = R * np.sin(theta)
    return x, y
