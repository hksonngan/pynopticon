from numpy import array,median,std,mean,log,concatenate,sum,reshape,sqrt,dot,exp,histogram,float,empty,unique
from ctypes import c_double
import pynopticon
import pynopticon.slots
from mpi_kmeans import kmeans as mpi_kmeans

class PairwiseDistances(object):
    mertics = ['euclidean', 'cityblock', 'sqeuclidean', 'cosine', 'correlation', 'hamming', 'jaccard',
               'chebyshev', 'canberra', 'braycurtis', 'mahalanobis', 'yule', 'dice', 'kulsinski',
               'russellrao', 'sokalmichener', 'sokalsneath']
    def __init__(self, metric = 'euclidean', plot=True, useLazyEvaluation=pynopticon.useLazyEvaluation):

        self.metric = metric
        self.plot = plot
        
        self.inputTypeData = pynopticon.slots.VectorType(shape=['flatarray'])
        self.outputType = pynopticon.slots.VectorType(shape='flatarray')

        self.inputSlot = pynopticon.slots.InputSlot(name='data',
                                               acceptsType=self.inputTypeData,
                                               bulk=True)


        self.outputSlot = pynopticon.slots.OutputSlot(name='distance matrix',
                                                 outputType=self.outputType,
                                                 useLazyEvaluation=useLazyEvaluation,
                                                 slotType = 'bulk',
                                                 inputSlot=self.inputSlot,
                                                 processFunc = pynopticon.weakmethod(self, 'pdist'))

    def pdist(self, X):
        import hcluster
        import pylab

        Y = hcluster.squareform(hcluster.pdist(array(X), metric=self.metric))

        if self.plot:
            pylab.imshow(Y)
            pylab.show()
            
        yield Y
        

class Score(object):
    def __init__(self, scoretype='clustering', useLazyEvaluation=pynopticon.useLazyEvaluation):
        self.scoretype = scoretype
        if self.scoretype not in ['clustering']:
            raise NotImplementedError, "No such score type"


        self.inputTypeData = pynopticon.slots.VectorType(shape=['flatarray'], bulk=True)
        self.inputTypeLabels = pynopticon.slots.VectorType(name=['labels'], shape=['flatlist'])
        
        self.outputType = pynopticon.slots.VectorType(shape='flatarray')

        self.inputSlotData = pynopticon.slots.InputSlot(name='untransformed',
                                                  acceptsType=self.inputTypeData)

        self.inputSlotLabels = pynopticon.slots.InputSlot(name='labels',
                                                    acceptsType=self.inputTypeLabels)

        self.outputSlot = pynopticon.slots.OutputSlot(name='transformed',
                                                outputType=self.outputType,
                                                useLazyEvaluation=useLazyEvaluation,
                                                iterator=pynopticon.weakmethod(self, 'iterator'))

    def iterator(self):
        # Pool data
        data = array(list(self.inputSlotData), dtype=c_double)
        labels = array(list(self.inputSlotLabels))


        # Transform labels to integers
        labelsint = empty(labels.shape, dtype=int)
        classes = self.inputSlotLabels.senderSlot().container.classes
        for i,classname in enumerate(classes):
            labelsint[labels==classname] = i
            
        if pynopticon.verbosity>0:
            print "Scoring: %s..." % self.scoretype

        score = score_one_clustering(data, labelsint, len(classes), 20)

        yield score


# The following code was kindly provided by Christoph Lampert
# (christoph.lampert@tuebingen.mpg.de) and comes under the
# Apache-License



def chl_entropy(y, base=2):
    """Calculate entropy of a discrete distribution/histogram"""
    p,bins = histogram(y, bins=unique(y))  # don't use 'Normed' feature, since that includes the bin-width!
    p = p[p!=0]/float(len(y))
    S = -1.0*sum(p*log(p))/log(base)
    return S


def condentropy(truelabels, labels):
    """Calculate conditional entropy of one label distribution given 
    another label distribution"""
    labels=array(labels)
    truelabels=array(truelabels)
    
    condent=0.
    for l in xrange(min(labels),max(labels)+1):
        sublabels = truelabels[ labels==l ]
        condent += len(sublabels)*chl_entropy( sublabels )
    return condent/float(len(labels))

def score_one_clustering(X, truelabels, num_components, num_iterations):
    """Cluster a dataset and evaluate it using Conditional Entropy"""
    #scipy's builtin K-means is very slow, use mpi-version instead.
    #from scipy.cluster.vq import kmeans,vq
    #clst,dist =  kmeans(X, num_components, NUM_ITERATIONS)
    #labels,dist =  vq(X, clst)
    clst,dist,labels = mpi_kmeans(X, num_components, 200, num_iterations)
    print truelabels
    print labels-1
    return condentropy(truelabels,labels-1)


# def score_one_mixture(X):
#     """Estimate a Gaussian mixture model from a dataset and evaluate it using 
#        Conditional Entropy
#        This version uses scipy.pyem, but seems fail from time to time."""

#     from scipy.sandbox.pyem import GM, GMM, EM
#     X = X/numpy.mean(X) # isotropic normalization to avoid unstable Gaussians
#     lgm = GM(X.shape[1], num_components, 'diag')
#     gmm = GMM(lgm, 'kmean') # initialize by kmeans
#     gmm.init_kmean(X)
#     em = EM()
#     like =em.train(X, gmm, maxiter=10, thresh=1e-6)
#     try:
#        posterior,dummy = gmm.sufficient_statistics(X)
#     except AttributeError: # upcoming API change
#        posterior,dummy = gmm.compute_responsabilities(X)
#     labels = pylab.argmax(posterior,axis=1)
#     return condentropy(truelabels,labels+1)
