/* Integral image computation.
 *
 * Copyright (C) 2008 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#include <assert.h>

#include "IntegralImage.h"

namespace Features {

IntegralImage::IntegralImage(const gmm::dense_matrix<double>& input)
	: integral(gmm::mat_nrows(input), gmm::mat_ncols(input)) {
	IntegralImageComputation::integral_image_compute(input,
		integral, 0, 0, gmm::mat_nrows(input), gmm::mat_ncols(input));
}

IntegralImage::IntegralImage(const gmm::dense_matrix<double>& input_f1,
	const gmm::dense_matrix<double>& input_f2)
	: integral(gmm::mat_nrows(input_f1), gmm::mat_ncols(input_f2)) {
	assert(gmm::mat_nrows(input_f1) == gmm::mat_nrows(input_f2));
	assert(gmm::mat_ncols(input_f1) == gmm::mat_ncols(input_f2));

	// Explicitly compute product map.  It would be better to delay this using
	// boost::lambda.
	gmm::dense_matrix<double> input_product(gmm::mat_nrows(input_f1),
		gmm::mat_ncols(input_f1));
	for (unsigned int r = 0; r < gmm::mat_nrows(input_f1); ++r)
		for (unsigned int c = 0; c < gmm::mat_ncols(input_f1); ++c)
			input_product(r, c) = input_f1(r, c) * input_f2(r, c);

	IntegralImageComputation::integral_image_compute(input_product,
		integral, 0, 0,
		gmm::mat_nrows(input_product), gmm::mat_ncols(input_product));
}

double IntegralImage::operator()(int r1, int c1, int r2, int c2) const {
	return (IntegralImageComputation::integral_image_box(integral,
		r1, c1, r2, c2));
}

}

