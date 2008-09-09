"""
<name>KMeans</name>
<description>KMeans Clustering.</description>
<icon>icons/KMeans.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>10</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
from exceptions import Exception
import pynopticon
import pynopticon.cluster
from pynopticon.slots import SeqContainer

class OWKmeans(OWWidget):
    settingsList = ["numClusters", "maxiter", "numruns", "sampleFromData", "useLazyEvaluation"]
    
    def __init__(self, parent=None, signalManager = None, name='kmeans'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Data", SeqContainer, self.setData)]
        self.outputs = [("Codebook", SeqContainer)] # , ("Histograms", ExampleTable)]

        self.useLazyEvaluation = pynopticon.useLazyEvaluation
        
        # Settings
        self.name = name
        self.kmeans = None
        self.loadSettings()

        self.numClusters = 20
        self.maxiter = 0
        self.numruns = 1
        self.sampleFromData = 1.0
        
        wbN = OWGUI.widgetBox(self.controlArea, "kMeans Settings")
        OWGUI.spin(wbN, self, "numClusters", 1, 100000, 100, None, "Number of clusters   ", orientation="horizontal")
        OWGUI.spin(wbN, self, "maxiter", 0, 100000, 1, None, "Maximum number of iterations", orientation="horizontal")
        OWGUI.spin(wbN, self, "numruns", 0, 100000, 1, None, "Number of runs ", orientation="horizontal")
        OWGUI.widgetLabel(wbN, 'Use x% of the data')
        OWGUI.lineEdit(wbN, self, 'sampleFromData', valueType=float)
        OWGUI.separator(self.controlArea)
	wbS = OWGUI.widgetBox(self.controlArea, "Widget Settings")
        OWGUI.checkBox(wbS, self, "useLazyEvaluation", "Use lazy evaluation")
        OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.applySettings, disabled=0)

        self.resize(100,150)


    def applySettings(self):
        if self.kmeans:
            if pynopticon.applySettings(self.settingsList, self, obj=self.kmeans, outputSlot=self.kmeans.outputSlot):
                self.sendData()
            
    def setData(self,slot):
        if slot is None:
            return
	if self.kmeans is None:
	    self.kmeans = pynopticon.cluster.Kmeans(numClusters = self.numClusters,
                                               maxiter = self.maxiter,
                                               numruns = self.numruns,
                                               sampleFromData = self.sampleFromData,
                                               useLazyEvaluation=self.useLazyEvaluation)
	
	self.kmeans.inputSlot.registerInput(slot)

        self.sendData()

    def sendData(self):
        self.send("Codebook", self.kmeans.outputSlot)

def main():
    a=QApplication(sys.argv)
    ows=OWKmeans()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
    
if __name__ == "__main__":
    main()
    
