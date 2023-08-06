import dataclasses
import io
import torch
import irisml.core


class Task(irisml.core.TaskBase):
    """Export the given model as ONNX."""
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        model: torch.nn.Module

    @dataclasses.dataclass
    class Config:
        input_size: int = 224

    @dataclasses.dataclass
    class Outputs:
        data: bytes = None

    def execute(self, inputs):
        model = torch.nn.Sequential(inputs.model, inputs.model.predictor)
        x = torch.randn(1, 3, self.config.input_size, self.config.input_size)
        with io.BytesIO() as bytes_io:
            torch.onnx.export(model, x, bytes_io)
            return self.Outputs(bytes(bytes_io.getbuffer()))
