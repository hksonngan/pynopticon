"""
<name>SlotToExampleTable</name>
<description>Converts an pynopticon slot to an orange ExampleTable.</description>
<icon>icons/DataTable.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>25</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
from pynopticon import Histograms,Labels

import pynopticon.combine
import weakref
import orange

class OWSlotToExampleTable(OWWidget):
    settingsList = []

    def __init__(self, parent=None, signalManager = None, name='ListToExampleTable'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Histograms", Histograms, self.setData, Multiple), ("Labels", Labels, self.setLabels)]
        self.outputs = [("Table", ExampleTable)]

        self.combiner = None
        
        # Settings
        self.name = name
        self.useLazyEvaluation = True
        
        self.loadSettings()

        self.labels = None
        #OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.apply, disabled=0)

        self.resize(100,250)


    def setLabels(self, slot):
        if slot is None:
            return
        self.labels = weakref.ref(slot)
        if self.combiner is not None:
            self.createExampleTable()
            
    def setData(self, slot, id):
        if slot is None:
            if self.combiner:
                # Signal to remove the slot
                if id in self.combiner.inputSlot.senderSlots.keys():
                    del self.combiner.inputSlot.senderSlots[id]
            return
        

        if self.combiner is None: # Create multi input combiner
            self.combiner = pynopticon.combine.Combiner(useLazyEvaluation=self.useLazyEvaluation)

        # Register the sender slot (multiple inputs possible)
        self.combiner.inputSlot.registerInput(slot, senderID=id)

        if self.labels is None:
            return

        if self.labels is not None:
            self.createExampleTable()
            
    def createExampleTable(self):
        # Create orange.ExampleTable
        datalabels = []

        data = list(self.combiner.outputSlot)
        labels = list(self.labels())
        
        for vec,label in zip(data, labels):
            datalabels.append(list(vec) + [str(label)])
            

        domain = orange.Domain([orange.FloatVariable('a%i'%x) for x in xrange(len(data[0]))] + [orange.EnumVariable("class", values = orange.StringList([str(x) for x in self.labels().container.classes]))])
        orngTable = orange.ExampleTable(domain, datalabels)

        self.send("Table", orngTable)
        
if __name__ == "__main__":
    a=QApplication(sys.argv)
    ows=OWSift()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
 
    
