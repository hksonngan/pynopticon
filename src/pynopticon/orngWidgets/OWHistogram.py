"""
<name>Histogram</name>
<description>Compute Histograms.</description>
<icon>icons/Rank.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>18</priority>
"""
from OWWidget import *
import OWGUI
from exceptions import Exception
import pynopticon
import pynopticon.histogram
from pynopticon import Clusters,Histograms

class OWHistogram(OWWidget):
    settingsList = ['bins', 'useLazyEvaluation']

    def __init__(self, parent=None, signalManager = None, name='Histogram'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Data", Clusters, self.setData)]
        self.outputs = [("Histogram", Histograms)] # , ("Histograms", ExampleTable)]

        self.useLazyEvaluation = pynopticon.useLazyEvaluation
        
        # Settings
        self.name = name
	self.histogram = None
	self.bins = 200
        self.loadSettings()        

        self.data = None                    # input data set

        wbN = OWGUI.widgetBox(self.controlArea, "Histogram Settings")
        OWGUI.spin(wbN, self, "bins", 1, 100000, 100, None, "Number of bins  ", orientation="horizontal")

        OWGUI.separator(self.controlArea)
	wbS = OWGUI.widgetBox(self.controlArea, "Widget Settings")
        OWGUI.checkBox(wbS, self, "useLazyEvaluation", "Use lazy evaluation")
        OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.applySettings, disabled=0)

        self.resize(100,150)


    def applySettings(self):
	if self.histogram:
	    if pynopticon.applySettings(self.settingsList, self, obj=self.histogram, outputSlot=self.histogram.outputSlot):
		self.sendData()
	
    def setData(self,slot):
        if slot is None:
            return

	if self.histogram is None:
	    self.histogram = pynopticon.histogram.Histogram(self.bins, useLazyEvaluation=self.useLazyEvaluation)

	self.histogram.inputSlot.registerInput(slot)
	    
	self.sendData()

    def sendData(self):
	self.send("Histogram", self.histogram.outputSlot)
	
def main():
    a=QApplication(sys.argv)
    ows=OWHistogram()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
    
if __name__ == "__main__":
    main()
    
