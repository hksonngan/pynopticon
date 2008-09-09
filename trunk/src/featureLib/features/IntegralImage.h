/* Integral image computation.
 *
 * Copyright (C) 2008 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#ifndef FEATURES_INTEGRALIMAGE_H
#define FEATURES_INTEGRALIMAGE_H

#include <vector>
#include <algorithm>
#include <assert.h>
#include <gmm/gmm.h>

namespace Features {

class IntegralImage {
public:
	// Instantiate the integral image for a simple scalar feature map
	explicit IntegralImage(const gmm::dense_matrix<double>& input);
	explicit IntegralImage(const gmm::dense_matrix<float>& input);

	// Instantiate the integral image for a per-element product feature map
	// That is, input_f1(r,c)*input_f2(r,c) is treated as scalar feature map.
	IntegralImage(const gmm::dense_matrix<double>& input_f1,
		const gmm::dense_matrix<double>& input_f2);

	// Compute and return the integral in the box given by (r1, c1) inclusive
	// to (r2, c2) inclusive.  By providing (r1, c1), (r2=r1, c2=c1) you
	// can recover the original pixel value at (r1, c1).
	double operator()(int r1, int c1, int r2, int c2) const;

private:
	gmm::dense_matrix<double> integral;
};

// Fast template code for integral images
namespace IntegralImageComputation {

/* Compute an integral image from the input image.  The integral image is
 * only computed for the region (r1,c1) inclusive to (r2,c2) exclusive.
 * INPUTITERATOR must support operator (row,col) readonly,
 * OUTPUTITERATOR must support (row,col) read/write.
 */
template <class INPUTITERATOR, class OUTPUTITERATOR>
void integral_image_compute(INPUTITERATOR const& in,
	OUTPUTITERATOR& out, int r1, int c1, int r2, int c2) {
	assert(r2 >= r1);
	assert(c2 >= c1);
	std::vector<double> rowsum(c2 - c1);	// cummulative row sum
	std::fill(rowsum.begin(), rowsum.end(), 0);

	int rows = r2 - r1;
	int cols = c2 - c1;
	for (int r = 0; r < rows; ++r) {
		for (int c = 0; c < cols; ++c) {
			rowsum[c] += in(r1 + r, c1 + c);
			// out(r,c) contains \sum_{i=0}^r \sum_{j=0}^c in(i,j).
			out(r1 + r, c1 + c) = (c == 0 ? 0.0 : out(r1 + r, c1 + c - 1))
				+ rowsum[c];
		}
	}
}

// Do not use this function, use IntegralImage::operator() instead
template <class INPUTITERATOR>
double integral_image_box(INPUTITERATOR const& in,
	int r1, int c1, int r2, int c2) {
	double val = in(r2, c2);
	if (r1 != 0)
		val -= in(r1 - 1, c2);
	if (c1 != 0)
		val -= in(r2, c1 - 1);
	if (r1 != 0 && c1 != 0)
		val += in(r1 - 1, c1 - 1);
	return (val);
}

}

}

#endif

