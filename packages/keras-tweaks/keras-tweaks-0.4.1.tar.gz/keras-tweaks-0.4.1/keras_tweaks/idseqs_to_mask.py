import tensorflow as tf
import itertools
from typing import List, Optional, Union
Number = Union[bool, int, float]


def idseqs_to_mask(idseqs: List[List[int]],
                   n_seqlen: Optional[int] = None,
                   n_vocab_sz: Optional[int] = None,
                   ignore: Optional[List[int]] = [],
                   dtype: Optional[tf.dtypes.DType] = tf.bool,
                   dense: Optional[bool] = False
                   ) -> tf.sparse.SparseTensor:
    """Convert ID sequences into mask matrices

    Parameter:
    ----------
    idseqs: List[List[int]]
        A list of ID sequences. Each ID basically a row-index.
          It's assumed that sequences are already padded!

    n_seqlen: Optional[int] = None
        The expected sequence length.

    n_vocab_sz: Optional[int] = None
        The number distinct IDs of all sequences.

    ignore: Optional[List[int]] = []
        A list of IDs to ignore, e.g. ignore=[VOCAB.index("[PAD]")]
          As a result the empty rows of the mask matrix are removed
          accordingly.

    dtype: Optional[tf.dtype] = tf.bool
        The data type of the mask matrix, e.g. tf.bool (True/False),
          tf.uint8 (0/1), tf.float16 (0.0, 1.0)

    dense: Optional[bool] = False
        Flag to return a dense mask matrix

    Returns:
    --------
    tf.sparse.SparseTensor
        A batch-first SparseTensor <batch_sz, n_seqlen, vocab_sz>

    Example:
    --------
        import tensorflow as tf
        from keras_tweaks import idseqs_to_mask
        idseqs = [[1,2,3,4,0,0,1,2], [2,4,2,0,1]]
        masks = idseqs_to_mask(idseqs, n_seqlen=5, ignore=[3], dtype=tf.uint8)
        tf.sparse.to_dense(masks)

    Help:
    -----
    - Sparse module: https://www.tensorflow.org/api_docs/python/tf/sparse
    - dtype: https://www.tensorflow.org/api_docs/python/tf/dtypes/DType
    """
    if n_seqlen is None:
        n_seqlen = max([len(seq) for seq in idseqs])

    # create a list of IDs
    if n_vocab_sz is None:
        ids = set(itertools.chain(*idseqs))
    else:
        ids = set(range(0, n_vocab_sz))

    # remove IDs that we ignore
    ids = ids.difference(set(ignore))
    n_features = len(ids)

    # convert to list to lookup with .index() method
    ids = list(ids)

    # loop over each ID sequence
    idx_triples = []
    for b, seq in enumerate(idseqs):
        # extract index pairs of the sparse matrix
        for s, elem in enumerate(seq[:n_seqlen]):
            try:
                idx_triples.append((b, s, ids.index(elem)))
            except Exception:
                pass

    # convert to 3D sparse matrix <batch_sz, n_seqlen, vocab_sz>
    masks = tf.sparse.SparseTensor(
        indices=idx_triples,
        values=tf.cast([1 for _ in range(len(idx_triples))], dtype=dtype),
        dense_shape=(len(idseqs), n_seqlen, n_features))

    # convert to dense matrix if requested
    if dense:
        masks = tf.sparse.to_dense(masks)

    # done
    return masks
