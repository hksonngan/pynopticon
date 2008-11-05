import pynopticon as pnc
import os.path

def example():
    #######################################
    # Create different objects
    #######################################
    
    # Create the ImageLoader object
    imgLoader = pnc.ImageDataset.ImageDataset()
    # Load a predefined dataset from an XML file
    imgLoader.loadFromXML(os.path.join(pnc.__path__[0], "datasets", "GarfieldBarrel.xml"))
    # Since we are finished with out dataset we call prepare()
    imgLoader.prepare()
    
    # Create a feature extractor (in this case the sift extractor using the Valedi implemenatation
    sift = pnc.features.SiftValedi()

    # Create a kmeans-cluster object and set numClusters=50 (50 cluster centroids)
    kmeans = pnc.cluster.Kmeans(numClusters=50)

    # Create a Quantization object
    quant = pnc.cluster.Quantize()

    # Create a Histogram object to bin the descriptors later on using 50 bins
    # (one for every cluster)
    histo = pnc.histogram.Histogram(bins=50)

    #######################################
    # Connect the objects via slots
    #######################################
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

if __name__ == "__main__":
    example()
    

    

    
    
