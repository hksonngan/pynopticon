import numpy, PIL.Image
import pynopticon.sift
import pynopticon.ImageDataset
import unittest
import os.path
import pynopticon.tests

class TestSift(unittest.TestCase):
    def setUp(self):
	self.path = pynopticon.tests.__path__[0]
	self.imgDataset = pynopticon.ImageDataset.ImageDataset()
	self.imgDataset.loadFromXML(os.path.join(self.path, 'test_valid.xml'))
	self.imgDataset.prepare()
	
    def testSiftGenerator(self):
	#TODO: Check if values are correct descriptors
	self.sft = pynopticon.features.SiftValedi(Verbose=1)
	self.sft.InputSlot.registerInput(self.imgDataset.OutputSlotTrain)
	list(self.sft.OutputSlot)

    def testSiftList(self):
	self.sft = pynopticon.features.SiftValedi(Verbose=1)
	self.sft.InputSlot.registerInput(self.imgDataset.OutputSlotTrain)
	list(self.sft.OutputSlot)

suite = unittest.TestLoader().loadTestsFromTestCase(TestSift)
unittest.TextTestRunner(verbosity=3).run(suite)
	
