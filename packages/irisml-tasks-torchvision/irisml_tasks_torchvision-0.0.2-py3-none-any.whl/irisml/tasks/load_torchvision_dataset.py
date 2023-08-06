import dataclasses
import typing
import torch
import torchvision.datasets
import irisml.core


class Task(irisml.core.TaskBase):
    """Load a dataset from torchvision package.

    Data will be downloaded to the current directory. Downloading will be skipped if the data is in the current directory.

    Only Image classification data is supported for now.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        name: str

    @dataclasses.dataclass
    class Outputs:
        train_dataset: torch.utils.data.Dataset = None
        val_dataset: torch.utils.data.Dataset = None
        num_classes: int = 0
        class_names: typing.Optional[typing.List[str]] = dataclasses.field(default_factory=list)

    def execute(self, inputs):
        if not hasattr(torchvision.datasets, self.config.name):
            raise RuntimeError(f"Dataset {self.config.name} is not supported.")

        dataset_class = getattr(torchvision.datasets, self.config.name)

        train_dataset = dataset_class('.', train=True, download=True)
        val_dataset = dataset_class('.', train=False, download=True)
        class_names = None
        if hasattr(train_dataset, 'classes'):
            num_classes = len(train_dataset.classes)
            class_names = train_dataset.classes
        else:
            label_set = set()
            for i in range(len(train_dataset)):
                _, label = train_dataset[i]
                label_set.add(label)
            num_classes = len(label_set)

        return self.Outputs(train_dataset=train_dataset, val_dataset=val_dataset, num_classes=num_classes, class_names=class_names)
