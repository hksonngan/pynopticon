"""
<name>ImageLoader</name>
<description>Reads in images of all kinds.</description>
<icon>icons/File.png</icon>
<contact>Thomas Wiecki (thomas.wiecki(@at@)gmail.com)</contact>
<priority>1</priority>
"""

#################################################################
#
# The class structure is as follows:
#
# OWImageSubLoader: Basic functionality like opening a file dialog
# OWImageLoader: The main GUI, inherits from OWImageSubLoader
#                and from ImageDataset as it is the logical
#                extension to this class
# ImageCategoryDlg: Edit individual categories, add files, display images
#               Inherits from OWImageSubLoader and from
#               ImageCategories as it is the logical extension of
#               that class



from OWWidget import *
import OWGUI 


import os
import os.path
import pynopticon
from pynopticon.ImageDataset import *
from pynopticon import Images, Labels

class OWImageSubFile(OWWidget):
    """Basic functionality like opening a file dialog"""
    allFileWidgets = []
    
    def __init__(self, parent=None, signalManager = None, name = ""):
        OWWidget.__init__(self, parent, signalManager, name)
        OWImageSubFile.allFileWidgets.append(self)
        self.filename = ""
    
    def destroy(self, destroyWindow, destroySubWindows):
        #OWImageSubFile.allFileWidgets.remove(self)
        OWWidget.destroy(self, destroyWindow, destroySubWindows)

    def activateLoadedSettings(self):
        # remove missing data set names
        self.recentFiles=filter(os.path.exists,self.recentFiles)
        self.setFileList()

        if len(self.recentFiles) > 0 and os.path.exists(self.recentFiles[0]):
            self.openFile(self.recentFiles[0])

        # connecting GUI to code
        self.connect(self.filecombo, SIGNAL('activated(int)'), self.selectFile)


    def browseFile(self, filters=None, inDemos=1, dir=0, save=0):
        """Display a FileDialog and select an existing file, 
        or a dir (dir=1) or a new file (save=1).
        filters can be a list with all extensions to be displayed during browsing
        Returned is/are the selected item(s) with complete path."""
	if not filters:
            filters = ["All (*.*)"]

        dialog = QFileDialog()
        if dir == 0 and save == 0:
            dialog.setFileMode(QFileDialog.ExistingFiles)
        elif dir == 1 and save == 0:
            dialog.setFileMode(QFileDialog.Directory)
        elif dir == 0 and save == 1:
            dialog.setFileMode(QFileDialog.AnyFile)
        else:
            print "Incorrect mode." # TODO, throw an exception here

	if inDemos:
	    import pynopticon
	    path = os.path.join(pynopticon.__path__[0], 'datasets')
	    dialog.setDirectory(path)

        dialog.setFilters(QStringList(filters))
        dialog.setViewMode(QFileDialog.List)

        if not dialog.exec_():
            return None

        selected = dialog.selectedFiles()

        return selected

    def setInfo(self, info):
        for (i, s) in enumerate(info):
            self.info[i].setText(s)

        
#*********************************************************
class OWImageLoader(OWImageSubFile):
    """Dialog to create your own image dataset.
    Basically, this is a frontend to pynopticon.ImageDataset.ImageDataset."""
