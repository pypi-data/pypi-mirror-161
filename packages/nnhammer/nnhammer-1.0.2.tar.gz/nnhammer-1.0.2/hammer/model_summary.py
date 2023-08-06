from collections import OrderedDict

import numpy as np
from torch.nn import Module


class ModelSummary:
    def __init__(self, model: Module):
        self.summary = OrderedDict()
        self.total = 0
        for name, module in model.named_children():
            num_parameters = sum(np.prod(parameter.shape) for parameter in module.parameters())
            self.total += num_parameters
            if num_parameters >= 1e6:
                num_parameters = "{:.2f}M".format(num_parameters / 1e6)
            else:
                num_parameters = "{:,}".format(num_parameters)
            self.summary[name] = (type(module).__name__, num_parameters)

        if self.total >= 1e6:
            self.total = "{:.2f}M".format(self.total / 1e6)
        else:
            self.total = "{:,}".format(self.total)

    def __str__(self):
        summary_str = "\n|{:-^60s}|\n".format("Model Summary")
        summary_str += "|{0:^13s}|{1:^29s}|{2:^16s}|\n".format("Module", "Type", "# of Params")
        summary_str += "|{}|\n".format("-" * 60)
        for k, v in self.summary.items():
            summary_str += "|{0:^13s}|{1:^29s}|{2:^16s}|\n".format(k, v[0], v[1])
            summary_str += "|{}|\n".format("-" * 60)
        summary_str += "|{0:^13s}|{1:^29s}|{2:^16s}|\n".format(str(len(self.summary)), "Total", self.total)
        summary_str += "|{}|\n".format("-" * 60)
        return summary_str
