from glob import glob
import os
import os.path
import xml.dom.minidom
from PIL import Image
import pynopticon.slots
import pynopticon


supportedFormats = ['.jpg', '.bmp', '.png', '.gif']
datasetsPath = os.path.join(pynopticon.__path__[0], 'datasets')

#****************************************************************
class ImageBase(object):
    """Base class with all the functional"""
#****************************************************************
    #=================
    def loadOneImage(self, fname, flatten=False, resize=False):
        """Loads the image with filename 'fname' and returns the PIL.Image object"""
    #=================
        try:
            if pynopticon.verbosity > 0:
                print("Loading: %s" % self.absFName(fname))
            im=Image.open(self.absFName(fname))
            if resize: # Resize to fixed size (obsolete)
                im = im.resize((160, 160), Image.ANTIALIAS)
            if flatten: # Convert to gray
                im = im.convert('L')
        except IOError:
            raise IOError, 'Could not read %s!' % fname
        return (im)


    #==============
    def randperm(self,(seq)):
        """Randomly permutes the sequences in the seq tuple with 
        every sequence permuted in the same order"""
    #==============
        from numpy.random import permutation
        perm = permutation(len(seq[0]))
        return [list(numpy.array(s)[perm]) for s in seq]

    #==============
    def split(self, (lst), ratio=.5): #=round(imgs/2)):
        """Split the input list and return two lists with the given ratio""" 
    #==============
        length=int(round(len(lst)*ratio))
        return (lst[0:length], lst[length:len(lst)])

    #=============
    def absFName(self, fname):
        """Changes a relative path to an absolute path
        (assumes the pynopticon/datasets directory to be the base path)"""
    #============
        if fname[0] == '.': #relative path given
            return os.path.join(datasetsPath, fname)
        else:
            return fname


#****************************************
class ImageDataset(ImageBase):
    """Class to create, edit and store an image dataset. One dataset can
    consist of multiple categories (seperate objects).

    Important: Before you can access the images in the dataset, you
    have to call prepare()."""
#****************************************
#==================================
    def __init__(self, categories=None, splitRatio=None, doPermutate=False):
#==================================
        super(ImageDataset, self).__init__()
        if not categories:
            categories = []
        self.categories = categories

        self.allFNames = None # Filled by prepare()
        self.allLabels = None # Filled by prepare()
        self.allNamesTrain = None
        self.allNamesTest = None
        self.allLabelsTrain = None
        self.allLabelsTest = None
        self.categoryNames = None    # Contains the category names

        self.outType = pynopticon.slots.ImageType(format='PIL', color_space='RGB')
	self.outTypeLabels = pynopticon.slots.VectorType(format='flatlist', name='labels')
	
        self.outputSlotTrain = pynopticon.slots.OutputSlot(name="ImagesTrain", outputType=self.outType)
        self.outputSlotTest = pynopticon.slots.OutputSlot(name="ImagesTest", outputType=self.outType)
        self.outputSlotLabelsTrain = pynopticon.slots.OutputSlot(name="LabelsTrain", sequence=self.allLabelsTrain,
							   outputType=self.outTypeLabels)
        self.outputSlotLabelsTest = pynopticon.slots.OutputSlot(name="LabelsTest", sequence=self.allLabelsTest,
							  outputType=self.outTypeLabels)
        
        self.outputSlots = pynopticon.slots.Slots(slots = [self.outputSlotTrain, self.outputSlotTest,
                                                        self.outputSlotLabelsTrain, self.outputSlotLabelsTest])

    def __iter__(self):
        return iter(self.outputSlot)
    
#==================================
    def prepare(self, doPermutate=False, doSplit=False, splitRatio = .5, useLazyEvaluation=pynopticon.useLazyEvaluation):
        """Once all files are added to the dataset this function has to get called
        to create a list of all images of all categories, this list is then
        permutated and split into a training and validation set (according to
        splitRatio and doPermutate."""
