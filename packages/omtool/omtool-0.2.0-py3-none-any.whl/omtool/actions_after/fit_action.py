import numpy as np

DataType = dict[str, np.ndarray]


def fit_polynomial(data: DataType, degree: int, x: str, y: str) -> DataType:
    coeffs = np.polyfit(data[x], data[y], deg=degree)
    fit = np.zeros(shape=data[x].shape)

    while degree >= 0:
        fit += coeffs[-degree - 1] * data[x] ** degree

        degree -= 1

    data[y] = fit

    return data


def fit_action(data: DataType, fit_type: str = "polynomial", **kwargs) -> DataType:
    funcs = {"polynomial": fit_polynomial}

    return funcs.get(fit_type, fit_polynomial)(data, **kwargs)
