import tensorflow as tf
import sparsity_pattern


def get_sparsity_pattern(sp: str, *args, **kwargs) -> tf.Tensor:
    # call sparsity-pattern package
    arr = sparsity_pattern.get(sp, *args, **kwargs)
    # convert to Tensor
    return tf.convert_to_tensor(arr, dtype=tf.int64)
