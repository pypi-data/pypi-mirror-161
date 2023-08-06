import tensorflow as tf
from keras_tweaks import normalizations


class TestSparsityPattern(tf.test.TestCase):
    def test10(self):
        x = tf.random.normal((3, 4, 5))
        layer = normalizations.get('layernorm')
        y = layer(x)
        assert x.shape == y.shape
        assert not tf.reduce_any(tf.math.is_nan(y))

    def test11(self):
        ln_config = {
            'epsilon': 1e-5,
            'beta_initializer': 'zeros',
            'beta_regularizer': tf.keras.regularizers.L1(0.01),
            'beta_constraint': tf.keras.constraints.MinMaxNorm(-1., 1.),
            'gamma_initializer': 'ones',
            'gamma_regularizer': tf.keras.regularizers.L2(0.01),
            'gamma_constraint': 'non_neg',
            'dtype': tf.float32,
            'trainable': True
        }
        x = tf.random.normal((3, 4, 5))
        layer = normalizations.get('layernorm', **ln_config)
        y = layer(x)
        assert x.shape == y.shape
        assert not tf.reduce_any(tf.math.is_nan(y))

    def test20(self):
        x = tf.random.normal((3, 4, 5))
        layer = normalizations.get('layernorm-nobias')
        y = layer(x)
        assert x.shape == y.shape
        assert not tf.reduce_any(tf.math.is_nan(y))

    def test30(self):
        x = tf.random.normal((3, 4, 5))
        layer = normalizations.get('scalenorm')
        y = layer(x)
        assert x.shape == y.shape
        assert not tf.reduce_any(tf.math.is_nan(y))

    def test31(self):
        x = tf.random.normal((3, 4, 5))
        layer = normalizations.get('scalenorm', eps=1e-4)
        y = layer(x)
        assert x.shape == y.shape
        assert not tf.reduce_any(tf.math.is_nan(y))
