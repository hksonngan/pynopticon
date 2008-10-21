"""
<name>Transform</name>
<description>Input transformations for dimensionality reduction</description>
<icon>icons/LinearProjection.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>14</priority>
"""

from OWWidget import *
import OWGUI
import pynopticon
import pynopticon.transforms
from pynopticon import Histograms,Labels

class OWTransform(OWWidget):
    settingsList = ['transtype', 'kernel', 'lazyEvaluation']

    def __init__(self, parent=None, signalManager = None, name='filter'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Untransformed Data", Histograms, self.setData), ("Labels", Labels, self.setLabels)]
        self.outputs = [("Transformed Data", Histograms)]

        self.useLazyEvaluation = pynopticon.useLazyEvaluation
        
        # Settings
        self.name = name
        self.transform = None
        self.transidx = 1
        self.transtype = None
        self.transtypes = ['none', 'PCA','KPCA', 'LLE']
        self.kernel = None
        self.kernelidx = 1
        self.kerneltypes = ['linear_kernel', 'gaussian_kernel', 'chi2_kernel']
        self.loadSettings()

        self.data = None                    # input data set

        wbN = OWGUI.widgetBox(self.controlArea, "Transformation Settings")
        self.transcombo = OWGUI.comboBoxWithCaption(wbN, self, "transidx", "Transform type: ", items=self.transtypes, valueType = int)
        self.kernelcombo = OWGUI.comboBoxWithCaption(wbN, self, "kernelidx", "Kernel type: ", items=self.kerneltypes, valueType = int)
        
        wbS = OWGUI.widgetBox(self.controlArea, "Widget Settings")
        OWGUI.checkBox(wbS, self, "useLazyEvaluation", "Use lazy evaluation")
        OWGUI.separator(self.controlArea)
        
        OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.applySettings, disabled=0)

        self.resize(100,150)


    def applySettings(self):
        if self.transform:
            self.transtype = self.transtypes[self.transidx]
            self.kernel = self.kerneltypes[self.kernelidx]
            if pynopticon.applySettings(self.settingsList, self, obj=self.transform, outputSlot=self.transform.outputSlot):
                self.sendData()
        
    def sendData(self):
        self.send("Transformed Data", self.transform.outputSlot)

    def setLabels(self, slot):
        if not slot:
            return
        if self.transform is None:
            self.transform = pynopticon.transforms.Transform(transtype=self.transtypes[self.transidx],
                                                        kernel=self.kerneltypes[self.kernelidx],
                                                        useLazyEvaluation=self.useLazyEvaluation)

        self.transform.inputSlotLabels.registerInput(slot)

        self.sendData()
            
    def setData(self, slot):
        if not slot:
            return
        if self.transform is None:
            self.transform = pynopticon.transforms.Transform(transtype=self.transtypes[self.transidx],
                                                        kernel=self.kerneltypes[self.kernelidx],
                                                        useLazyEvaluation=self.useLazyEvaluation)

        self.transform.inputSlotData.registerInput(slot)

        self.sendData()
        
if __name__ == "__main__":
    a=QApplication(sys.argv)
    ows=OWTransform()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
