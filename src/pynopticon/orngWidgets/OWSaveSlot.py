"""
<name>SaveSlot</name>
<description>Save a slot to a file.</description>
<icon>icons/Save.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>3</priority>
"""
from OWWidget import *
import OWGUI
import pynopticon
from pynopticon import Descriptors, Codebook, Images, Labels, Histograms, Clusters

class OWSaveSlot(OWWidget):
    settingsList = []

    def __init__(self, parent=None, signalManager = None, name='SaveSlot'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Descriptors", Descriptors, self.setDataDescriptors),
		       ("Codebook", Codebook, self.setDataCodebook),
		       ("Images", Images, self.setDataImages),
		       ("Labels", Labels, self.setDataLabels),
		       ("Histograms", Histograms, self.setDataHistograms),
		       ("Clusters", Clusters, self.setDataClusters)]
	
        self.outputs = []

        self.useLazyEvaluation = pynopticon.useLazyEvaluation
        
        # Settings
        self.name = name
        self.loadSettings()

	self.fname = None
        self.slot = None
	
        
        OWGUI.button(self.controlArea, self, "Save to...", callback = self.browseFile, disabled=0)

        self.resize(50,150)

    def browseFile(self, filters=None):
        """Display a FileDialog and select an existing file, 
        or a dir (dir=1) or a new file (save=1).
        filters can be a list with all extensions to be displayed during browsing
        Returned is/are the selected item(s) with complete path."""
        if not filters:
            filters = ["All (*.*)"]

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)

        dialog.setFilters(QStringList(filters))
        dialog.setViewMode(QFileDialog.List)

        if not dialog.exec_():
            return None

        selected = dialog.selectedFiles()

        self.fname = str(selected[0])
	self.setData(self.slot)

    def setDataDescriptors(self, slot):
	self.setData(slot, Descriptors)

    def setDataCodebook(self, slot):
	self.setData(slot, Codebook)

    def setDataImages(self, slot):
	self.setData(slot, Images)

    def setDataLabels(self, slot):
	self.setData(slot, Labels)

    def setDataHistograms(self, slot):
	self.setData(slot, Histograms)

    def setDataClusters(self, slot):
	self.setData(slot, Clusters)
	
    def setData(self, slot, slotType=None):
	self.slot = slot
	if slotType:
	    self.slotType = slotType
	    
        if self.slot is None or self.fname is None:
            return

        pynopticon.saveSlots(self.fname, outputSlot=slot, slotType = self.slotType)

def main():
    a=QApplication(sys.argv)
    ows=OWSaveSlot()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
    
if __name__ == "__main__":
    main()
    