#*********************************************************
    settingsList=['loadedDataset', 'recentFiles', 'doSplit', 'splitRatio', 'doPermutate']
    
    def __init__(self, parent=None, signalManager = None):
        OWImageSubFile.__init__(self, parent, signalManager, "Image Dataset")
        
        self.imgDataset = pynopticon.ImageDataset.ImageDataset()
        
        self.inputs = []
        self.outputs = [("Images Train", Images), ("Images Test", Images), ("Labels Train", Labels),("Labels Test", Labels)]

        self.useLazyEvaluation = pynopticon.useLazyEvaluation
        
        #set default settings
        self.recentFiles=["(none)"]
        self.domain = None
        #get settings from the ini file, if they exist
        self.doPermutate = False
        self.doSplit = False
        self.splitRatio = .5
        self.loadedDataset = None

        
        self.loadSettings()

        buttonWidth = 1.5

        # Create the GUI
        self.dialogWidth = 250

        box = OWGUI.widgetBox(self.controlArea, 'Categories', addSpace = True, orientation=1)

        self.categoryList = OWGUI.listBox(box, self)
        self.connect(self.categoryList, SIGNAL('itemDoubleClicked(QListWidgetItem *)'), self.editDataset)
        self.connect(self.categoryList, SIGNAL('itemEntered(QListWidgetItem *)'), self.editDataset)
        self.connect(self.categoryList, SIGNAL('itemSelectionChanged()'), self.selectionChanged)

        #self.filecombo = OWGUI.comboBox(box, self, "Categories")
        #self.filecombo.setMinimumWidth(self.dialogWidth)

        self.createNewButton = OWGUI.button(box, self, 'Create new category', callback = self.createNew, disabled=0, width=self.dialogWidth)
        self.removeSelectedButton = OWGUI.button(box, self, 'Remove selected category', callback = self.removeSelected, disabled=1, width=self.dialogWidth)
        self.addExistingButton = OWGUI.button(box, self, 'Add existing dataset', callback = self.addExisting, disabled=0, width=self.dialogWidth)
        self.saveDatasetButton = OWGUI.button(box, self, 'Save dataset', callback = self.saveDataset, disabled=0, width=self.dialogWidth)
        self.autoAddButton = OWGUI.button(box, self, 'Automatically add dataset', callback = self.autoAdd, disabled=0, width=self.dialogWidth) 

        databox = OWGUI.widgetBox(self.controlArea, 'Dataset', addSpace = True, orientation=1)
        self.permutateBox = OWGUI.checkBox(databox, self, "doPermutate", "Randomly permutate the dataset")
        self.splitBox = OWGUI.checkBox(databox, self, "doSplit", "Split dataset into train and test sets")
        OWGUI.spin(databox, self, "splitRatio", 0, 100, 1, None, "Split Ratio  ", orientation="horizontal")
#        self.splitRatio = OWGUI.spin(databox, self, "splitRatio", 0, 1, 0.01, None, "Split ratio", orientation='horizontal')

	
        OWGUI.checkBox(databox, self, "useLazyEvaluation", "Use lazy evaluation")
        self.resize(self.dialogWidth,480)


        # info
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data loaded.')
        self.infob = OWGUI.widgetLabel(box, '')
        self.warnings = OWGUI.widgetLabel(box, '')


        self.adjustSize()

        self.applyButton = OWGUI.button(self.controlArea, self, 'Apply', callback = self.apply, disabled=0, width=self.dialogWidth)

        self.inChange = False

        if self.loadedDataset:
            if pynopticon.verbosity >= 1:
                print "Loading file from last time"
            self.imgDataset.loadFromXML(self.loadedDataset)
            self.updateCategoryList()            

#====================================
    def sendData(self):
        """Prepare the ImageDataset and send it to the receiving widgets"""
#====================================
        if len(self.imgDataset.categories) == 0:
            return
        
#        self.imgDataset.prepare(useLazyEvaluation=self.useLazyEvaluation)
        self.send("Images Train", self.imgDataset.outputSlotTrain)
	self.send("Images Test", self.imgDataset.outputSlotTest)
        self.send("Labels Train", self.imgDataset.outputSlotLabelsTrain)
	self.send("Labels Test", self.imgDataset.outputSlotLabelsTest)
        
#==================================
    def addCategory(self, parent=None, name="", fnames=None, visible=False):
        """Add a new category to ImageDataset and display dialog to add/remove images"""
#==================================
        if not fnames:
            fnames = []
        category = self.imgDataset.addCategory(name=name, fnames=fnames)
        if visible:
            # Create GUI
            ImageCategoryDlg(category, parent=self)

        # Update the widget list because something changed in imgDataset
        self.updateCategoryList()

#===================================
    def autoAdd(self, parent=None):
        """Wrapper for ImageDataset.autoAdd(). Let the user choose from which directory to pool."""
#===================================
        datasetDir = self.browseFile(dir=1)
        self.imgDataset.addAutomatic(str(datasetDir[0]))
        self.updateCategoryList()
        
