import dataclasses
import logging
import typing
import torch
import torchvision.models
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Create a torchvision model.

    Currently this task supports three kind of tasks. multiclass_classification, multilabel_classificaiton, and object_detection.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        name: str
        num_classes: int
        task_type: typing.Literal['multiclass_classification', 'multilabel_classification', 'object_detection'] = 'multiclass_classification'
        pretrained: bool = False

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module = None

    MODULES = {
        'multiclass_classification': (torch.nn.CrossEntropyLoss(), torch.nn.Softmax(1)),
        'multilabel_classification': (torch.nn.BCEWithLogitsLoss(), torch.nn.Sigmoid()),
    }

    class TorchvisionICModel(torch.nn.Module):
        def __init__(self, model_name, num_classes, criterion, predictor, state_dict=None):
            super().__init__()
            model_class = getattr(torchvision.models, model_name)
            if not model_class:
                raise RuntimeError(f"Model {model_name} is not supported by torchvision.")
            self.model = model_class(pretrained=False, num_classes=num_classes)
            self._model_name = model_name
            self._num_classes = num_classes
            self._criterion = criterion
            self._predictor = predictor
            # Those constants needs to be buffers so that they can be moved to the target device.
            self.register_buffer('mean_value', torch.Tensor([0.485, 0.456, 0.406]).reshape((3, 1, 1)))
            self.register_buffer('std_value', torch.Tensor([0.229, 0.224, 0.225]).reshape((3, 1, 1)))
            if state_dict:
                self.model.load_state_dict(state_dict)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.model((x - self.mean_value) / self.std_value)

        def training_step(self, inputs, targets):
            loss = self._criterion(self(inputs), targets)
            return {'loss': loss}

        def prediction_step(self, inputs):
            return self._predictor(self(inputs))

        def __getstate__(self):
            return {'model_name': self._model_name, 'num_classes': self._num_classes, 'criterion': self._criterion, 'predictor': self._predictor, 'state_dict': dict(self.model.state_dict())}

        def __setstate__(self, state):
            self.__init__(**state)

    class TorchvisionODModel(torch.nn.Module):
        def __init__(self, model_name, num_classes, state_dict=None):
            super().__init__()
            model_class = getattr(torchvision.models.detection, model_name)
            if not model_class:
                raise RuntimeError(f"Model {model_name} for object detection is not supported by torchvision.")
            self.model = model_class(pretrained=False, pretrained_backbone=False, num_classes=num_classes)
            self._model_name = model_name
            self._num_classes = num_classes
            # Those constants needs to be buffers so that they can be moved to the target device.
            self.register_buffer('mean_value', torch.Tensor([0.485, 0.456, 0.406]).reshape((3, 1, 1)))
            self.register_buffer('std_value', torch.Tensor([0.229, 0.224, 0.225]).reshape((3, 1, 1)))
            if state_dict:
                self.model.load_state_dict(state_dict)

        def training_step(self, inputs, targets):
            inputs = list((i - self.mean_value) / self.std_value for i in inputs)  # Make sure the inputs is a list.

            image_sizes = torch.tensor([i.shape[1:] for i in inputs])  # Shape [N, 2]
            image_sizes2 = torch.stack((image_sizes[:, 1], image_sizes[:, 0], image_sizes[:, 1], image_sizes[:, 0]), dim=1)  # w, h, w, h
            assert image_sizes2.shape == (len(inputs), 4)
            boxes = [targets[i][:, 1:] * image_sizes2[i] for i in range(len(inputs))]
            labels = [t[:, 0].to(torch.int64) for t in targets]
            assert len(boxes) == len(labels) == len(inputs)

            targets = [{'boxes': boxes[i], 'labels': labels[i]} for i in range(len(inputs))]
            outputs = self.model(inputs, targets)
            return {'loss': sum(o for o in outputs.values())}

        def prediction_step(self, inputs):
            inputs = list((i - self.mean_value) / self.std_value for i in inputs)  # Make sure the inputs is a list.
            predictions = self.model(inputs)
            results = []
            for i, p in enumerate(predictions):
                h, w = inputs[i].shape[1:]
                box = [[b[0] / w, b[1] / h, b[2] / w, b[3] / h] for b in p['boxes']]
                results.append(torch.tensor([[p['labels'][j], p['scores'][j], *box[j]] for j in range(len(box))]))
            return results

        def __getstate__(self):
            return {'model_name': self._model_name, 'num_classes': self._num_classes, 'state_dict': dict(self.model.state_dict())}

        def __setstate__(self, state):
            self.__init__(**state)

    def execute(self, inputs):
        logger.info(f"Creating a torchvision model: name={self.config.name}, num_classes={self.config.num_classes}, pretrained={self.config.pretrained}")

        if self.config.task_type == 'object_detection':
            model = Task.TorchvisionODModel(self.config.name, self.config.num_classes)
        else:
            criterion, predictor = self.MODULES[self.config.task_type]
            model = Task.TorchvisionICModel(self.config.name, self.config.num_classes, criterion, predictor)

        if self.config.pretrained:
            logger.debug("Loading pretrained weights for the model.")
            model_class = getattr(torchvision.models.detection if self.config.task_type == 'object_detection' else torchvision.models, self.config.name)
            pretrained_model = model_class(pretrained=True, progress=False)
            # We cannot directly construct since the pretrained weights will be loaded with strict mode.
            state_dict = model.model.state_dict()
            pretrained_state_dict = pretrained_model.state_dict()
            filtered_state_dict = {k: v for k, v in pretrained_state_dict.items() if pretrained_state_dict[k].shape == state_dict[k].shape}
            model.model.load_state_dict(filtered_state_dict, strict=False)

        return self.Outputs(model)

    def dry_run(self, inputs):
        if self.config.task_type == 'object_detection':
            model = Task.TorchvisionODModel(self.config.name, self.config.num_classes)
        else:
            criterion, predictor = self.MODULES[self.config.task_type]
            model = Task.TorchvisionICModel(self.config.name, self.config.num_classes, criterion, predictor)

        return self.Outputs(model)
