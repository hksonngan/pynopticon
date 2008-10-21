"""
<name>Sift</name>
<description>Scale invariant feature transform.</description>
<icon>icons/kNearestNeighbours.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>5</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
import pynopticon
import pynopticon.features
from pynopticon import Images,Descriptors

class OWSift(OWWidget):
    settingsList = ["useLazyEvaluation", "Octave", "Levels", "FirstOctave", "PeakThresh", "EdgeThresh", "NormThresh", "Orientations"]

    def __init__(self, parent=None, signalManager = None, name='sift'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Images PIL", Images, self.setData)]
        self.outputs = [("Descriptors", Descriptors)]

        
        
        # Settings
        self.name = name
	self.sift = None

	self.useLazyEvaluation = pynopticon.useLazyEvaluation
	
        self.Octave = 6
        self.Levels = 3
        self.FirstOctave = 0
        self.PeakThresh = 0
        self.EdgeThresh = 10
	self.NormThresh = 0
        self.Orientations = 0

        self.loadSettings()
        
        self.data = None                    # input data set

        wbN = OWGUI.widgetBox(self.controlArea, "Sift Settings")
        OWGUI.spin(wbN, self, "Octave", -1, 8, 1, None, "Octaves   ", orientation="horizontal")
        OWGUI.spin(wbN, self, "Levels", 1, 8, 1, None, "Levels   ", orientation="horizontal")
        OWGUI.spin(wbN, self, "FirstOctave", 0, 8, 1, None, "First Octave ", orientation="horizontal")
        OWGUI.spin(wbN, self, "PeakThresh", -1, 8, 1, None, "PeakThresh", orientation="horizontal")
        OWGUI.spin(wbN, self, "EdgeThresh", -1, 8, 1, None, "EdgeThresh", orientation="horizontal")
	OWGUI.spin(wbN, self, "NormThresh", -1, 8, 1, None, "NormThresh", orientation="horizontal")    
        OWGUI.spin(wbN, self, "Orientations", 0, 1, 1, None, "Force computation of orientations", orientation="horizontal")
        wbS = OWGUI.widgetBox(self.controlArea, "Widget Settings")
        OWGUI.checkBox(wbS, self, "useLazyEvaluation", "Use lazy evaluation")
        OWGUI.separator(self.controlArea)
        
        OWGUI.button(self.controlArea, self, "&Apply Settings", callback = self.applySettings, disabled=0)

        self.resize(100,250)


    def applySettings(self):
	changed = False
	
	if self.sift is not None:
	    if pynopticon.applySettings(self.settingsList, self, kwargs=self.sift.kwargs):
		self.sendData()

    def sendData(self):
	self.send("Descriptors", self.sift.outputSlot)
	
    def setData(self, slot):
        if not slot:
            return
	if self.sift is None:
	    self.sift = pynopticon.features.SiftValedi(Octave=self.Octave, Levels=self.Levels, FirstOctave=self.FirstOctave, PeakThresh=self.PeakThresh, EdgeThresh=self.EdgeThresh, Orientations=self.Orientations, useLazyEvaluation=self.useLazyEvaluation)

	    self.sift.inputSlot.registerInput(slot)

	self.sendData()
        
if __name__ == "__main__":
    a=QApplication(sys.argv)
    ows=OWSift()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()

    
    
