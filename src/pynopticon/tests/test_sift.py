import numpy as np, PIL.Image
import pynopticon.features
import pynopticon.ImageDataset
import unittest
import os.path
import pynopticon.tests
import pynopticon

class TestSift(unittest.TestCase):
    def setUp(self):
        pynopticon.verbose = 2
        pynopticon.useOrange = False
	self.path = pynopticon.tests.__path__[0]
	self.imgDataset = pynopticon.ImageDataset.ImageDataset()
	self.imgDataset.loadFromXML(os.path.join(self.path, 'test_sift.xml'))
	self.imgDataset.prepare()
	
    def testSiftGenerator(self):
	#TODO: Check if values are correct descriptors
	self.sft = pynopticon.features.SiftValedi(Verbose=1)
	self.sft.inputSlot.registerInput(self.imgDataset.outputSlotTrain)
	self.descr = list(self.sft.outputSlot)
        self.validate()

    def testSiftList(self):
	self.sft = pynopticon.features.SiftValedi(Verbose=1)
	self.sft.inputSlot.registerInput(self.imgDataset.outputSlotTrain)
	self.descr = list(self.sft.outputSlot)
        self.validate()

    def validate(self):
        descr_orig = np.loadtxt(os.path.join(self.path, 'orig_descr_test1pgm.sift'), delimiter=',', dtype=np.uint8)
        np.testing.assert_array_almost_equal(np.array(self.descr)[0], descr_orig.T, decimal=-1)
        
        
suite = unittest.TestLoader().loadTestsFromTestCase(TestSift)
unittest.TextTestRunner(verbosity=3).run(suite)
	
