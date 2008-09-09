"""
<name>Filter</name>
<description>Apply a filter to the images.</description>
<icon>icons/unknown.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>7</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
import pynopticon
import pynopticon.filter
from pynopticon.slots import SeqContainer

class OWFilter(OWWidget):
    settingsList = ['filterID']

    def __init__(self, parent=None, signalManager = None, name='filter'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Images PIL", SeqContainer, self.setData)]
        self.outputs = [("Filtered Images PIL", SeqContainer)]

        self.useLazyEvaluation = pynopticon.useLazyEvaluation
        
        # Settings
        self.name = name
	self.filter = None
        self.filterID = 5
        self.filters = pynopticon.filter.Filter().filters.keys()
        self.loadSettings()

        self.data = None                    # input data set

        wbN = OWGUI.widgetBox(self.controlArea, "Filter Settings")
        self.filecombo = OWGUI.comboBoxWithCaption(wbN, self, "filterID", "Filters: ", items=self.filters, valueType = str)

        wbS = OWGUI.widgetBox(self.controlArea, "Widget Settings")
        OWGUI.checkBox(wbS, self, "useLazyEvaluation", "Use lazy evaluation")
        OWGUI.separator(self.controlArea)
        
        OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.applySettings, disabled=0)

        self.resize(100,150)


    def applySettings(self):
        changed = False
        
        if self.filter is not None:
            if pynopticon.applySettings(self.settingsList, self, self.filter):
                changed = True

            if changed:
                self.sendData()

    def sendData(self):
        self.send("Filtered Images PIL", self.filter.outputSlot)
        
    def setData(self, slot):
        if not slot:
            return
        if self.filter is None:
            self.filter = pynopticon.filter.Filter(filter=self.filters[self.filterID], useLazyEvaluation=self.useLazyEvaluation)

            self.filter.inputSlot.registerInput(slot)

        self.sendData()
        
if __name__ == "__main__":
    a=QApplication(sys.argv)
    ows=OWFilter()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
