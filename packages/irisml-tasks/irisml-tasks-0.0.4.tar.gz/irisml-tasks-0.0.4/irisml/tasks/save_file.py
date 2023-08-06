import dataclasses
import logging
import pathlib
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Save the given input binary to a file."""
    VERSION = '0.1.0'
    CACHE_ENABLED = False

    @dataclasses.dataclass
    class Inputs:
        data: bytes

    @dataclasses.dataclass
    class Config:
        path: pathlib.Path

    def execute(self, inputs):
        if self.config.path.exists():
            logger.warning(f"Path {self.config.path} already exists. Aborting.")
        else:
            self.config.path.parent.mkdir(parents=True, exist_ok=True)
            self.config.path.write_bytes(inputs.data)
        return self.Outputs()
