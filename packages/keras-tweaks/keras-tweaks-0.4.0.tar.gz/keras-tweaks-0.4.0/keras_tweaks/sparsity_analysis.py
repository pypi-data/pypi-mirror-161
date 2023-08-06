import tensorflow as tf
import numpy as np
from .dense_sparse_matmul import dense_sparse_matmul


def shortest_path_to_origin(W: tf.Tensor, max_recur: int):
    dim = W.shape[0]
    assert W.shape[0] == W.shape[1]
    # start
    res = []
    for origin in tf.range(dim):
        s = np.zeros((1, dim), dtype=np.int32)
        s[0, origin] = 1
        s = tf.constant(s)
        # find shortest path
        pathlen = None
        for t in range(1, max_recur + 1):
            s = (dense_sparse_matmul(s, W) > 0)
            s = tf.cast(s, tf.int32)
            if s[0, origin] == 1:
                pathlen = t
                break
        # save
        res.append(pathlen)
    # done
    return res


def feedback_signal_patterns(W: tf.Tensor, max_recur: int):
    dim = W.shape[0]
    assert W.shape[0] == W.shape[1]
    ts = np.zeros((dim, max_recur), dtype=np.int8)
    # start
    for origin in tf.range(dim):
        s = np.zeros((1, dim), dtype=np.int32)
        s[0, origin] = 1
        s = tf.constant(s)
        # simulate
        for t in range(max_recur):
            s = (dense_sparse_matmul(s, W) > 0)
            s = tf.cast(s, tf.int32)
            # s = dense_sparse_matmul(s, W)
            if s[0, origin]:
                ts[origin, t] = 1
    # done
    return ts
