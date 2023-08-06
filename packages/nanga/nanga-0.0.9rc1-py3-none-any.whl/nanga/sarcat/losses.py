# @copyright  Copyright (c) 2018-2020 Opscidia

from torch import nn
import torch
from torch.nn import functional as F
from data.utils import get_mcat_masks, cats2mcats, get_class_weights


class NestedBCELoss(nn.Module):
    ''' A nested form of binary cross entropy.
    From the category predictions it pulls out the master category
    predictions, using the utils.cats2mcats function, which enables
    a positive master category prediction even though all individual
    category predictions within that master category have sigmoid values
    less than 0.50.
    It then computes the binary cross entropy of the category- and master
    category predictions, with the given class weights, and scales the
    two losses in accordance with mcat_ratio.
    INPUT
        cat_weights: torch.FloatTensor
            The class weights for the categories
        mcat_weights: torch.FloatTensor
            The class weights for the master categories
        mcat_ratio: float = 0.1
            The ratio between the category loss and the master category loss
        data_dir: str = '.data'
            The path to the data directory
    '''
    def __init__(self, cat_weights, mcat_weights, mcat_ratio: float = 0.1,
        cats = None, mcats_dict = None, device='cuda'):
        super().__init__()
        self.masks = get_mcat_masks(cats, mcats_dict, device)
        self.cat_weights = cat_weights
        self.mcat_weights = mcat_weights
        self.mcat_ratio = mcat_ratio
        self.device = device
        self.cats = cats
        self.mcats_dict = mcats_dict,
    
    def forward(self, pred, target, weighted: bool = True):
        mpred, mtarget = cats2mcats(pred, target, masks = self.masks, cats = self.cats, mcats_dict = self.mcats_dict, device=self.device)

        cat_loss = F.binary_cross_entropy_with_logits(pred, target,
            pos_weight = self.cat_weights if weighted else None)
        print(mpred.is_cuda, mtarget.is_cuda, self.mcat_weights.is_cuda)
        mcat_loss = F.binary_cross_entropy_with_logits(mpred, mtarget,
            pos_weight = self.mcat_weights if weighted else None)
        
        cat_loss *= 1 - self.mcat_ratio
        mcat_loss *= self.mcat_ratio

        return cat_loss + mcat_loss

    def cuda(self):
        self.masks = self.masks.cuda()
        self.cat_weights = self.cat_weights.cuda()
        self.mcat_weights = self.mcat_weights.cuda()
        return self
