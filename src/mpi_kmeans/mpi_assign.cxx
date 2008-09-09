#include "mex.h"
#include <memory.h>
#include "mpi_kmeans.h"

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{

	unsigned int	npts, dim, nclus;
	const double	*X,*px,*CX; 
	int				i;
	unsigned int *c;
#ifdef COMPILE_WITH_ICC
	unsigned int dims[2];
#else
	mwSize dims[2];
#endif

	dim = mxGetM(prhs[0]);
	npts = mxGetN(prhs[0]);
	nclus = mxGetN(prhs[1]);

	dims[0]= npts;
	dims[1] = 1;
	plhs[0] = mxCreateNumericArray(2,dims,mxUINT32_CLASS,mxREAL);
	c = (unsigned int*)mxGetPr(plhs[0]);

	/* input points */
	X = (double*)mxGetPr(prhs[0]);
	/* cluster centers */
	CX = (double*)mxGetPr(prhs[1]);

	for (i=0,px=X; i<npts; i++,px+=dim)
		c[i] = 1+assign_point_to_cluster_ordinary(px, CX, dim, nclus);

}




