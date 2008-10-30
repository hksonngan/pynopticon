import unittest
import pynopticon.ImageDataset
import pynopticon.cluster
import pynopticon.tests
import pynopticon.histogram
import pynopticon.filter
import pynopticon.transforms
import pynopticon.features
import pynopticon.score

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
        CLUSTERS = 200
        #from IPython.Debugger import Tracer; debug_here = Tracer()
        #debug_here()
        #rce = self.createDescr()
        #rce = pynopticon.loadSlots('rce.pickle')

        ft = pynopticon.filter.Filter(filter='none')
        #sft = pynopticon.features.Nowozin('edge')
	sft = pynopticon.features.SiftValedi()
        km = pynopticon.cluster.Kmeans(CLUSTERS)
        qt = pynopticon.cluster.Quantize()
        hg = pynopticon.histogram.Histogram(CLUSTERS)
        nz = pynopticon.transforms.Normalize('none')
        tf = pynopticon.transforms.Transform('none')
        nz2 = pynopticon.transforms.Normalize('none')
        sc = pynopticon.score.Score()
        #pd = pynopticon.score.PairwiseDistances(metric='euclidean')

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
        #pd.inputSlot.registerInput(nz2.outputSlot)
        x = list(sc.outputSlot)
        print x


suite = unittest.TestLoader().loadTestsFromTestCase(testAll)
unittest.TextTestRunner(verbosity=3).run(suite)
