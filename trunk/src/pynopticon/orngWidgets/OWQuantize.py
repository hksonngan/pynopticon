"""
<name>Quantize</name>
<description>Return the closest cluster center.</description>
<icon>icons/MDS.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>15</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
from exceptions import Exception
import pynopticon.cluster
from pynopticon import Codebook,Clusters,Descriptors

class OWQuantize(OWWidget):
    settingsList = ['useLazyEvaluation']

    def __init__(self, parent=None, signalManager = None, name='kmeans'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Codebook", Codebook, self.setCodebook), ("Data", Descriptors, self.setData)]
        self.outputs = [("Clusters", Clusters)]

        self.useLazyEvaluation = pynopticon.useLazyEvaluation
        
        # Settings
        self.name = name
        self.loadSettings()
                
        wbN = OWGUI.widgetBox(self.controlArea, "Quantization settings")

        
        OWGUI.checkBox(wbN, self, "useLazyEvaluation", "Use lazy evaluation")
        OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.applySettings, disabled=0)

        self.resize(100,150)

        self.quantize = pynopticon.cluster.Quantize(useLazyEvaluation=self.useLazyEvaluation)

    def applySettings(self):
        pynopticon.applySettings(self.settingsList, self, obj=self.quantize, outputSlot=self.quantize.outputSlot)

    def setData(self,slot):
        if not slot:
            return

        self.quantize.inputSlotVec.registerInput(slot)
        self.send("Clusters", self.quantize.outputSlot)

    def setCodebook(self, slot):
        if not slot:
            return

        self.quantize.inputSlotCodebook.registerInput(slot)
        self.send("Clusters", self.quantize.outputSlot)
        
        

def main():
    a=QApplication(sys.argv)
    ows=OWQuantize()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
    
if __name__ == "__main__":
    main()
    
