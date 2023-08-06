import copy
import dataclasses
import io
import pathlib
import typing
import torch
import irisml.core


class Task(irisml.core.TaskBase):
    """Load a state_dict from various sources.

    Supported sources are:
        1. a dictionary object. Use Inputs.state_dict.
        2. a bytes object. Use Inputs.state_dict_bytes.
        3. a file on local filesystem. Use Config.path.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        model: torch.nn.Module
        state_dict: typing.Optional[typing.Dict] = None
        state_dict_bytes: typing.Optional[bytes] = None

    @dataclasses.dataclass
    class Config:
        path: typing.Optional[pathlib.Path] = None

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module = None

    def execute(self, inputs: Inputs):
        num_sources = len([x for x in [inputs.state_dict, inputs.state_dict_bytes, self.config.path] if x])
        if num_sources != 1:
            raise ValueError("One state_dict source must be provided.")

        if inputs.state_dict:
            state_dict = inputs.state_dict
        if inputs.state_dict_bytes:
            state_dict = torch.load(io.BytesIO(inputs.state_dict_bytes), map_location='cpu')
        elif self.config.path:
            state_dict = torch.load(self._config.path, map_location='cpu')

        if not state_dict:
            raise ValueError("Failed to load the state_dict.")

        model = copy.deepcopy(inputs.model)
        model.load_state_dict(state_dict)
        return self.Outputs(model)