#==================================
        # Create list with all filenames and their class IDs
        self.allFNames = []
        self.allLabels = []
        self.categoryNames = []
        
        for category in self.categories:
            self.categoryNames.append(str(category.name))
            for fname in category:
                self.allFNames.append(self.absFName(fname))
                self.allLabels.append(str(category.name))

        # Permutate them
        if doPermutate:
            (self.allFNames, self.allLabels) = self.randperm((self.allFNames, self.allLabels))
            
        # Split them into training and validation set
        if doSplit:
            (self.allNamesTrain, self.allNamesTest) = self.split(self.allFNames, splitRatio)
            (self.allLabelsTrain, self.allLabelsTest) = self.split(self.allLabels, splitRatio)
        else:
            self.allNamesTrain = self.allFNames
            self.allLabelsTrain = self.allLabels
            
        # Prepare the output container by giving it the generator function
        # self.iterator() which yields the images element wise.
        self.outputSlotTrain.__init__(name="ImagesTrain",
                                      outputType = self.outType,
                                      iterator = self.iterTrain,
                                      useLazyEvaluation=useLazyEvaluation,
				      useCaching = False)

        self.outputSlotLabelsTrain.__init__(name="LabelsTrain",
                                            sequence=self.allLabelsTrain,
                                            classes=self.categoryNames,
					    outputType=self.outTypeLabels,
                                            useLazyEvaluation=useLazyEvaluation)
        
        if doSplit:
            self.outputSlotTest.__init__(name="ImagesTest",
                                         outputType = self.outType,
                                         iterator = self.iterTest,
                                         useLazyEvaluation=useLazyEvaluation,
					 useCaching = False)
            self.outputSlotLabelsTrain.__init__(name="LabelsTest",
                                                sequence=self.allLabelsTest,
                                                classes=self.categoryNames,
						outputType=self.outTypeLabels,
                                                useLazyEvaluation=useLazyEvaluation)


#===================================
    def iterTrain(self):
        """Generator function that yields one PIL image 
        (can be either self.all{Names,IDs}Train oder self.all{Names,IDs}Valid)"""
#===================================
        # Yield the images element wise
        for img in self.allNamesTrain:
            yield self.loadOneImage(img)

#===================================
    def iterTest(self):
        """Generator function that yields one PIL image 
        (can be either self.all{Names,IDs}Train oder self.all{Names,IDs}Valid)"""
#===================================
        # Yield the images element wise
        for img in self.allNamesTest:
            yield self.loadOneImage(img)
            
#==================================
    def loadFromXML(self, filename, verbose=False):
#==================================
        """Load a dataset in xml format from filename and return it"""
        dom = xml.dom.minidom.parse(filename)
        def getText(nodelist):
            rc = ""
            for node in nodelist:
                if node.nodeType == node.TEXT_NODE:
                    rc = rc + node.data
            return rc

        def handleImgDatasets(xmlImgDatasets):
            if verbose: print "<imgdataset>"
            imgDatasets = xmlImgDatasets.getElementsByTagName("category")
            for imgDataset in imgDatasets:
                categoryname = handleTitle(imgDataset.getElementsByTagName("title")[0])
                fnames = handleFilenames(imgDataset.getElementsByTagName("filename"))
                # Create the category and append it to the dataset
                self.addCategory(name=categoryname,fnames=fnames)
            if verbose: print "</imgdataset>"


        def handleTitle(title):
            if verbose: print "<title>%s</title>" % getText(title.childNodes)
            return getText(title.childNodes)

        def handleFilenames(xmlFilenames):
            filenames = []
            for filename in xmlFilenames:
                filenames.append(getText(filename.childNodes))
                if verbose: print "<filename>%s</filename>" % getText(filename.childNodes)
            
            return filenames

        handleImgDatasets(dom)

#==================================
    def saveToXML(self, fnameToSave, URL=None, info=None):
