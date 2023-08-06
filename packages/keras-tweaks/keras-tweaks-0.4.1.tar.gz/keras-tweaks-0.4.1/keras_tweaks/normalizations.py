import tensorflow as tf
from typing import Optional


def get(method: str, *args, **kwargs):
    if method in ("layernorm"):  # https://arxiv.org/abs/1607.06450
        return tf.keras.layers.LayerNormalization(
            *args, **kwargs, axis=-1, scale=True, center=True)
    elif method in ("layernorm-nobias"):
        return tf.keras.layers.LayerNormalization(
            *args, **kwargs, axis=-1, scale=True, center=True)
    elif method in ("unitnorm"):
        return tf.keras.layers.UnitNormalization(
            *args, **kwargs, axis=-1)
    elif method in ("scalenorm"):
        return ScaleNorm(*args, **kwargs, axis=-1)


class ScaleNorm(tf.keras.layers.Layer):
    """ScaleNorm by Nguyen/Salazar
    Parameters:
    -----------
    eps : Optional[float]
        Minimum size of the denominator (default: 1e-6)
    Learned:
    --------
    weight : float
        The radius ("g") is the only weight that must be learned.
    Literature:
    -----------
    Nguyen and Salazar (2019), URL: https://arxiv.org/pdf/1910.05895
    """
    def __init__(self,
                 axis: Optional[int] = -1,
                 eps: Optional[float] = 1e-6):
        super(ScaleNorm, self).__init__()
        self.axis = axis
        self.eps = tf.constant(eps)
        self.weight = tf.Variable(1.0)

    def call(self, x):
        return self.weight * x / tf.clip_by_value(
            tf.norm(x, axis=self.axis, keepdims=True), 
            clip_value_min=self.eps,
            clip_value_max=1. / self.eps)
