"""
<name>ExtractFeature</name>
<description>Different kinds of feature extractors.</description>
<icon>icons/SieveDiagram.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>6</priority>
"""
from OWWidget import *
import OWGUI
import pynopticon
import pynopticon.features
from pynopticon import Images, Descriptors

class OWExtractFeatures(OWWidget):
    settingsList = ['featureID', 'featureType', 'useLazyEvaluation']

    def __init__(self, parent=None, signalManager = None, name='ExtractFeatures'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Images PIL", Images, self.setData)]
        self.outputs = [("Descriptors", Descriptors)]

        self.useLazyEvaluation = pynopticon.useLazyEvaluation
        
        # Settings
        self.name = name
        self.feature = None
        self.featureID = 0
        self.featureType = None
        self.features = pynopticon.features.Nowozin.features
        self.loadSettings()

        self.data = None                    # input data set

        wbN = OWGUI.widgetBox(self.controlArea, "Feature Extractor Settings")
        self.filecombo = OWGUI.comboBoxWithCaption(wbN, self, "featureID", "Feature type: ", items=self.features, valueType = int)

        wbS = OWGUI.widgetBox(self.controlArea, "Widget Settings")
        OWGUI.checkBox(wbS, self, "useLazyEvaluation", "Use lazy evaluation")
        OWGUI.separator(self.controlArea)
        
        OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.applySettings, disabled=0)

        self.resize(100,150)


    def applySettings(self):
        if self.feature:
            self.featureType = self.features[self.featureID]
            if pynopticon.applySettings(self.settingsList, self, obj=self.feature, outputSlot=self.feature.outputSlot):
                self.sendData()
            
    def sendData(self):
        self.send("Descriptors", self.feature.outputSlot)
        
    def setData(self, slot):
        if not slot:
            return
        if self.feature is None:
            self.feature = pynopticon.features.Nowozin(featureType=self.features[self.featureID], useLazyEvaluation=self.useLazyEvaluation)

        self.feature.inputSlot.registerInput(slot)
        self.sendData()
        
if __name__ == "__main__":
    a=QApplication(sys.argv)
    ows=OWExtractFeatures()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