#==================================
        """Save datasets to fnameToSave in a specific xml format.
        Datasets can later be loaded by calling loadFromXML(filename)."""
        xmldoc = xml.dom.minidom.getDOMImplementation()
        newdoc = xmldoc.createDocument(None, "imgdataset", None)
        # Add URL
        if not URL:
            URL = ""
        urldoc = newdoc.createElement("URL")
        urltext = newdoc.createTextNode(URL)
        urldoc.appendChild(urltext)
        newdoc.childNodes[0].appendChild(urldoc)

        # Add info
        if not info:
            info = ""
        infodoc = newdoc.createElement("info")
        infotext = newdoc.createTextNode(info)
        infodoc.appendChild(infotext)
        newdoc.childNodes[0].appendChild(infodoc)
        

        for category in self.categories:
            imgdataset = newdoc.createElement("category")
        
            title = newdoc.createElement("title")
            titletext = newdoc.createTextNode(category.name)
            title.appendChild(titletext)
            imgdataset.appendChild(title)
            
            for fname in category.fnames:
                filename = newdoc.createElement("filename")
                filenametext = newdoc.createTextNode(fname)
                filename.appendChild(filenametext)
                imgdataset.appendChild(filename)

            newdoc.childNodes[0].appendChild(imgdataset)

        try:
            fdToSave = open(fnameToSave, 'w')
            newdoc.writexml(fdToSave)
        finally:
            del fdToSave

#==================================
    def addCategory(self, name=None, fnames=None):
        """Add a new category object to the dataset.

        Returns the added category for convenience."""
#==================================
        if not name:
            name = ""
        if not fnames:
            fnames = []
        self.categories.append(ImageCategory(name=name, fnames=fnames))
        # Return added element
        return self.categories[-1]

#==================================
    def delCategory(self, pos):
        """Delete the category at pos from the dataset"""
#==================================
        del self.categories[pos]

#=================================
    def addAutomatic(self, path):
        """Try to automatically generate a new dataset by treating the
        directory names found in path as categories and the filnames
        in it as the images belonging to that category."""
#================================
        path = os.path.abspath(path)
        for counter, (catPath, catN, catFiles) in enumerate(os.walk(path)):
            if counter == 0: # first iteration is the base dir, we want subdirs
                continue
            self.addCategory(name=os.path.split(catPath)[1], fnames = [os.path.join(catPath, fname) for fname in catFiles])
        


#************************************************************
class ImageCategory(ImageBase):
    """Class for creating and modifying an image category.
    A list of elements of this class are in ImageDataset.
    """
#************************************************************
#==================================
    def __init__(self, name="", fnames=None):
#==================================
        super(ImageCategory, self).__init__()

        self.fnames = []
        
        if fnames is not None:
            self.addFiles(fnames)
        self.name = name      # Name of the category

    def __call__(self):
        return self.name

    def __iter__(self):
        return iter(self.fnames)

#==================================
    def addFile(self, absFileName):
        """Add the single file absFileName (with path) to the category
        files in pynopticon/datasets are changed to being relative."""
#==================================
        # Replace the path with "." if the files reside pynopticon/datasets
        # (makes creating datasets for other people usage easier
        absFileName = str(absFileName)
        if os.path.splitext(str(absFileName))[1] not in supportedFormats:
            if pynopticon.verbosity>0:
                print "Excluding %s" % absFileName
            return
        (completePath, fname) = os.path.split(str(absFileName))
        (subPath, category) = os.path.split(completePath)
        (base, dataset) = os.path.split(subPath)
        if base == datasetsPath:
            absFileName = os.path.join(".", dataset, category, fname)
        self.fnames.append(absFileName)

#==================================
    def addFiles(self, absFileNames):
        """Adds a list of file names to the category."""
#==================================
        for absFileName in absFileNames:
            self.addFile(absFileName)

#==================================
    def addDir(self, dirName):
        """Adds _all_ files found in dirName to the category."""
#==================================
        absFileNames = glob(os.path.join(str(dirName), "*.*"))
        self.addFiles(absFileNames)

#==================================
    def delFile(self, fnameToDel):
        """Delete an item from the category list with name fnameToDel."""
#==================================
        for i,fname in enumerate(self.fnames):
            if fname == fnameToDel:
                del self.fnames[i]
                break # Found the element.

#==================================
    def delID(self, idToDel):
        """Delete an item from the file list at position idToDel."""
#==================================
        del self.fnames[idToDel]
