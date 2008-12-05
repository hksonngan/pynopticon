import pynopticon as pnc
import os.path

def examplePipeline():
    ###############################################
    # Create an object for every step of the procedure
    ###############################################
    
    # Create the ImageLoader object
    imgLoader = pnc.ImageDataset.ImageDataset()
    # Load the images (here, we use a predefined dataset from an xml-file)
    imgLoader.loadFromXML("GarfieldBarrel.xml", demos=True)
	# Loading complete - prepare the ImageLoader for further steps
    imgLoader.prepare()
    
    # Create the feature extractor object 
	#(in this case the sift extractor,  using the valedi implementation)
    sift = pnc.features.SiftValedi()

    # Create a k-means-cluster object with 50 clusters 
    kmeans = pnc.cluster.Kmeans(numClusters=50)

    # Create a quantization object
    quant = pnc.cluster.Quantize()

    # Create a histogram object to bin the descriptors into 50 bins (one for every cluster)
    histo = pnc.histogram.Histogram(bins=50)

    ###############################################
    # Connect the objects via slots
    ###############################################
    pnc.connect(imgLoader.outputSlotTrain, sift.inputSlot)
    pnc.connect(sift.outputSlot, kmeans.inputSlot)
    pnc.connect(sift.outputSlot, quant.inputSlotVec)
    pnc.connect(kmeans.outputSlot, quant.inputSlotCodebook)
    pnc.connect(quant.outputSlot, histo.inputSlot)

    ###############################################
    # Get the histograms as a list of numpy arrays
    ###############################################
    histograms = list(histo.outputSlot)

    # train classificator etc....

class exampleSlot(object):
    def __init__(self):
        # For every slot we can define the type of data that is
        # exepected or outputted, for more info have a look at
        # slots.py

        # Input is expected to be images in PIL format
        inputType = pnc.slots.ImageType(format=["PIL"], color_space=["gray"])
        # Output is a flat array (a 2D array consisting of vectors)
	outputType = pnc.slots.VectorType(name='Example', shape='flatarray')

        # Next we have to define an input and an output slot which
        # will handle the data sending and receiving
        self.inputSlot = pnc.slots.InputSlot(name='Images',
                                             acceptsType = inputType)

	# We have several options of defining an output slot (see the
        # help for slots.OutputSlots for more infos).  Here, we create
        # an output slot that receives data from our just defined
        # inputSlot and calls the function self.process() on every
        # element.  The reason we are using pnc.weakmethod(class,
        # method) instead of handing self.process directly is purely
        # technical.
	self.outputSlot = pnc.slots.OutputSlot(name='Example',
                                               inputSlot = self.inputSlot,
                                               processFunc = pnc.weakmethod(self, 'process'),
                                               outputType = outputType)

    def process(self, img):
        descr = do_funky_computations(img)
        return descr
    
if __name__ == "__main__":
    examplePipeline()
