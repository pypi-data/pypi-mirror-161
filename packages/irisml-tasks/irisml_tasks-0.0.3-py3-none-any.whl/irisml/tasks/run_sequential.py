import dataclasses
import typing
import irisml.core


class Task(irisml.core.TaskBase):
    """Run the given tasks in sequence. Each task must have an unique name."""
    VERSION = '0.1.0'
    CACHE_ENABLED = False

    @dataclasses.dataclass
    class Config:
        tasks: typing.List[irisml.core.TaskDescription]

    def execute(self, inputs):
        for task_description in self.config.tasks:
            task = irisml.core.Task(task_description)
            task.load_module()
            task.execute(self.context)

        return self.Outputs()

    def dry_run(self, inputs):
        return self.execute()
