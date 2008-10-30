#ifndef __MPI_KMEANS_MEX_H__
#define __MPI_KMEANS_MEX_H__

/* use the input type variable to generate code for integer input or double */
#define INPUT_TYPE 0

#ifdef INPUT_TYPE
#if INPUT_TYPE==0
#define PREC double
#endif
#if INPUT_TYPE==1
#define PREC unsigned int
#endif 
#if INPUT_TYPE==2
#define PREC float
#endif 
#endif

#ifndef BOUND_PREC
#define BOUND_PREC float
//#define BOUND_PREC double
#endif
#ifndef BOUND_PREC_MAX
#define BOUND_PREC_MAX FLT_MAX
//#define BOUND_PREC_MAX DBL_MAX
#endif

#define BOUND_EPS 1e-6

// comment for more speed but no sse output
//#define KMEANS_DEBUG

// if you do not want to have verbose messages printed
// #define KMEANS_VERBOSE

#ifdef KMEANS_DEBUG
unsigned int saved_two=0,saved_three_one=0,saved_three_two=0,saved_three_three=0,saved_three_b=0;
#endif

extern "C"{
double kmeans(double *CXp, const double *X,unsigned int *c,unsigned int dim,unsigned int npts,unsigned int nclus,unsigned int maxiter, unsigned int nr_restarts);
  }
double compute_distance(const double *vec1, const double *vec2, const unsigned int dim);
	unsigned int assign_point_to_cluster_ordinary(const PREC *px, const double *CX, unsigned int dim,unsigned int nclus);
void randperm(unsigned int *order, unsigned int npoints);

#endif


