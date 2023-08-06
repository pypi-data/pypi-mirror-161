import tensorflow as tf
from keras_tweaks import dense_sparse_matmul


class Test_dense_sparse_matmul(tf.test.TestCase):
    def test1(self):
        h = tf.constant([1., 2., 3.])
        W = tf.sparse.SparseTensor(
            indices=([0, 1], [1, 1], [1, 2], [2, 0], [2, 3]),
            values=[1., 2., 3., 4., 5.],
            dense_shape=(3, 4))
        net = dense_sparse_matmul(h, W)
        assert list(net.shape) == [1, 4]
        self.assertAllEqual(net, [[12., 5., 6., 15.]])

    def test2(self):
        # (batch=1, dim=3)
        h = tf.constant([[1., 2., 3.]])
        W = tf.sparse.SparseTensor(
            indices=([0, 1], [1, 1], [1, 2], [2, 0], [2, 3]),
            values=[1., 2., 3., 4., 5.],
            dense_shape=(3, 4))
        net = dense_sparse_matmul(h, W)
        assert list(net.shape) == [1, 4]
        self.assertAllEqual(net, [[12., 5., 6., 15.]])

    def test3(self):
        # (batch=4, dim=3)
        h = tf.constant([
            [1., 2., 3.], [4., 5., 6.], [7., 8., 9.], [10., 11., 12.]])
        W = tf.sparse.SparseTensor(
            indices=([0, 1], [1, 1], [1, 0], [2, 0], [2, 1]),
            values=[1., 2., 3., 4., 5.],
            dense_shape=(3, 2))
        net = dense_sparse_matmul(h, W)
        assert list(net.shape) == [4, 2]
        self.assertAllEqual(net, [
            [18., 20.], [39., 44.], [60., 68.], [81., 92.]])

    def test4(self):
        # (batch=2, seqlen=4, dim=3)
        h = tf.constant([
            [[1., 2., 3.], [4., 5., 6.], [7., 8., 9.], [10., 11., 12.]],
            [[12., 11., 10.], [9., 8., 7.], [6., 5., 4.], [2., 1., 0.]],
            [[1., 2., 3.], [4., 5., 6.], [7., 8., 9.], [10., 11., 12.]],
        ])
        W = tf.sparse.SparseTensor(
            indices=([0, 1], [1, 1], [1, 0], [2, 0], [2, 1]),
            values=[1., 2., 3., 4., 5.],
            dense_shape=(3, 2))
        net = dense_sparse_matmul(h, W)
        assert list(net.shape) == [3, 4, 2]
        self.assertAllEqual(net, [
            [[18., 20.], [39., 44.], [60., 68.], [81., 92.]],
            [[73., 84.], [52., 60.], [31., 36.], [3., 4.]],
            [[18., 20.], [39., 44.], [60., 68.], [81., 92.]],
        ])


if __name__ == "__main__":
    tf.test.main()
