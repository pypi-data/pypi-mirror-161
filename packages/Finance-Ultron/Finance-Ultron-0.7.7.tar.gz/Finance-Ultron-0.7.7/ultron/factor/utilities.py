import base64
import math
import pickle

import numpy as np
import numba as nb



@nb.njit(nogil=True, cache=True)
def simple_abssum(x, axis=0):
    length, width = x.shape

    if axis == 0:
        res = np.zeros(width)
        for i in range(length):
            for j in range(width):
                res[j] += abs(x[i, j])

    elif axis == 1:
        res = np.zeros(length)
        for i in range(length):
            for j in range(width):
                res[i] += abs(x[i, j])
    else:
        raise ValueError("axis value is not supported")
    return res


@nb.njit(nogil=True, cache=True)
def group_mapping(groups: np.ndarray) -> np.ndarray:
    length = groups.shape[0]
    order = groups.argsort()
    res = np.zeros(length, dtype=order.dtype)

    start = 0
    res[order[0]] = start
    previous = groups[order[0]]

    for i in range(1, length):
        curr_idx = order[i]
        curr_val = groups[curr_idx]
        if curr_val != previous:
            start += 1
            res[curr_idx] = start
        else:
            res[curr_idx] = start
        previous = curr_val
    return res


@nb.njit(nogil=True, cache=True)
def agg_std(groups, x, ddof=1):
    max_g = groups.max()
    length, width = x.shape
    res = np.zeros((max_g + 1, width), dtype=np.float64)
    sumsq = np.zeros((max_g + 1, width), dtype=np.float64)
    bin_count = np.zeros(max_g + 1, dtype=np.int32)

    for i in range(length):
        for j in range(width):
            res[groups[i], j] += x[i, j]
            sumsq[groups[i], j] += x[i, j] * x[i, j]
        bin_count[groups[i]] += 1

    for i in range(max_g + 1):
        curr = bin_count[i]
        for j in range(width):
            res[i, j] = math.sqrt((sumsq[i, j] - res[i, j] * res[i, j] / curr) / (curr - ddof))
    return res


@nb.njit(nogil=True, cache=True)
def agg_sum(groups, x):
    max_g = groups.max()
    length, width = x.shape
    res = np.zeros((max_g + 1, width), dtype=np.float64)

    for i in range(length):
        for j in range(width):
            res[groups[i], j] += x[i, j]
    return res


@nb.njit(nogil=True, cache=True)
def agg_sqrsum(groups, x):
    max_g = groups.max()
    length, width = x.shape
    res = np.zeros((max_g + 1, width), dtype=np.float64)

    for i in range(length):
        for j in range(width):
            res[groups[i], j] += x[i, j] * x[i, j]

    res = np.sqrt(res)
    return res


@nb.njit(nogil=True, cache=True)
def agg_abssum(groups, x):
    max_g = groups.max()
    length, width = x.shape
    res = np.zeros((max_g + 1, width), dtype=np.float64)

    for i in range(length):
        for j in range(width):
            res[groups[i], j] += abs(x[i, j])
    return res


@nb.njit(nogil=True, cache=True)
def agg_mean(groups, x):
    max_g = groups.max()
    length, width = x.shape
    res = np.zeros((max_g+1, width), dtype=np.float64)
    bin_count = np.zeros(max_g+1, dtype=np.int32)

    for i in range(length):
        for j in range(width):
            res[groups[i], j] += x[i, j]
        bin_count[groups[i]] += 1

    for i in range(max_g+1):
        curr = bin_count[i]
        for j in range(width):
            res[i, j] /= curr
    return res

@nb.njit(nogil=True, cache=True)
def copy_value(groups, source):
    length = groups.shape[0]
    width = source.shape[1]
    destination = np.zeros((length, width))
    for i in range(length):
        k = groups[i]
        for j in range(width):
            destination[i, j] = source[k, j]
    return destination


@nb.njit(nogil=True, cache=True)
def scale_value(groups, source, x, scale):
    length, width = x.shape
    destination = x.copy()
    for i in range(length):
        k = groups[i]
        for j in range(width):
            destination[i, j] /= source[k, j] / scale
    return destination


def encode(obj: object) -> str:
    encoded = base64.encodebytes(pickle.dumps(obj))
    return encoded.decode('ascii')


def decode(str_repr: str):
    encoded = str_repr.encode('ascii')
    return pickle.loads(base64.decodebytes(encoded))

def list_eq(lhs: list, rhs: list):
    if not lhs and not rhs:
        return True

    if len(lhs) != len(rhs):
        return False

    for i, v1 in enumerate(lhs):
        if v1 != rhs[i]:
            return False
    return True

def transform(groups: np.ndarray,
              x: np.ndarray,
              func: str,
              ddof: int = 1,
              scale: float = 1.) -> np.ndarray:
    if func == 'mean':
        value_data = agg_mean(groups, x)
    elif func == 'std':
        value_data = agg_std(groups, x, ddof=ddof)
    elif func == 'sum':
        value_data = agg_sum(groups, x)
    elif func == 'abssum' or func == 'scale':
        value_data = agg_abssum(groups, x)
    elif func == 'sqrsum' or func == 'project':
        value_data = agg_sqrsum(groups, x)
    else:
        raise ValueError('({0}) is not recognized as valid functor'.format(func))

    if func == 'scale' or func == 'project':
        return scale_value(groups, value_data, x, scale)
    else:
        return copy_value(groups, value_data)
