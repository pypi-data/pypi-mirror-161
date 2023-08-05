# tools from book: ISLR Seventh printing
import numpy as np

y = [1, 2, 3, 4, 5]
fx = [2, 3, 4, 5, 6]


def mean_squared_error(y, fx):
    y = np.array(y)
    fx = np.array(fx)
    return np.average((y - fx) ** 2)

