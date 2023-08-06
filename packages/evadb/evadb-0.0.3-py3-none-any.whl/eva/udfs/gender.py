# coding=utf-8
# Copyright 2018-2020 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import List

import pandas as pd
import numpy as np
import os

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.udfs.pytorch_abstract_udf import PytorchAbstractUDF

try:
    import torch
    import torch.nn as nn
    from torch import Tensor
except ImportError as e:
    raise ImportError(f"Failed to import with error {e}, \
        please try `pip install torch`")

try:
    import torchvision
    from torchvision import transforms
except ImportError as e:
    raise ImportError(f"Failed to import with error {e}, \
        please try `pip install torch`")


class GenderDetector(PytorchAbstractUDF):

    @property
    def name(self) -> str:
        return "gender"

    def __init__(self):
        super().__init__()
        self.model_path = os.path.join("gender.pth")

        self.model = torchvision.models.resnet18(pretrained=True)
        num_features = self.model.fc.in_features
        self.model.fc = nn.Linear(num_features, 2) # binary classification (num_of_class == 2)
        self.model.load_state_dict(torch.load(self.model_path))
        self.model.eval()

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> List[str]:
        return [
            'female', 'male'
        ]

    @property
    def transforms(self) -> transforms.Compose:
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

    def _get_predictions(self, frames: Tensor) -> pd.DataFrame:
        """
        Performs predictions on input frames
        Arguments:
            frames (np.ndarray): Frames on which predictions need
            to be performed

        Returns:
            tuple containing predicted_classes (List[str])
        """
        outcome = pd.DataFrame()
        predictions = self.model(frames)
        for prediction in predictions:
            label = self.as_numpy(prediction.data.argmax())
            outcome = outcome.append({"label" : str(label)}, ignore_index=True)        

