import tensorflow as tf
from keras_tweaks import (
    shortest_path_to_origin,
    feedback_signal_patterns
)
import sparsity_pattern
import random


class TestSparsityAnalysis(tf.test.TestCase):
    def test1(self):
        random.seed(0)
        dim = 5
        spat = sparsity_pattern.get('random', r=dim, c=dim, pct=.01)
        W = tf.sparse.SparseTensor(
            dense_shape=(dim, dim),
            indices=tf.convert_to_tensor(spat, dtype=tf.int64),
            values=tf.ones((len(spat), ), dtype=tf.int32),
        )
        max_recur = 10
        pathlens = shortest_path_to_origin(W, max_recur)
        self.assertAllEqual(pathlens, [3, 3, 3, 2, 2])
        signals = feedback_signal_patterns(W, max_recur)
        self.assertAllEqual(signals.shape, [dim, max_recur])
