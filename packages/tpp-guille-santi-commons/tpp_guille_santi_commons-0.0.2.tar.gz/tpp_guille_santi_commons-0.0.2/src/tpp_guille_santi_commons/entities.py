import torch.nn as nn
import torch.nn.functional as F
from pydantic import BaseModel


class Material(BaseModel):
    material: str


class MyModel(nn.Module):
    def __init__(self):
        super(MyModel, self).__init__()

        # 224x224x3 => 26x26x32
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3)
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=32, kernel_size=3)
        self.pool = nn.MaxPool2d(kernel_size=3)
        self.conv3 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3)
        self.conv4 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3)
        self.conv5 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3)
        self.conv6 = nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3)
        # self.conv7 = nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3)
        # self.pool4 = nn.MaxPool2d(kernel_size=2)
        self.d1 = nn.Linear(73 * 73 * 32, 128)
        self.d2 = nn.Linear(128, 6)

    def forward(self, x):
        # 32x3x224x224 => 32x32x222x222
        x = self.conv1(x)
        x = F.relu(x)

        x = self.conv2(x)
        x = F.relu(x)

        x = self.pool(x)

        # x = self.conv7(x)
        # x = F.relu(x)

        # x = self.pool4(x)

        # print("Shape:")
        # print(x.shape)
        # flatten => 32 x (32*222*222) = 1577088
        x = x.flatten(start_dim=1)

        # 32 x (32*222*222) => 32x128
        x = self.d1(x)
        x = F.relu(x)

        # logits => 32x6
        logits = self.d2(x)
        out = F.softmax(logits, dim=1)
        return out
