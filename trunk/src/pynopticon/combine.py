import pynopticon
import pynopticon.slots
import numpy as np

class Combiner(object):
    """Module that can receive many inputs and stacks them together."""

    def __init__(self, useLazyEvaluation=pynopticon.useLazyEvaluation):
        self.inputSlot = pynopticon.slots.MultiInputSlot(name='data')
        self.outputSlot = pynopticon.slots.OutputSlot(name='combined data',
                                                 iterator=pynopticon.weakmethod(self, 'iterator'),
                                                 useLazyEvaluation=useLazyEvaluation)

    def iterator(self):
        # Pool data
        for data in self.inputSlot:
            yield np.concatenate(data)
