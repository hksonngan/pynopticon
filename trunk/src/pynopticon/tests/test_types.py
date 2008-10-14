import pynopticon.slots
import unittest
import PIL.Image
import numpy

class TestTypes(unittest.TestCase):
    def setUp(self):
	pass

    def testConvertRGB(self):
	a = pynopticon.slots.ImageType(format=['PIL'], color_space=['gray'])
	b = pynopticon.slots.ImageType(format='PIL', color_space='RGB')
	self.assertEqual(a.compatible(b)[0].dataType, {'color_space': 'gray', 'format': 'PIL'})
	self.assertEqual(a.compatible(b)[1][0].__name__, '_weakmethod')

    def testIncompatibleType(self):
	a = pynopticon.slots.ImageType(format=['PIL'], color_space=['RGB'])
	b = pynopticon.slots.VectorType(format='PIL', color_space='gray')
	assert a.compatible(b) is False

    def testIncompatibleAttr(self):
	a = pynopticon.slots.ImageType(format=['PIL'], color_space=['RGB'])
	b = pynopticon.slots.ImageType(format='PIL', color_space='gray')
	assert a.compatible(b) is False	

    def testNestedVectorToFlat(self):
	a = pynopticon.slots.VectorType(shape=['flatarray'])
	b = pynopticon.slots.VectorType(shape='nestedlist')
	self.assertEqual(a.compatible(b)[0].dataType, {'shape': 'flatarray'})
	self.assertEqual(a.compatible(b)[1][0].__name__, '_weakmethod')


suite = unittest.TestLoader().loadTestsFromTestCase(TestTypes)
unittest.TextTestRunner(verbosity=3).run(suite)
