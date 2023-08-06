from keras_tweaks import idseqs_to_mask
import tensorflow as tf


class AllTests(tf.test.TestCase):

    def test1(self):
        idseqs = [[1, 1, 0, 0, 2, 2, 3], [1, 3, 2, 1, 0, 0, 2]]

        target = tf.sparse.SparseTensor(
            indices=(
                [0, 0, 1],
                [0, 1, 1],
                [0, 2, 0],
                [0, 3, 0],
                [0, 4, 2],
                [0, 5, 2],
                [1, 0, 1],
                [1, 2, 2],
                [1, 3, 1],
                [1, 4, 0],
                [1, 5, 0]),
            values=[True for _ in range(11)],
            dense_shape=(2, 6, 3))

        masks = idseqs_to_mask(
            idseqs, n_seqlen=6, n_vocab_sz=3, ignore=[3], dense=False)

        self.assertAllEqual(
            tf.sparse.to_dense(masks), tf.sparse.to_dense(target))
        self.assertAllEqual(masks.dtype, target.dtype)
        self.assertAllEqual(masks.shape, target.shape)

    def test2(self):
        idseqs = [[1, 1, 0, 0, 2, 2, 3], [1, 3, 2, 1, 0, 0, 2]]

        target = tf.sparse.SparseTensor(
            indices=(
                [0, 0, 1],
                [0, 1, 1],
                [0, 2, 0],
                [0, 3, 0],
                [0, 4, 2],
                [0, 5, 2],
                [1, 0, 1],
                [1, 2, 2],
                [1, 3, 1],
                [1, 4, 0],
                [1, 5, 0]),
            values=[1 for _ in range(11)],
            dense_shape=(2, 6, 3))

        masks = idseqs_to_mask(
            idseqs, n_seqlen=6, n_vocab_sz=3, ignore=[3],
            dense=False, dtype=tf.uint8)

        self.assertAllEqual(
            tf.sparse.to_dense(masks), tf.sparse.to_dense(target))
        # self.assertAllEqual(masks.dtype, target.dtype)
        self.assertAllEqual(masks.shape, target.shape)

    def test3(self):
        idseqs = [[1, 1, 0, 0, 2, 2, 3], [1, 3, 2, 1, 0, 0, 2]]

        target = tf.sparse.SparseTensor(
            indices=(
                [0, 0, 1],
                [0, 1, 1],
                [0, 2, 0],
                [0, 3, 0],
                [0, 4, 2],
                [0, 5, 2],
                [1, 0, 1],
                [1, 2, 2],
                [1, 3, 1],
                [1, 4, 0],
                [1, 5, 0]),
            values=[1.0 for _ in range(11)],
            dense_shape=(2, 6, 3))

        masks = idseqs_to_mask(
            idseqs, n_seqlen=6, n_vocab_sz=3, ignore=[3],
            dense=False, dtype=tf.float64)

        self.assertAllEqual(
            tf.sparse.to_dense(masks), tf.sparse.to_dense(target))
        # self.assertAllEqual(masks.dtype, target.dtype)
        self.assertAllEqual(masks.shape, target.shape)

    def test4(self):
        idseqs = [[1, 1, 0, 0, 2, 2, 3], [1, 3, 2, 1, 0, 0, 2]]

        target = tf.sparse.SparseTensor(
            indices=(
                [0, 2, 0],
                [0, 3, 0],
                [0, 4, 1],
                [0, 5, 1],
                [1, 1, 2],
                [1, 2, 1],
                [1, 4, 0],
                [1, 5, 0]),
            values=[True for _ in range(8)],
            dense_shape=(2, 6, 3))

        masks = idseqs_to_mask(
            idseqs, n_seqlen=6, ignore=[1],
            dense=False, dtype=tf.bool)

        self.assertAllEqual(
            tf.sparse.to_dense(masks), tf.sparse.to_dense(target))
        self.assertAllEqual(masks.dtype, target.dtype)
        self.assertAllEqual(masks.shape, target.shape)

    def test5(self):
        idseqs = [[1, 1, 0, 0, 2, 2, 3], [1, 3, 2, 1, 0, 0, 2]]

        target = tf.sparse.SparseTensor(
            indices=(
                [0, 2, 0],
                [0, 3, 0],
                [0, 4, 1],
                [0, 5, 1],
                [1, 1, 2],
                [1, 2, 1],
                [1, 4, 0],
                [1, 5, 0]),
            values=[True for _ in range(8)],
            dense_shape=(2, 6, 3))

        masks = idseqs_to_mask(
            idseqs, n_seqlen=6, ignore=[1],
            dense=True, dtype=tf.bool)

        self.assertAllEqual(masks, tf.sparse.to_dense(target))
        self.assertAllEqual(masks.dtype, target.dtype)
        self.assertAllEqual(masks.shape, target.shape)


if __name__ == "__main__":
    tf.test.main()
