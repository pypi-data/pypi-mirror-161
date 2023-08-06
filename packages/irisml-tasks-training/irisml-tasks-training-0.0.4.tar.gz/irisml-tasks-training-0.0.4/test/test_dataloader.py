import unittest
import torch
from irisml.tasks.train.build_dataloader import collate, Dataset


class TestDataLoader(unittest.TestCase):
    def test_collate(self):
        # Image only
        result = collate([torch.zeros((3, 64, 64), dtype=float) for _ in range(8)])
        self.assertIsInstance(result[0], torch.Tensor)
        self.assertIsNone(result[1])
        self.assertEqual(result[0].shape, (8, 3, 64, 64))

        result = collate([(torch.zeros((3, 64, 64), dtype=float), i) for i in range(8)])
        self.assertIsInstance(result[0], torch.Tensor)
        self.assertEqual(result[0].shape, (8, 3, 64, 64))
        self.assertIsInstance(result[1], torch.Tensor)
        self.assertEqual(result[1].shape, (8, ))

        result = collate([(torch.zeros((3, 64, 64), dtype=float), torch.tensor(i)) for i in range(8)])
        self.assertIsInstance(result[0], torch.Tensor)
        self.assertEqual(result[0].shape, (8, 3, 64, 64))
        self.assertIsInstance(result[1], torch.Tensor)
        self.assertEqual(result[1].shape, (8, ))

        # multilabel classification or object detection with no labels
        result = collate([(torch.zeros((3, 64, 64), dtype=float), []) for _ in range(8)])
        self.assertIsInstance(result[0], torch.Tensor)
        self.assertEqual(result[0].shape, (8, 3, 64, 64))
        self.assertIsInstance(result[1], list)
        self.assertFalse(any(result[1]))

        result = collate([(torch.zeros((3, 64, 64), dtype=float), [i]) for i in range(8)])
        self.assertIsInstance(result[0], torch.Tensor)
        self.assertEqual(result[0].shape, (8, 3, 64, 64))
        self.assertIsInstance(result[1], torch.Tensor)
        self.assertEqual(result[1].shape, (8, ))

        result = collate([(torch.zeros((3, 64, 64), dtype=float), [j for j in range(i)]) for i in range(8)])
        self.assertIsInstance(result[0], torch.Tensor)
        self.assertEqual(result[0].shape, (8, 3, 64, 64))
        self.assertIsInstance(result[1], list)
        self.assertTrue(torch.equal(result[1][0], torch.tensor([])))
        self.assertTrue(torch.equal(result[1][1], torch.tensor([0])))
        self.assertTrue(torch.equal(result[1][2], torch.tensor([0, 1])))

        # object detection
        result = collate([(torch.zeros((3, 64, 64), dtype=float), [[0, 0.1, 0.1, 0.2, 0.2] for _ in range(i)]) for i in range(8)])
        self.assertIsInstance(result[0], torch.Tensor)
        self.assertEqual(result[0].shape, (8, 3, 64, 64))
        self.assertIsInstance(result[1], list)
        self.assertIsInstance(result[1][0], torch.Tensor)
        self.assertIsInstance(result[1][1], torch.Tensor)
        self.assertEqual(result[1][0].shape, (0, 5))
        self.assertTrue(torch.equal(result[1][1], torch.tensor([[0, 0.1, 0.1, 0.2, 0.2]])))
        self.assertEqual(result[1][2].shape, (2, 5))

        result = collate([(torch.zeros((3, 64, 64), dtype=float), torch.tensor([[0, 0.1, 0.1, 0.2, 0.2] for _ in range(i)])) for i in range(8)])
        self.assertIsInstance(result[0], torch.Tensor)
        self.assertEqual(result[0].shape, (8, 3, 64, 64))
        self.assertIsInstance(result[1], list)
        self.assertIsInstance(result[1][0], torch.Tensor)
        self.assertIsInstance(result[1][1], torch.Tensor)
        self.assertEqual(result[1][1].shape, (1, 5))
        self.assertEqual(result[1][2].shape, (2, 5))

        # image-text
        result = collate([((torch.zeros((3, 64, 64), dtype=float), torch.zeros(16, dtype=int)), [3]) for _ in range(8)])
        self.assertIsInstance(result[0][0], torch.Tensor)  # image
        self.assertIsInstance(result[0][1], torch.Tensor)  # text
        self.assertIsInstance(result[1], torch.Tensor)  # targets

    def test_get_transform_args(self):
        # Make sure it doesn't throw an exception.
        Dataset([], self._fake_transform_method1)
        Dataset([], self._fake_transform_method2)

        def fake_transform_function1(x):
            return x

        def fake_transform_function2(x, y):
            return x, y

        Dataset([], fake_transform_function1)
        Dataset([], fake_transform_function2)

    def _fake_transform_method1(self, x):
        return x

    def _fake_transform_method2(self, x, y):
        return x, y
