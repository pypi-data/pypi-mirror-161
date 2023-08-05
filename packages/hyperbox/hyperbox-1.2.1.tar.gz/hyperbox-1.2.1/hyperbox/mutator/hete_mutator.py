from collections import OrderedDict

import json
import numpy as np

import torch
import torch.nn.functional as F

from hyperbox.mutables.spaces import InputSpace, OperationSpace, ValueSpace

from hyperbox.mutator.random_mutator import RandomMutator

__all__ = [
    'HeteMutator',
]


class HeteMutator(RandomMutator):
    def __init__(
        self,
        model,
        num_bins: int = 30,
        filepath: str = None,
        base: str = 'params',
        sample_mode: str = 'seq', # or 'random'
        *args, **kwargs
    ):
        super().__init__(model)
        self.masks = self.load_masks(filepath)
        self.keys = list(self.masks.keys())
        self.num_bins = num_bins
        self.base = base
        self.sample_mode = sample_mode
        self.mask_bins = self.split_masks_by_bins(self.masks, self.num_bins, base=self.base)
        self.count = 9

    def load_masks(self, filepath=None):
        if filepath is None:
            filepath = '/home/xihe/xinhe/hyperbox/ofa_mbv3_searchspace.json'
        with open(filepath, 'r') as f:
            masks = json.load(f)
        masks = OrderedDict(masks)
        return masks

    def split_masks_by_bins(self, masks: dict, num_bins: int, base: str='flops'):
        flops = torch.tensor([v['flops'] for v in masks.values()])
        params = torch.tensor([v['params'] for v in masks.values()])
        names = np.array([key for key in masks])

        interval = len(flops) // num_bins
        if base=='flops':
            sort_indices = torch.argsort(flops)
        elif base=='params':
            sort_indices = torch.argsort(params)
        elif base=='both':
            sort_indices = torch.argsort(params+flops)

        mask_bins = {}
        start = 0
        for i in range(num_bins):
            end = start + interval
            indices = torch.zeros(len(flops))
            if i==num_bins-1 and end<len(flops):
                end = len(flops)
            indices[sort_indices[start:end]] = 1
            mask_bins[i] = indices.bool()
            start = end
        return mask_bins

        # if base=='flops':
        #     _min = min(flops)
        #     _max = max(flops)
        #     tosplit_list = flops
        # elif base=='params':
        #     _min = min(params)
        #     _max = max(params)
        #     tosplit_list = params
        # interval = (_max - _min) / num_bins

        # mask_bins = {}
        # _start = _min
        # for i in range(num_bins):
        #     _end = _start + interval
        #     index_left = tosplit_list >= _start
        #     index_right = tosplit_list <= _end
        #     index = torch.logical_and(index_left, index_right) # torch>=1.8
        #     _start = _end
        #     mask_bins.update({i: index})
        # return mask_bins

    def build_archs_for_valid(self, *args, **kwargs):
        '''
        Build a list of archs for validation
        '''
        return super().build_archs_for_valid(*args, **kwargs)

    def sample_search(self):
        if 'seq' in self.sample_mode:
            bin_id = self.count % self.num_bins
        elif 'random' in self.sample_mode:
            bin_id = np.random.randint(self.num_bins)
        else:
            bin_id = np.random.randint(self.num_bins) # 根据权重采样
        mask_bin = self.mask_bins[bin_id]
        valid_indices = np.arange(0, len(mask_bin))[mask_bin]
        one_index = np.random.choice(valid_indices, 1)[0]
        sample_key = self.keys[one_index]
        result = dict()
        for m in self.mutables:
            key = m.key
            mask = torch.tensor(self.masks[sample_key]['mask'][key])
            assert m.mask.shape==mask.shape,\
                f'{key}: {m.mask.shape} not match {mask.shape}'
            result[key] = mask.bool()
            m.mask.data.copy_(mask.data)
        return result

    def sample_final(self):
        return self.sample_search()


if __name__ == '__main__':
    from hyperbox.networks import OFAMobileNetV3
    net = OFAMobileNetV3()
    hm = HeteMutator(net)
    mask = hm.reset()
    pass