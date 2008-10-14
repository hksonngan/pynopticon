import unittest
import pynopticon.ImageDataset
import pynopticon.cluster
import pynopticon.tests
import pynopticon.histogram
import pynopticon.filter
import pynopticon.transforms
import pynopticon.features
import pynopticon.score
import hcluster

import pynopticon
import numpy
import os.path
import gc

class testAll(unittest.TestCase):
    def setUp(self):
        self.path = pynopticon.__path__[0]
        self.pathtest = pynopticon.tests.__path__[0]
        self.imgDataset = pynopticon.ImageDataset.ImageDataset()
        #self.imgDataset.loadFromXML(os.path.join(self.pathtest, 'test_valid.xml'))
        self.imgDataset.loadFromXML(os.path.join(self.path, 'datasets', 'caltech_small.xml'))

        self.imgDataset.prepare()

    def createDescr(self):
        ft = pynopticon.filter.Filter(filter='none')
        sft = pynopticon.features.SiftValedi()
        #rce = pynopticon.features.Nowozin('color')
        #rce = pynopticon.features.SiftRobHess()
        #rce = pynopticon.features.SiftValedi()
        
        ft.inputSlot.registerInput(self.imgDataset.outputSlotTrain)
        #sft.InputSlot.registerInput(ft.outputSlot)
        sft.inputSlot.registerInput(ft.outputSlot)
        pynopticon.saveSlots('sft.pickle', sft.outputSlot)
        return sft
    
    def testGenerator(self):
        CLUSTERS = 500
        #from IPython.Debugger import Tracer; debug_here = Tracer()
        #debug_here()
        #rce = self.createDescr()
        #rce = pynopticon.loadSlots('rce.pickle')

        ft = pynopticon.filter.Filter(filter='none')
        #sft = pynopticon.features.Nowozin('edge')
	sft = pynopticon.features.SiftValediExec()
        km = pynopticon.cluster.Kmeans(CLUSTERS)
        qt = pynopticon.cluster.Quantize()
        hg = pynopticon.histogram.Histogram(CLUSTERS)
        nz = pynopticon.transforms.Normalize('none')
        tf = pynopticon.transforms.Transform('none')
        nz2 = pynopticon.transforms.Normalize('none')
        sc = pynopticon.score.Score()
        pd = pynopticon.score.PairwiseDistances(metric='euclidean')

        ft.inputSlot.registerInput(self.imgDataset.outputSlotTrain)
        sft.inputSlot.registerInput(ft.outputSlot)
        #km.inputSlot.registerInput(rce.outputSlot)
        km.inputSlot.registerInput(sft.outputSlot)
        #pynopticon.saveSlots('km.pickle', km.outputSlot)
        #km = pynopticon.loadSlots('km.pickle')
        
        #km = pynopticon.loadSlots('km.pickle')
        qt.inputSlotCodebook.registerInput(km.outputSlot)
        qt.inputSlotVec.registerInput(sft.outputSlot)
        #qt.inputSlotVec.registerInput(rce.outputSlot)
        hg.inputSlot.registerInput(qt.outputSlot)
        nz.inputSlot.registerInput(hg.outputSlot)
        tf.inputSlotData.registerInput(nz.outputSlot)
        tf.inputSlotLabels.registerInput(self.imgDataset.outputSlotLabelsTrain)
        nz2.inputSlot.registerInput(tf.outputSlot)
        sc.inputSlotData.registerInput(nz2.outputSlot)
        sc.inputSlotLabels.registerInput(self.imgDataset.outputSlotLabelsTrain)

        #pd.inputSlot.registerInput(nz2.outputSlot)
        pd.inputSlot.registerInput(nz2.outputSlot)
        x = list(pd.outputSlot)
        print list(sc.outputSlot)
        #x = numpy.array(list(hg.outputSlot))
        #from IPython.Debugger import Tracer; debug_here = Tracer()
        #debug_here()

        #print list(sc.outputSlot)
        #del sft
        #self.assertRaises(AttributeError, list(hg.OutputSlot))
#       del km
#       self.assertRaises(AttributeError, list(hg.OutputSlot))
        
        #pynopticon.saveSlots('kmeansSlot.pickle', outputSlot = sft.OutputSlot)
        #savedslot = pynopticon.loadSlots('kmeansSlot.pickle')
        #print list(savedslot)
#       assert (list(km.OutputSlot), list(kmSlots['codebook']))
#       print list(km.OutputSlot)[0].shape


        #self.assertEqual([x[1] for x in data], [u'test1', u'test2'])
        #for x,y in zip(data, [numpy.array([475, 693, 531]), numpy.array([566, 782, 509])]):
        #    self.assertTrue(all(x[0] == y))
        
#     def testList(self):
#       sft = pynopticon.sift(self.imgDataset.getData())
#       km = pynopticon.cluster(sft.getData(), 3)
#       data = list(km.getData())
#       self.assertEqual([x[1] for x in data], [u'test1', u'test2'])
        #TODO: Call kmeans with fixed start vectors
        #for x,y in zip(data, [numpy.array([475, 693, 531]), numpy.array([566, 782, 509])]):
        #    self.assertTrue(all(x[0] == y))

suite = unittest.TestLoader().loadTestsFromTestCase(testAll)
unittest.TextTestRunner(verbosity=3).run(suite)
