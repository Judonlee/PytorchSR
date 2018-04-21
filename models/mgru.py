import torch
import torch.nn as nn
from torch.autograd import Variable

from data.data_utils import PHNS
from models.model import Model
from models.modules import MinimalGRU, SeqLinear
from settings.hparam import hparam as hp


class MinimalGRUNet(Model):

    def __init__(self, is_bidirection=True, num_layers=1, is_cuda=True):
        super().__init__()
        self.is_bidirection = is_bidirection
        self.hidden_size = hp.train.hidden_units
        self.num_layers = num_layers
        self.is_cuda = is_cuda

        output_hidden_nodes = self.hidden_size * 2 if is_bidirection else self.hidden_size

        self.mgru = MinimalGRU(hp.default.n_mfcc, self.hidden_size,
                               num_layers=self.num_layers, is_bidirection=self.is_bidirection)
        self.output = SeqLinear(output_hidden_nodes, len(PHNS))
        self.output_drop = nn.Dropout(0.2)
        self.ppg_output = nn.Softmax()

    def forward(self, x):
        batch_size = x.size()[0]

        hx = Variable(torch.ones(2 * self.num_layers, batch_size, self.hidden_size))
        if self.is_cuda:
            hx = hx.cuda()
        net = self.mgru(x, hx)
        net = self.output_drop(self.output(net))
        return net