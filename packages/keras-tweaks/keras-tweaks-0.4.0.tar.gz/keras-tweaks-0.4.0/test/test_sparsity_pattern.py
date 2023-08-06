import tensorflow as tf
from keras_tweaks import get_sparsity_pattern


class TestSparsityPattern(tf.test.TestCase):
    def test1(self):
        sp = get_sparsity_pattern('diag', 3)
        target = [(0, 0), (1, 1), (2, 2)]
        self.assertAllEqual(sp, target)

    def test2(self):
        sp = get_sparsity_pattern('dense', 2)
        target = [(0, 0), (0, 1), (1, 0), (1, 1)]
        self.assertAllEqual(sp, target)

    def test3(self):
        sp = get_sparsity_pattern('dense', 2, 3)
        target = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
        self.assertAllEqual(sp, target)

    def test4(self):
        sp = get_sparsity_pattern('nodiag', 3)
        target = [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]
        self.assertAllEqual(sp, target)

    def test5(self):
        sp = get_sparsity_pattern('nodiag', 2, 3)
        target = [(0, 1), (0, 2), (1, 0), (1, 2)]
        self.assertAllEqual(sp, target)

    def test6(self):
        sp = get_sparsity_pattern('block', 4, 2)
        target = [(0, 0), (0, 1), (1, 0), (1, 1),
                  (2, 2), (2, 3), (3, 2), (3, 3)]
        self.assertAllEqual(sp, target)

    def test7(self):
        sp = get_sparsity_pattern('block', 3, [2, 2])
        target = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 2)]
        self.assertAllEqual(sp, target)

    def test8(self):
        sp = get_sparsity_pattern('circle', 5, [1, 1])
        target = [(0, 4), (1, 0), (2, 1), (3, 2), (4, 3)]
        self.assertAllEqual(sp, target)


if __name__ == "__main__":
    tf.test.main()
