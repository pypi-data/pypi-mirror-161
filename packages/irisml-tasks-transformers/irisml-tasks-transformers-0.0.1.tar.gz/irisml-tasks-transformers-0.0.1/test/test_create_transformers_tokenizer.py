import unittest
import torch
from irisml.tasks.create_transformers_tokenizer import Task


class TestCreateTransformersTokenizer(unittest.TestCase):
    def test_simple(self):
        outputs = Task(Task.Config('openai/clip-vit-base-patch32')).execute(Task.Inputs())
        self.assertIsNotNone(outputs.tokenizer)

        token = outputs.tokenizer("Answer to the Ultimate Question of Life, The Universe, and Everything")
        self.assertGreater(len(token), 0)
        self.assertIsInstance(token, torch.Tensor)
