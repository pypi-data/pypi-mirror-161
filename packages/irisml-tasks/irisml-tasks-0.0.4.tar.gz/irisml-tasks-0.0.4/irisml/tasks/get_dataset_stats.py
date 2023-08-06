import dataclasses
import logging
import typing
import torch.utils.data
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset

    @dataclasses.dataclass
    class Outputs:
        num_images: int = 0
        num_classes: int = 0
        num_boxes: int = 0
        dataset_type: typing.Literal['multiclass_classification', 'multilabel_classification', 'object_detection'] = None

    def execute(self, inputs):
        num_images = len(inputs.dataset)
        dataset_type = None
        num_boxes = 0
        classes_set = set()
        potential_dataset_type = set()

        for image, targets in inputs.dataset:
            if isinstance(targets, torch.Tensor):
                if len(targets.shape) == 1:
                    targets = [int(x) for x in targets]
                elif len(targets.shape) == 2 and targets.shape[1] == 5:
                    targets = [[int(t[0]), float(t[1]), float(t[2]), float(t[3]), float(t[4])] for t in targets]
            elif isinstance(targets, int):
                targets = [targets]
                potential_dataset_type.add('multiclass_classification')

            if len(targets) > 1:
                if isinstance(targets[0], int):
                    potential_dataset_type.add('multilabel_classification')
                elif isinstance(targets[0], list) and len(targets[0]) == 5:
                    potential_dataset_type.add('object_detection')

            if targets and isinstance(targets[0], list):
                classes_set.update(t[0] for t in targets)
            else:
                classes_set.update(targets)

        if len(potential_dataset_type) > 1:
            raise RuntimeError(f"Couldn't detect dataset types: {potential_dataset_type}")

        if potential_dataset_type:
            dataset_type = list(potential_dataset_type)[0]
        else:
            dataset_type = 'multiclass_classification'

        num_classes = len(classes_set)
        logger.info(f"Dataset type: {dataset_type}, num_classes={num_classes}, num_images={num_images}, num_boxes={num_boxes}")
        return self.Outputs(num_images=num_images, num_classes=num_classes, num_boxes=num_boxes, dataset_type=dataset_type)
