import dataclasses
import typing
from transformers import AutoTokenizer
import irisml.core


class Task(irisml.core.TaskBase):
    """Create a Tokenizer using transformers library.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        name: str

    @dataclasses.dataclass
    class Outputs:
        tokenizer: typing.Callable = None

    def execute(self, inputs):
        tokenizer = AutoTokenizer.from_pretrained(self.config.name)
        return self.Outputs(Tokenizer(tokenizer))


class Tokenizer:
    def __init__(self, tokenizer):
        self._tokenizer = tokenizer

    def __call__(self, inputs):
        return self._tokenizer(inputs, return_tensors='pt', padding='max_length', max_length=77)['input_ids'][0]
