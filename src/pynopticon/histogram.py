import pynopticon
import pynopticon.slots
import numpy

class Histogram(object):
    def __init__(self, bins, useLazyEvaluation=pynopticon.useLazyEvaluation):
        self.useLazyEvaluation = useLazyEvaluation
        self.bins = bins
        
        inputType = pynopticon.slots.VectorType(shape=['flatarray'])
        outputType = pynopticon.slots.VectorType(shape='flatarray')

        self.inputSlot = pynopticon.slots.InputSlot(name='vector',
                                               acceptsType=inputType)

        self.outputSlot = pynopticon.slots.OutputSlot(name='histogram',
                                                 inputSlot = self.inputSlot,
                                                 slotType = 'sequential',
                                                 processFunc = pynopticon.weakmethod(self, 'histogram'),
						 outputType = outputType,
                                                 useLazyEvaluation = self.useLazyEvaluation)

        
    def histogram(self, vector):
        if pynopticon.verbosity > 0:
            print "Computing histogram with %i bins..." % self.bins
            if pynopticon.verbosity > 1:
                print numpy.histogram(vector, bins = self.bins, range=(0,self.bins))[0]
        return numpy.histogram(vector, bins = self.bins, range=(0, self.bins))[0]


class Concatenate(object):
    def __init__(self, useLazyEvaluation=pynopticon.useLazyEvaluation):
        self.useLazyEvaluation = useLazyEvaluation
        
        self.inputType = pynopticon.slots.VectorType(shape=['flatarray'])
        self.outputType = pynopticon.slots.VectorType(shape='flatarray')
        self.inputSlots = []

        self.inputSlot = property(fget=self.__createSlot)
        
        self.outputSlot = pynopticon.slots.OutputSlot(name='concatenated',
                                                 iterator=pynopticon.weakmethod(self, 'concatenate'),
						 outputType=self.outputType,
                                                 useLazyEvaluation = self.useLazyEvaluation)

    def __createSlot(self):
        # For every input we need to have a different inputSlot
        # TODO: check if slot is already registered
	
        inputSlot = pynopticon.slots.InputSlot(name='vector',
                                          acceptsType=self.inputType)

        self.inputSlots.append(inputSlot)

        return inputSlot
        

    def concatenate(self):
        # Pool from every input slot until is StopIteration raised
        output = numpy.array()
        
        try:
            while True:
                for slot in self.inputSlots:
                    # Receive one element
                    output = numpy.concatenate(output, slot.next())

                yield output

        except StopIteration:
            raise StopIteration

        
        
