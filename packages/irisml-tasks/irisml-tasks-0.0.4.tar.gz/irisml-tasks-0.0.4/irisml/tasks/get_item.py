import dataclasses
import typing
import irisml.core


class Task(irisml.core.TaskBase):
    """Get an item from the given list."""
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        array: typing.List[typing.Any]

    @dataclasses.dataclass
    class Config:
        index: int

    @dataclasses.dataclass
    class Outputs:
        item: typing.Any = None

    def execute(self, inputs):
        return self.Outputs(inputs.array[self.config.index])

    def dry_run(self, inputs):
        return self.execute(inputs)
