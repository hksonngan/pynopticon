import unittest
from pynopticon.ImageDataset import ImageDataset
import pynopticon.tests
import os.path

class TestImageDataset(unittest.TestCase):
    def setUp(self):
        self.ImageDataset = ImageDataset()
        self.path = pynopticon.tests.__path__[0]
        self.pathTestImgs = os.path.join(pynopticon.tests.__path__[0], 'testImgs')
        self.setInvalid = [os.path.join(self.pathTestImgs, 'nonexisting.jpg'), os.path.join(self.pathTestImgs, 'test1.jpg')]
        self.setValid = [os.path.join(self.pathTestImgs,'test1.jpg'), os.path.join(self.pathTestImgs, 'test2.jpg')]
        
    def addCategories(self, set = None):
        if not set:
            set = self.setInvalid
        self.ImageDataset.addCategory()
        self.ImageDataset.addCategory('test1')
        self.ImageDataset.addCategory('test2', set)

    def testAddCategories(self):
        self.addCategories()
#       self.ImageDataset.saveToXML('test.xml')
        self.checkConsistency()
        
    def checkConsistency(self):
        self.assertEqual(self.ImageDataset.categories[0].name, '')
        self.assertEqual(self.ImageDataset.categories[1].name, 'test1')
        self.assertEqual(self.ImageDataset.categories[2].name, 'test2')
        self.assertEqual(self.ImageDataset.categories[2].fnames, self.setInvalid)

        
    def testDelCategories(self):
        self.addCategories()
        self.ImageDataset.delCategory(0)
        self.assertEqual(len(self.ImageDataset.categories), 2)
        self.assertEqual(self.ImageDataset.categories[0].name, 'test1')

        self.assertRaises(IndexError, self.ImageDataset.delCategory, 2)
        
        
    def testLoadFromXML(self, fname=None):
        if not fname:
            self.testSaveToXML()
            fname = os.path.join(self.path, 'test_saved.xml')
            
        self.ImageDataset.loadFromXML(fname)
        self.checkConsistency()
        
    def testSaveToXML(self):
        self.addCategories()
        self.ImageDataset.saveToXML(os.path.join(self.path, 'test_saved.xml'))
        del self.ImageDataset
        self.setUp()
        self.ImageDataset.loadFromXML(os.path.join(self.path, 'test_saved.xml'))
        self.checkConsistency()
        
    def testAddAndDelFnames(self):
        self.addCategories()
        self.ImageDataset.categories[1].addDir(self.pathTestImgs)
        self.assertEqual(self.ImageDataset.categories[1].fnames, self.setValid)
        self.ImageDataset.categories[1].delFile(os.path.join(self.pathTestImgs, 'test1.jpg'))
        self.assertEqual(self.ImageDataset.categories[1].fnames, [os.path.join(self.pathTestImgs, 'test2.jpg')])
        self.ImageDataset.categories[1].delID(0)
        self.assertEqual(len(self.ImageDataset.categories[1].fnames), 0)

    def testAccessNoContainer(self):
        self.addCategories()
	self.assertRaises(AttributeError, self.ImageDataset.__iter__)

    def testIterateFnames(self):
        self.addCategories()
        for x,y in zip(self.ImageDataset.categories[2], [os.path.join(self.pathTestImgs, 'nonexisting.jpg'), os.path.join(self.pathTestImgs, 'test1.jpg')]):
            self.assertEqual(x,y)

    def testSeqContainerValid(self):
        self.addCategories(set = self.setValid)
	self.ImageDataset.prepare()
        seqContainer = self.ImageDataset.OutputSlotTrain
        
    def testSeqContainerValidIter(self):
        self.addCategories(set = self.setValid)
	self.ImageDataset.prepare()
        seqContainer = self.ImageDataset.OutputSlotTrain

    def testSeqContainerInvalid(self):
        self.addCategories()
#        self.assertRaises(IOError, self.ImageDataset.getData)
	

suite = unittest.TestLoader().loadTestsFromTestCase(TestImageDataset)
unittest.TextTestRunner(verbosity=3).run(suite)
