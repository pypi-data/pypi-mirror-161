import unittest
import torch
from irisml.tasks.create_transformers_model import Task


class TestCreateTransformersModel(unittest.TestCase):
    def test_clip(self):
        outputs = Task(Task.Config('openai/clip-vit-base-patch32')).execute(Task.Inputs())
        self.assertIsInstance(outputs.model, torch.nn.Module)
        loss = outputs.model.training_step((torch.zeros(1, 3, 224, 224), torch.zeros(1, 8, dtype=torch.int)), torch.zeros((1, ), dtype=torch.long))
        self.assertIsInstance(loss['loss'], torch.Tensor)
