import torch
from torch.nn import Module


class DiceLoss(Module):
    """
    One-hot encode is required. The shape of data has to be BN[spatial dimension]
    """

    def __init__(self, spatial_dims=None, class_reduction: str = 'none'):
        super().__init__()
        self.eps = 1e-6
        assert class_reduction in ['none', 'mean']
        self.class_reduction = class_reduction
        self.spatial_dims = spatial_dims

    def forward(self, input: torch.Tensor, target: torch.Tensor):
        assert input.size() == target.size()
        spatial_dims = self.spatial_dims if self.spatial_dims is not None else tuple(range(2, len(input.shape)))
        intersection = torch.sum(input * target, dim=spatial_dims)
        union = torch.sum(input + target, dim=spatial_dims)
        dc = (2. * intersection + self.eps) / (union + self.eps)
        dc_loss = 1.0 - dc
        if self.class_reduction == 'none':
            return torch.mean(dc_loss, dim=0)
        elif self.class_reduction == 'mean':
            return torch.mean(dc_loss)
