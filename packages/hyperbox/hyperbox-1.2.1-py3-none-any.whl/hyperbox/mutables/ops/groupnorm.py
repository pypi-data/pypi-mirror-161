
import torch.nn as nn

from .base_module import FinegrainedModule
from .utils import is_searchable


class GroupNorm(nn.GroupNorm, FinegrainedModule):

	def __init__(self, num_groups, num_channels, eps=1e-5, affine=True):
        FinegrainedModule.__init__(self)
		GroupNorm.__init__(self, num_groups, self.num_channels, self.eps, self.affine)
		self.channel_per_group = channel_per_group
        self.is_search = self.isSearchGroupNorm()

    def isSearchGroupNorm(self):
        if all([not vs.is_search for vs in self.value_spaces.values()]):
            return False

        if is_searchable(getattr(self.value_spaces, 'num_groups', None)):
            self.search_num_groups = True
        if is_searchable(getattr(self.value_spaces, 'num_channels', None)):
            self.search_num_channels = True
        return True

	def forward(self, x):
		n_channels = x.size(1)
        n_groups = getattr(self.value_spaces, 'num_groups', self.num_groups)
		return F.group_norm(
            x,
            n_groups,
            self.weight[:n_channels] if self.affine else None,
            self.bias[:n_channels] if self.affine else None,
            self.eps)

	@property
	def bn(self):
		return self