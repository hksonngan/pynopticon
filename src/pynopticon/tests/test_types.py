import pynopticon.datatypes
import unittest
import PIL.Image
import numpy

class TestTypes(unittest.TestCase):
    def setUp(self):
	pass

    def testConvertRGB(self):
	a = pynopticon.datatypes.ImageType(format=['PIL'], color_space=['gray'])
	b = pynopticon.datatypes.ImageType(format='PIL', color_space='RGB')
	self.assertEqual(a.compatible(b)[0].dataType, {'color_space': 'gray', 'format': 'PIL'})
	self.assertEqual(a.compatible(b)[1][0].__name__, '_weakmethod')

    def testIncompatibleType(self):
	a = pynopticon.datatypes.ImageType(format=['PIL'], color_space=['RGB'])
	b = pynopticon.datatypes.VectorType(format='PIL', color_space='gray')
	assert a.compatible(b) is False

    def testIncompatibleAttr(self):
	a = pynopticon.datatypes.ImageType(format=['PIL'], color_space=['RGB'])
	b = pynopticon.datatypes.ImageType(format='PIL', color_space='gray')
	assert a.compatible(b) is False	

    def testNestedVectorToFlat(self):
	a = pynopticon.datatypes.VectorType(shape=['flatarray'])
	b = pynopticon.datatypes.VectorType(shape='nestedlist')
	self.assertEqual(a.compatible(b)[0].dataType, {'shape': 'flatarray'})
	self.assertEqual(a.compatible(b)[1][0].__name__, '_weakmethod')


suite = unittest.TestLoader().loadTestsFromTestCase(TestTypes)
unittest.TextTestRunner(verbosity=3).run(suite)
