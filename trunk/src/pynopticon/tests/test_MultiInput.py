import unittest
import pynopticon
import pynopticon.slots
import pynopticon.combine
import numpy as np

numSlots = 100

class TestMultiInput(unittest.TestCase):
    def setUp(self):
        # Create some output slots
        self.outputSlots = []

        for i in xrange(numSlots):
            self.outputSlots.append(pynopticon.slots.OutputSlot(name=str(i), sequence=range(numSlots)*i, outputType=pynopticon.slots.ImageType()))

        # Create the MultiSlot
        self.inputSlot = pynopticon.slots.MultiInputSlot(name='testCase')

        # Connect outputslots to the multislot
        for outputSlot in self.outputSlots:
            self.inputSlot.registerInput(outputSlot)

    def connected(self, numConnected=numSlots):
        self.assertEqual(len(self.inputSlot.senderSlots), numConnected)

    def iterating(self):
        for idx,output in enumerate(self.inputSlot):
            self.assertEqual(output, [i*idx for i in xrange(numSlots)])

    def testConnected(self):
        self.connected()

    def testIterating(self):
        self.iterating()
        self.iterating()

    def testDelete(self):
        del self.outputSlots[0]
        self.connected(numConnected=numSlots-1)
        del self.outputSlots[2]
        self.connected(numConnected=numSlots-2)

    def testReconnect(self):
        self.inputSlot.registerInput(self.outputSlots[2])
        self.connected()
        self.iterating()

class TestCombiner(TestMultiInput):
    def setUp(self):
        # Create some output slots
        self.outputSlots = []

        for i in xrange(numSlots):
            self.outputSlots.append(pynopticon.slots.OutputSlot(name=str(i), sequence=range(numSlots)*i, outputType=pynopticon.slots.ImageType()))

        # Create the Combiner
        self.combiner = pynopticon.combine.Combiner()
        self.inputSlot = self.combiner.inputSlot

        # Connect outputslots to the multislot
        for outputSlot in self.outputSlots:
            self.inputSlot.registerInput(outputSlot)

    def iterating(self):
        for idx,output in enumerate(self.combiner.outputSlot):
            self.assertEqual(output, np.concatenate([i*idx for i in xrange(numSlots)]))

        
suite_multiinput = unittest.TestLoader().loadTestsFromTestCase(TestMultiInput)
unittest.TextTestRunner(verbosity=3).run(suite_multiinput)

suite_combiner = unittest.TestLoader().loadTestsFromTestCase(TestCombiner)
unittest.TextTestRunner(verbosity=3).run(suite_combiner)
