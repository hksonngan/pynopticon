import unittest
import pynopticon
import pynopticon.slots
import gc

class TestTypes(unittest.TestCase):
    def setUp(self):
        pass
    
    def setTypesNoConversion(self):
        self.outType1 = pynopticon.slots.ImageType(format='PIL', color_space='RGB')
        self.inType2 = pynopticon.slots.ImageType(format=['PIL'], color_space=['RGB'])
        self.outType2 = pynopticon.slots.VectorType(shape='nestedlist')

    def setTypesConversion(self):
        self.outType1 = pynopticon.slots.ImageType(format='PIL', color_space='RGB')
        self.inType2 = pynopticon.slots.ImageType(format=['PIL'], color_space=['gray'])
        self.outType2 = pynopticon.slots.VectorType(shape='nestedlist')

    def setTypesIncompatible(self):
        self.outType1 = pynopticon.slots.ImageType(format='PIL', color_space='gray')
        self.inType2 = pynopticon.slots.ImageType(format=['PIL'], color_space=['RGB'])
        self.outType2 = pynopticon.slots.VectorType(shape='nestedlist')

    def setSlots(self):
        self.slotSend = pynopticon.slots.OutputSlot('sender',
                                              iterator=self.iterator,
                                              outputType=self.outType1)

        self.slotInput = pynopticon.slots.InputSlot('input',
                                              acceptsType=self.inType2)
        
        self.slotRecv = pynopticon.slots.OutputSlot('receiver',
					      inputSlot = self.slotInput,
					      processFunc=self.process,
					      outputType=self.outType2,
					      slotType='sequential')


    def setMultiInput(self):
        self.slotSend = pynopticon.slots.OutputSlot('sender', iterator=self.iterator)
        
        self.slotInput1 = pynopticon.slots.InputSlot('input1')
        self.slotInput2 = pynopticon.slots.InputSlot('input2')
        
        self.InputSlots = pynopticon.slots.Slots([self.slotInput1, self.slotInput2])
        self.InputSlots['input1'].registerInput(self.slotSend)
        self.InputSlots['input2'].registerInput(self.slotSend)
        
        
    def testSlotConnectNoConversion(self):
        self.setTypesNoConversion()
        self.setSlots()
        self.slotInput.registerInput(self.slotSend)
        self.assertEqual(self.slotRecv.processFunc.__name__, 'process')
        
    def testSlotConnectConversion(self):
        self.setTypesConversion()
        self.setSlots()
        self.slotInput.registerInput(self.slotSend)
        self.assertEqual([i.__name__ for i in self.slotInput.converters], ['_weakmethod'])
        self.assertEqual(self.slotRecv.processFunc.__name__, 'process')

    def testSlotIncompatible(self):
        self.setTypesIncompatible()
        self.setSlots()
        self.assertRaises(TypeError, self.slotInput.registerInput, self.slotSend)
        
    def testIterating(self):
        self.setTypesNoConversion()
        self.setSlots()
        self.slotInput.registerInput(self.slotSend)
        self.assertEqual([i for i in self.slotRecv], range(10))
        self.assertEqual([i for i in self.slotRecv], range(10))

    def testReconnect(self):
        self.setTypesNoConversion()
        self.setSlots()
        self.slotInput.registerInput(self.slotSend)
        self.slotSend = pynopticon.slots.OutputSlot('sender',
                                              sequence=range(11),
                                              outputType=self.outType1)
        self.slotInput.registerInput(self.slotSend)
        self.assertEqual([i for i in self.slotRecv], range(11))

    def testMultiInput(self):
        self.setMultiInput()
        self.slotRecv = pynopticon.slots.OutputSlot('receiver', iterator=self.iterMulti)
        self.assertEqual([i for i in self.slotRecv], [x+y for x,y in zip(range(10),range(10))])

    def testGroup(self):
        self.setTypesNoConversion()
        self.setSlots()
        self.slotInput.registerInput(self.slotSend)
        
        self.slotInput2 = pynopticon.slots.InputSlot('input2',
                                              acceptsType=self.inType2)
        
        self.slotRecv2 = pynopticon.slots.OutputSlot('receiver2',
					       inputSlot = self.slotInput2,
					       processFunc=self.process,
					       outputType=self.outType2,
					       slotType='sequential')

        self.slotInput2.registerInput(self.slotSend)

        self.assertEqual([i for i in self.slotRecv], range(10))
        self.assertEqual([i for i in self.slotRecv2], range(10))
        
    def iterMulti(self):
        input1 = list(self.InputSlots['input1'])
        for count,i in enumerate(self.InputSlots['input2']):
            yield input1[count] + i
        
    def process(self, item):
        return item

    def iterator(self):
        for i in xrange(10):
            yield i

suite = unittest.TestLoader().loadTestsFromTestCase(TestTypes)
unittest.TextTestRunner(verbosity=3).run(suite)
