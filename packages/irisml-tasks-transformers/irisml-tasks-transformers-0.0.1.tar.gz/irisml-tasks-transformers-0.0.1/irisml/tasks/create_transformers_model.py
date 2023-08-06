import dataclasses
import torch.nn
import transformers
import irisml.core
from irisml.tasks.make_image_text_contrastive_model import ImageTextContrastiveModel


class Task(irisml.core.TaskBase):
    """Create a model using transformers library.

    Currently only CLIPModel is supported.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        name: str
        pretrained: bool = False

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module

    def execute(self, inputs):
        return self.Outputs(self._create_model(self.config.name, self.config.pretrained))

    def dry_run(self, inputs):
        return self.Outputs(self._create_model(self.config.name, False))

    @staticmethod
    def _create_model(name, pretrained):
        if pretrained:
            transformers_model = transformers.AutoModel.from_pretrained(name)
        else:
            transformers_config = transformers.AutoConfig.from_pretrained(name)
            transformers_model = transformers.AutoModel.from_config(transformers_config)

        if isinstance(transformers_model, transformers.CLIPModel):
            model = ImageTextContrastiveModel(PoolerOutputExtractor(transformers_model.vision_model), PoolerOutputExtractor(transformers_model.text_model),
                                              transformers_model.visual_projection, transformers_model.text_projection,
                                              'clip', float(transformers_model.logit_scale))
        else:
            raise RuntimeError(f"The model type {type(transformers_model)} is not supported. Please submit a pull request.")

        return model


class PoolerOutputExtractor(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self._model = model

    def forward(self, inputs):
        result = self._model(inputs)
        return result.pooler_output

    def state_dict(self):
        return self._model.state_dict()

    def load_state_dict(self, *args, **kwargs):
        return self._model.load_state_dict(*args, **kwargs)