#==================================
    def editDataset(self, dataset):
        """Creates an edit dialog for the selected category"""
#==================================
        selectedCategory = self.imgDataset.categories[self.categoryList.currentRow()]
        # Create a separate GUI for editing
        ImageCategoryDlg(selectedCategory, parent=self)

#==================================
    def selectionChanged(self):
        """Selection changed so there is a dataset present which _could_ be deleted,
        enable remove button"""
#==================================
        self.removeSelectedButton.setEnabled(1)

#==================================
    def addExisting(self):
        """Wrapper for ImageDataset.loadFromXML().
        Load an existing dataset from an xml file (special format)
        and add it to the dataset list."""
#==================================
        dataset_file = self.browseFile(filters=['Image Dataset (*.xml)','All files (*.*)'])
        if not dataset_file:
            return
        self.imgDataset.loadFromXML(str(dataset_file[0]))
        self.loadedDataset = str(dataset_file[0])
        self.updateCategoryList()
        
#==================================
    def createNew(self):
        """Create a new dataset, a new dialog opens 
        where you can choose which files to include
        and what name the dataset should have"""
#==================================
        self.addCategory(parent = self, visible=True)
        
#==================================
    def removeSelected(self):
        """Remove dataset from the list of datasets"""
#==================================
        currentCategory = self.categoryList.currentRow() 
        self.imgDataset.delCategory(currentCategory)
        self.updateCategoryList()

#==================================
    def saveDataset(self):
        """Open a file dialog to select the filename and save the current datasets to the
        file in xml format"""
#==================================
        saveFile = self.browseFile(filters=['Image Dataset (*.xml)','All files (*.*)'], save=1)
        if not saveFile:
            return
        self.imgDataset.saveToXML(str(saveFile[0]))

#==================================
    def updateCategoryList(self):
        """Called to update the GUI from the imgDataset structure.
        This needs to get called everytime there are changes to the categories
        in self.imgDataset.
        """
#==================================
        # delete all items from the list
        # TODO: check if something changed at all
        self.categoryList.clear()
        for category in self.imgDataset.categories:
            self.categoryList.addItem(str(category.name))

        # Set dataset summary in infobox
        if len(self.imgDataset.categories) != 0:
            self.infoa.setText('%i categories with a total of %i images' % (len(self.imgDataset.categories), sum([len(category.fnames) for category in self.imgDataset.categories])))
            #self.infob.setText()
        else:
            self.infoa.setText("No data loaded")
            
#==================================
    def setFileList(self):
    # set the file combo box
#==================================
        self.filecombo.clear()
        if not self.recentFiles:
            self.filecombo.addItem("(none)")
        for file in self.recentFiles:
            if file == "(none)":
                self.filecombo.addItem("(none)")
            else:
                self.filecombo.addItem(os.path.split(file)[1])
        self.filecombo.addItem("Browse documentation data sets...")
        #self.filecombo.adjustSize() #doesn't work properly :(
        self.filecombo.updateGeometry()

#==================================
    def apply(self):
    # User pressed apply button, hide the dialog (should we close here?)
#==================================
        self.imgDataset.prepare(doPermutate=self.doPermutate,
				doSplit=self.doSplit,
				splitRatio=self.splitRatio,
				useLazyEvaluation=self.useLazyEvaluation)
        self.sendData()
        self.setVisible(0)

#==================================
    def onButtonClick(self):
#==================================
        pass

#==================================
    def openFile(self,fn, throughReload = 0):
#==================================
        self.openFileBase(fn, throughReload=throughReload)


#==================================
    # user selected a file from the combo box
    def selectFile(self,n):
#==================================
        if n < len(self.recentFiles) :
            name = self.recentFiles[n]
            self.recentFiles.remove(name)
            self.recentFiles.insert(0, name)
        elif n:
            self.browseFile(inDemos=1)

        if len(self.recentFiles) > 0:
            self.setFileList()
            self.openFile(self.recentFiles[0])

