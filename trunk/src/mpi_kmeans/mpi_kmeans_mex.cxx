#include <memory.h>
#include "mex.h"
#include "mpi_kmeans.h"

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{

	unsigned int	npts, dim, nclus;
	const PREC	*X; 
	double			*CXp, *psse;
	int				i,k;
	double sse;
	unsigned int maxiter;
	unsigned int restarts;
	unsigned int *assignment, *order;
#ifdef COMPILE_WITH_ICC
	unsigned int dims[2];
#else
	mwSize dims[2];
#endif

	if (nrhs < 2){
		mexPrintf("at least two input arguments expected.");
		return;
	}
	maxiter = 0;
	if (nrhs > 2)
		maxiter = (unsigned int) *(mxGetPr(prhs[2]));
	
	restarts = 0;
	if (nrhs > 3)
		restarts = (unsigned int) *(mxGetPr(prhs[3]));

#ifdef KMEANS_VERBOSE
	if (restarts>0)
		printf("will do %d restarts\n",restarts);
#endif

	if ((nlhs > 3) || (nlhs < 1)){
		mexPrintf("minimal one, maximal three output arguments expected.");
		return;
	}

#ifdef INPUT_TYPE
#if INPUT_TYPE==0
	if (!mxIsDouble(prhs[0]) || mxIsComplex(prhs[0]) ||
		mxGetNumberOfDimensions(prhs[0]) != 2)
	{
		mexPrintf("input 1 (X) must be a real double matrix");
		return;
	}
#elif INPUT_TYPE==1
	if (!mxIsClass(prhs[0],"uint32") || mxIsComplex(prhs[0]) ||
		mxGetNumberOfDimensions(prhs[0]) != 2)
	{
		mexPrintf("input 1 (X) must be a uint32 matrix");
		return;
	}
#elif INPUT_TYPE==2
	if (!mxIsSingle(prhs[0]) || mxIsComplex(prhs[0]) ||
		mxGetNumberOfDimensions(prhs[0]) != 2)
	{
		mexPrintf("input 1 (X) must be a real single matrix");
		return;
	}
#endif
#endif

	dim = mxGetM(prhs[0]);
	npts = mxGetN(prhs[0]);

	if (mxGetN(prhs[1])==mxGetM(prhs[1])==1)
		nclus = (unsigned int)*(mxGetPr(prhs[1]));
	else
		nclus = mxGetN(prhs[1]);


	if (!mxIsDouble(prhs[1]) || mxIsComplex(prhs[1]) ||
		mxGetNumberOfDimensions(prhs[1]) != 2)
	{
		mexPrintf("input 2 (CX) must be a real double matrix compatible with input 1 (X)");
		return;
	}

	plhs[0] = mxCreateDoubleMatrix(dim, nclus, mxREAL);
	CXp = mxGetPr(plhs[0]);

	/* input points */
	X = (PREC*)mxGetPr(prhs[0]);

	/* return also the assignment */
	if (nlhs>2) 
	{
		dims[0] = npts;
		dims[1] = 1;
		plhs[2] = mxCreateNumericArray(2,dims,mxUINT32_CLASS,mxREAL);
		assignment = (unsigned int*)mxGetPr(plhs[2]);
	}
	else
		assignment = (unsigned int *) malloc(npts * sizeof(unsigned int)); 	/* assignement of points to cluster */

	assert(assignment);

	if ((mxGetN(prhs[1])==mxGetM(prhs[1]))==1)
	{
		/* select nclus points from data at random... */
		order = (unsigned int*)malloc(npts * sizeof(unsigned int));
		randperm(order,npts);
		for (i=0; i<nclus; i++)
			for (k=0; k<dim; k++ )
				CXp[(i*dim)+k] = (double)X[order[i]*dim+k];
		free(order);
	}
	else
	{
		/* ... or copy initial guess to CXp */
		memcpy(CXp,mxGetPr(prhs[1]),dim*nclus*sizeof(double));
	}

	/* start kmeans */
	sse = kmeans(CXp,X,assignment,dim,npts,nclus,maxiter,restarts);

	if (nlhs>1)
	{
		plhs[1] = mxCreateScalarDouble(0.0);
		psse = mxGetPr(plhs[1]);
		psse[0] = sse;
	}

	/* return also the assignment */
	if (nlhs>2)
	{
		for (i=0; i<npts; i++)
			assignment[i]++;
	}
	else
		free(assignment);
}




