import torch
from torch import nn
from torchvision import transforms


class Encoding(nn.Module):
    """Convoution, ReLU, Convolution, ReLU MaxPool2d"""
    def __init__(self, input_c, output_c):
        super().__init__()
        self.conv1 = nn.Conv2d(input_c, output_c, kernel_size=3, stride=1,
                               padding=1)
        self.norm1 = nn.BatchNorm2d(output_c)
        self.conv2 = nn.Conv2d(output_c, output_c, kernel_size=3, stride=1,
                               padding=1)
        self.norm2 = nn.BatchNorm2d(output_c)
        self.relu = nn.ReLU()
        self.maxpool = nn.MaxPool2d(2)

    def forward(self, x):
        x = self.conv1(x)
        x = self.norm1(x)
        x = self.relu(x)
        x = self.conv2(x)
        x = self.norm2(x)
        x = self.relu(x)
        out = self.maxpool(x)
        return out, x


class Decoding(nn.Module):
    """Conv2dtranspose, concat,convolution, relu, convolution, relu"""
    def __init__(self, input_c, skip_c, output_c):
        super().__init__()
        self.upsample = nn.ConvTranspose2d(input_c, input_c, 4, stride=2,
                                           padding=1)
        self.conv1 = nn.Conv2d(input_c + skip_c, output_c, kernel_size=3,
                               stride=1, padding=1)
        self.norm1 = nn.BatchNorm2d(output_c)
        self.conv2 = nn.Conv2d(output_c, output_c, kernel_size=3, stride=1,
                               padding=1)
        self.norm2 = nn.BatchNorm2d(output_c)
        self.relu = nn.ReLU()

    def forward(self, x, skip):
        x = self.upsample(x)
        *_, w, h = skip.shape
        x = transforms.functional.resize(x, (w, h))
        x = torch.cat([x, skip], dim=1)
        x = self.conv1(x)
        x = self.norm1(x)
        x = self.relu(x)
        x = self.conv2(x)
        x = self.norm2(x)
        x = self.relu(x)
        return x


class UNet(nn.Module):
    """
    A U-Net is a set of:
        Downsampling: Convolution, ReLU, Convolution, ReLU, MaxPool
        Bottleneck: Convolution, ReLU, Convolution, ReLU, no down-sampling
        Up-sampling: ConvTranspose, concatenate skip layer,Convolution, ReLU,
                     Convolution, ReLU
    Ending in a 1x1 Convolution and an activation (e.g. sigmoid) to get the
    correctly shaped output.
    """
    def __init__(self, input_c, output_c, init_features=32):
        super().__init__()
        # Encoding
        encoder = [Encoding(input_c, init_features)]
        features = init_features
        for i in range(3):
            encoder.append(Encoding(features, features*2))
            features *= 2
        self.encoder = nn.ModuleList(encoder)
        # Bottleneck
        bottleneck = []
        for i in range(2):
            bottleneck += [nn.Conv2d(features, features, 3, stride=1,
                                     padding=1),
                           nn.ReLU()]
        self.bottleneck = nn.Sequential(*bottleneck)
        # Decoding
        decoder = []
        for i in range(4):
            decoder.append(Decoding(features, features, features // 2))
            features = features // 2
        self.decoder = nn.ModuleList(decoder)
        # Include previous time point
        self.merge_prev = nn.Sequential(nn.Conv2d(features + output_c,
                                                  features, 1),
                                        nn.ReLU())
        # Output conversion
        self.output = nn.Sequential(nn.Conv2d(features, output_c, 1),
                                    nn.Sigmoid())

    def forward(self, x, prev=None):
        # encoding
        skips = []
        for enc in self.encoder:
            x, skip = enc(x)
            skips.insert(0, skip)
        # Bottleneck
        x = self.bottleneck(x)
        # Decoding
        for dec, skip in zip(self.decoder, skips):
            x = dec(x, skip)
        # Add information about previous time-point
        if prev is not None:
            x = torch.cat([x, prev], dim=1)
            x = self.merge_prev(x)
        # Output
        return self.output(x)
