#!/usr/bin/python
# Wrapper for the MPI-Kmeans library by Peter Gehler 
from __future__ import division
import numpy as np
# "cimport" is used to import special compile-time information
# about the numpy module (this is stored in a file numpy.pxd which is
# currently part of the Cython distribution).
cimport numpy as np
# We now need to fix a datatype for our arrays. I've used the variable
# DTYPE for this, which is assigned to the usual NumPy runtime
# type info object.
DTYPE = np.double

# "ctypedef" assigns a corresponding compile-time type to DTYPE_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a _t-suffix.
ctypedef np.double_t DTYPE_t

cdef extern from "mpi_kmeans.h":
    double c_kmeans "kmeans" (double *CX, double *X,unsigned int *assignment,unsigned int dim,unsigned int npts,unsigned int nclus,unsigned int maxiter, unsigned int restarts)

from ctypes import c_int, c_double, c_uint
from numpy.ctypeslib import ndpointer
import numpy as N
from numpy import empty,array,reshape,arange
#import mpi_kmeans_py

def kmeans(np.ndarray[DTYPE_t, ndim=2] X, unsigned int nclst, unsigned int maxiter=0, unsigned int numruns=1):
    """Wrapper for Peter Gehlers accelerated MPI-Kmeans routine."""
    cdef unsigned int npts = X.shape[0]
    cdef unsigned int dim = X.shape[1]
    cdef unsigned int nclst_real
    cdef double SSE
    nclst_real = min(nclst, npts)
    
    cdef np.ndarray assignments=np.empty( (npts), dtype=c_uint)
    
    cdef np.ndarray[DTYPE_t, ndim=1] Xvec = array( reshape( X, (-1,) ), order='C')
    permutation = N.random.permutation( range(npts) ) # randomize order of points
    cdef np.ndarray[DTYPE_t, ndim=1] CX = array(X[permutation[:nclst],:], order='C').flatten()
    print "Calling kmeans"
    cdef double * CXdata
    CXdata = <double*> X.data
    
    SSE = c_kmeans( CXdata, <double *> Xvec.data,
		  <unsigned int *> assignments.data, dim, npts,
		  nclst_real, maxiter, numruns)
    print SSE
    return reshape(CX, (nclst,dim)), SSE, (assignments+1)


def test():
    from numpy import array
    from numpy.random import rand
    
    X = array( rand(12), c_double )
    X.shape = (4,3)
    print X
    clst,dist,labels = kmeans(X, 2)
    
    print "cluster centers=\n",clst
    print "dist=",dist
    print "cluster labels",labels
