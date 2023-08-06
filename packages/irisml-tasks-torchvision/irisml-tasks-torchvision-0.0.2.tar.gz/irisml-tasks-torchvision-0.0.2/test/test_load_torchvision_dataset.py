import unittest
from irisml.core import Context
from irisml.tasks.load_torchvision_dataset import Task


class TestLoadTorchvisionDataset(unittest.TestCase):
    def test_simple(self):
        config = Task.Config(name='unknown_dataset')
        tasks = Task(config, Context())
        with self.assertRaises(RuntimeError):
            tasks.execute(None)
