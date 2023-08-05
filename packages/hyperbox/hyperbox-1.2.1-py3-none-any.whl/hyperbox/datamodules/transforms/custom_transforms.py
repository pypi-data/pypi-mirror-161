# Once for All: Train One Network and Specialize it for Efficient Deployment
# Han Cai, Chuang Gan, Tianzhe Wang, Zhekai Zhang, Song Han
# International Conference on Learning Representations (ICLR), 2020.

import time
import random
import os
from typing import Union, Optional, List, Tuple
from PIL import Image

import torchvision.transforms.functional as F
import torchvision.transforms as transforms


class MyRandomResizedCrop(transforms.RandomResizedCrop):
    ACTIVE_SIZE = 224
    IMAGE_SIZE_LIST = [224]

    CONTINUOUS = False
    SYNC_DISTRIBUTED = False

    EPOCH = 0

    def __init__(
        self,
        size: Union[int, List],
        scale: Union[Tuple, List] = (0.08, 1.0),
        ratio: Union[Tuple, List] = (3./4., 4./3.),
        interpolation=Image.BILINEAR
    ):
        if not isinstance(size, int):
            size = size[-1]
        MyRandomResizedCrop.ACTIVE_SIZE = size
        super(MyRandomResizedCrop, self).__init__(size, scale, ratio, interpolation)
        self.interpolation = interpolation

    def __call__(self, img):
        i, j, h, w = self.get_params(img, self.scale, self.ratio)
        return F.resized_crop(
            img, i, j, h, w, (MyRandomResizedCrop.ACTIVE_SIZE, MyRandomResizedCrop.ACTIVE_SIZE), self.interpolation
        )

    @staticmethod
    def get_candidate_image_size():
        if MyRandomResizedCrop.CONTINUOUS:
            min_size = min(MyRandomResizedCrop.IMAGE_SIZE_LIST)
            max_size = max(MyRandomResizedCrop.IMAGE_SIZE_LIST)
            candidate_sizes = []
            for i in range(min_size, max_size + 1):
                if i % 4 == 0:
                    candidate_sizes.append(i)
        else:
            candidate_sizes = MyRandomResizedCrop.IMAGE_SIZE_LIST

        relative_probs = None
        return candidate_sizes, relative_probs

    @staticmethod
    def sample_image_size(batch_id):
        if MyRandomResizedCrop.SYNC_DISTRIBUTED:
            _seed = int('%d%.3d' % (batch_id, MyRandomResizedCrop.EPOCH))
        else:
            _seed = os.getpid() + time.time()
        random.seed(_seed)
        candidate_sizes, relative_probs = MyRandomResizedCrop.get_candidate_image_size()
        MyRandomResizedCrop.ACTIVE_SIZE = random.choices(candidate_sizes, weights=relative_probs)[0]
