import unittest
import torch
import PIL.Image
from irisml.core import Context
from irisml.tasks.create_torchvision_transform import Task


class TestCreateTorchvisionTransform(unittest.TestCase):
    def test_simple(self):
        config = Task.Config(["Resize((256, 256))", "CenterCrop(224)", "RandomHorizontalFlip(0.1)", "ColorJitter(0.2, 0.2)"])
        task = Task(config, Context())
        outputs = task.execute(None)

        image = PIL.Image.new('RGB', (500, 500))
        transformed = outputs.transform(image)

        self.assertIsInstance(transformed, torch.Tensor)
        self.assertEqual(transformed.shape, (3, 224, 224))