#***********************************************************************
class ImageCategoryDlg(OWImageSubFile):
    """Dialog to create/edit a single category.
    The user can add single image files or a whole directory and give
    the dataset a name."""
#***********************************************************************
#==================================
    def __init__(self, imgCategory, parent=None, signalManager = None, visible=True):
#==================================
        #get settings from the ini file, if they exist
        #self.loadSettings()
        self.imgCategory = imgCategory
        self.name = self.imgCategory.name
        
        OWImageSubFile.__init__(self, parent, signalManager, "Category "+self.imgCategory.name)

        #set default settings
        self.domain = None
        #GUI
        self.dialogWidth = 250
        buttonWidth = 1.5
        self.recentFiles=["(none)"]
        
        box = OWGUI.widgetBox(self.controlArea, 'Dataset', addSpace = True, orientation=1)
        OWGUI.lineEdit(box, self, "name", "Name of dataset: ", orientation="horizontal", tooltip="The name of the dataset used throughout the training")

        self.widgetFileList = OWGUI.listBox(box, self)
        self.connect(self.widgetFileList, SIGNAL('itemDoubleClicked(QListWidgetItem *)'), self.displayImage)
        self.connect(self.widgetFileList, SIGNAL('itemEntered(QListWidgetItem *)'), self.displayImage)
        self.connect(self.widgetFileList, SIGNAL('itemSelectionChanged()'), self.selectionChanged)
        self.connect(self, SIGNAL('updateParent'), parent.updateCategoryList)
        #OWGUI.connectControl(self.widgetFileList, self, None, self.displayImage, "itemDoubleClicked(*QListWidgetItem)", None, None)

        self.fileButton = OWGUI.button(box, self, 'Add file(s)', callback = self.browseImgFile, disabled=0, width=self.dialogWidth)
        self.dirButton = OWGUI.button(box, self, 'Add directory', callback = self.browseImgDir, disabled=0, width=self.dialogWidth)
        self.removeButton = OWGUI.button(box, self, 'Remove selected file', callback = self.removeFile, disabled=1, width=self.dialogWidth)
        self.applyButton = OWGUI.button(self.controlArea, self, 'OK', callback = self.ok, disabled=0, width=self.dialogWidth)        
        self.inChange = False
        self.resize(self.dialogWidth,300)

        # Add the filenames to the widgetFileList
        self.widgetFileList.addItems(self.imgCategory.fnames)
        if visible:
            self.show()

#==================================
    def displayImage(self, WidgetItem):
#==================================
        img = self.imgCategory.loadOneImage(str(WidgetItem.text()))
        img.show()

#==================================
    def selectionChanged(self):
#==================================
        self.removeButton.setEnabled(1)

#==================================
    def removeFile(self):
#==================================
        row = self.widgetFileList.currentRow()
        self.imgCategory.delID(row)
        self.updateFileList()

#==================================
    def browseImgFile(self):
#==================================
        fileList = self.browseFile(filters=['Image Files (*.jpg *.png *.gif *.bmp)','All files (*.*)'])
        if not fileList:
            return
        self.imgCategory.addFiles([str(file) for file in fileList])
        self.updateFileList()

#==================================
    def browseImgDir(self):
#==================================
        dirName = self.browseFile(dir=1)
        if not dirName:
            return
        self.imgCategory.addDir(str(dirName[0]))
        self.updateFileList()

#==================================
    def apply(self):
#==================================
        self.emit(SIGNAL('updateParent'))
        self.setVisible(0)

#==================================
    def ok(self):
#==================================
        self.imgCategory.name = self.name
        self.emit(SIGNAL('updateParent'))
        self.close()
    
#==================================
    def cancel(self):
#==================================
        self.setVisible(0)

#==================================
    def updateFileList(self):
#==================================
        self.widgetFileList.clear()
        self.widgetFileList.addItems(self.imgCategory.fnames)
        if self.widgetFileList.count() == 0:
            self.removeButton.setDisabled(0)



if __name__ == "__main__":
    a=QApplication(sys.argv)
    owf=OWImageLoader()
    owf.activateLoadedSettings()
    owf.show()
    sys.exit(a.exec_())
    owf.saveSettings()
