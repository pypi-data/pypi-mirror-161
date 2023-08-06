import pickle
import unittest
import torch
from irisml.tasks.create_torchvision_model import Task


class TestCreateTorchvisionModel(unittest.TestCase):
    def test_classification(self):
        self._execute_task(name='mobilenet_v2', num_classes=1000, task_type='multiclass_classification')
        model = self._execute_task(name='mobilenet_v2', num_classes=1000, task_type='multilabel_classification')
        deserialized = pickle.loads(pickle.dumps(model))
        self.assertIsNotNone(deserialized)

    def test_object_detection(self):
        model = self._execute_task(name='fasterrcnn_resnet50_fpn', num_classes=91, task_type='object_detection')
        deserialized = pickle.loads(pickle.dumps(model))
        self.assertIsNotNone(deserialized)

        model.training_step(torch.zeros(4, 3, 320, 320), [torch.zeros(0, 5), torch.zeros(0, 5), torch.zeros(0, 5), torch.zeros(0, 5)])

    def _execute_task(self, **kwargs):
        config = Task.Config(**kwargs, pretrained=False)
        task = Task(config)
        outputs = task.execute(None)
        self.assertIsInstance(outputs.model, torch.nn.Module)
        return outputs.model
