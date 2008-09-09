"""
<name>SaveSlot</name>
<description>Save a slot to a file.</description>
<icon>icons/Save.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>3</priority>
"""
import orngOrangeFoldersQt4
from OWWidget import *
import OWGUI
from exceptions import Exception
import pynopticon
from pynopticon.slots import SeqContainer

class OWSaveSlot(OWWidget):
    settingsList = []

    def __init__(self, parent=None, signalManager = None, name='kmeans'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = [("Data", SeqContainer, self.setData)]
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

    def setData(self,slot):
	self.slot = slot
        if self.slot is None or self.fname is None:
            return
        pynopticon.saveSlots(self.fname, outputSlot=slot)

def main():
    a=QApplication(sys.argv)
    ows=OWKmeans()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
    
if __name__ == "__main__":
    main()
    
