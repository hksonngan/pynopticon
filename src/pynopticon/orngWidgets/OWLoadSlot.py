"""
<name>LoadSlot</name>
<description>Save a slot to a file.</description>
<icon>icons/ExtendedFile.png</icon>
<contact>Thomas Wiecki thomas.wiecki(@at@)gmail.com)</contact>
<priority>2</priority>
"""
from OWWidget import *
import OWGUI
from exceptions import Exception
import pynopticon
from pynopticon.slots import SeqContainer

class OWLoadSlot(OWWidget):
    settingsList = []

    def __init__(self, parent=None, signalManager = None, name='Loader'):
        OWWidget.__init__(self, parent, signalManager, name, wantMainArea = 0)

        self.callbackDeposit = []

        self.inputs = []
        self.outputs = [("Data", SeqContainer)]

        self.useLazyEvaluation = pynopticon.useLazyEvaluation
        
        # Settings
        self.name = name
        self.loadSettings()

	self.fname = None
        self.slot = None
	
        #OWGUI.separator(self.controlArea)
        
        OWGUI.button(self.controlArea, self, "Load from...", callback = self.browseFile, disabled=0)

        self.resize(50,150)

    def browseFile(self, filters=None):
        """Display a FileDialog and select an existing file, 
        or a dir (dir=1) or a new file (save=1).
        filters can be a list with all extensions to be displayed during browsing
        Returned is/are the selected item(s) with complete path."""
        if not filters:
            filters = ["All (*.*)"]

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)

        dialog.setFilters(QStringList(filters))
        dialog.setViewMode(QFileDialog.List)

        if not dialog.exec_():
            return None

        selected = dialog.selectedFiles()

        fname = str(selected[0])
	print fname
	slot = pynopticon.loadSlots(fname)
	self.send("Data", slot)

def main():
    a=QApplication(sys.argv)
    ows=OWKmeans()
    ows.activateLoadedSettings()
    ows.show()
    sys.exit(a.exec_())
    ows.saveSettings()
    
if __name__ == "__main__":
    main()
    
