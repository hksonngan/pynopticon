import mpi_kmeans
import numpy
import numpy.random
import pynopticon.slots
import pynopticon
from ctypes import c_double
from scipy import cluster

class Kmeans(object):
    """Class to perform kmeans clustering on input data (e.g. descriptors).
    Returns a codebook.
    For performance reasons we use the kmeans implementation of Peter Gehler
    (pgehler@tuebingen.mpg.de, URL: http://mloss.org/software/view/48/)

    Default is lazy, so the clustering will only be performed when the codebook
    gets accessed."""
    def __init__(self, numClusters, maxiter=0, numruns=20, sampleFromData=1., useLazyEvaluation=pynopticon.useLazyEvaluation):
        """ numClusters: Number of clusters centroids
            maxiter: How many iterations to run maximally
            numruns: How often to start the algorithm
            sampleFromData: How much of the input data to use -- often it is not necessary to use all the data
            """
        self.numClusters = numClusters
        self.maxiter = maxiter
        self.numruns = numruns
        self.sampleFromData = sampleFromData
	self.useLazyEvaluation = useLazyEvaluation
	
	# Define some types
	inputType = pynopticon.slots.VectorType(shape=['flatarray'])
	outputType = pynopticon.slots.VectorType(name='codebook', shape='flatarray')

	self.inputSlot = pynopticon.slots.InputSlot(name='vectors', acceptsType = inputType, bulk=True, useLazyEvaluation=useLazyEvaluation)
	
	self.outputSlot = pynopticon.slots.OutputSlot(name='codebook',
						inputSlot = self.inputSlot,
						slotType = 'bulk',
						processFunc = pynopticon.weakmethod(self, 'process'),
						outputType = outputType,
						useLazyEvaluation= self.useLazyEvaluation)
	
    def process(self, data):
	# Perform KMeans clustering
	if pynopticon.verbosity > 0:
	    print "Performing kmeans clustering with k=%i..." % self.numClusters

        # Sample from data, randomly take self.sampleFromData percent of the vectors
        samplePoints = numpy.random.permutation(range(len(data)))[0:int(round(len(data)*self.sampleFromData))]
        data = numpy.array(data, dtype=c_double)
        data = data[samplePoints,:]

        
	self.codebook, self.dist, self.labels = mpi_kmeans.kmeans(numpy.array(data, dtype=c_double), self.numClusters, self.maxiter, self.numruns)

	return self.codebook



class Quantize(object):
    def __init__(self, useLazyEvaluation=pynopticon.useLazyEvaluation):

        self.useLazyEvaluation = useLazyEvaluation

        # Define types
        inputTypeVec = pynopticon.slots.VectorType(shape=['nestedlist', 'nestedarray'])
        inputTypeCodebook = pynopticon.slots.VectorType(name=['codebook'], shape=['flatarray'])
        
        outputType = pynopticon.slots.VectorType(shape='flatarray')

        # Define slots
        self.inputSlotVec = pynopticon.slots.InputSlot(name='vectors',
                                                  acceptsType=inputTypeVec)

        self.inputSlotCodebook = pynopticon.slots.InputSlot(name='codebook',
                                                       acceptsType=inputTypeCodebook)
        
        self.outputSlot = pynopticon.slots.OutputSlot(name='cluster',
                                                 outputType=outputType,
                                                 iterator=pynopticon.weakmethod(self, 'quantize'),
                                                 useLazyEvaluation=self.useLazyEvaluation)

    def quantize(self):
        # Get data from codebook slot

        codebook = numpy.array(list(self.inputSlotCodebook))

        # Sequentiall get data from vector slot
        for features in self.inputSlotVec:
            if pynopticon.verbosity > 0:
                print ("Quantizing... Codebook shape: %i,%i Vector Shape: %i,%i " % (codebook.shape[0], codebook.shape[1], \
                                                                                     len(features), len(features[0])))
            clusters = cluster.vq.vq(features, codebook)[0]
            yield clusters
