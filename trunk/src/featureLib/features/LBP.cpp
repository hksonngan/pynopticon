/* Local Binary Patterns (LBP), following Ojala et al.
 *
 * Copyright (C) 2007 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#include <map>

#include <math.h>
#include <assert.h>

#include <vigra/stdimage.hxx>
#include <vigra/convolution.hxx>
#include <vigra/impex.hxx>
#include <vigra/rgbvalue.hxx>
#include <vigra/splineimageview.hxx>

#include <gmm/gmm.h>

#include "LBP.h"

namespace Features {

LocalBinaryPattern::LocalBinaryPattern(unsigned int P, double R)
	: P(P), R(R), lbp_count(0) {
	assert(P > 0 && P < 31);
}

void LocalBinaryPattern::InitializeImage(const vigra::FVector3Image& image) {
	// Continuous quadratic-interpolated version of the image to allow
	// continuous coordinate access
	vigra::SplineImageView<2, double> image_cont(
		image.upperLeft(), image.lowerRight(),
		VectorMeanAccessor<vigra::FVector3Image::Accessor>());

	// Reset LBP field
	gmm::resize(image_lbp, image.height(), image.width());
	gmm::clear(image_lbp);

	// Fill all uniform patterns, all positions.
	std::map<unsigned int, unsigned int> lbp_trans;
	std::map<unsigned int, unsigned int> lbp_trans_uniq;
	for (unsigned int p = 0; p < (1u << P); ++p) {
		if (IsUniformPattern(p) == false)
			continue;

		unsigned int rot_invariant = RotationMinimal(p);
		lbp_trans[p] = rot_invariant;
		lbp_trans_uniq[rot_invariant] = 1;
	}
	// Assign unique indices to all rotation invariant patterns.  All other
	// patterns are assigned an LBP code of zero.
	lbp_count = 1;
	for (std::map<unsigned int, unsigned int>::iterator li =
		lbp_trans_uniq.begin(); li != lbp_trans_uniq.end(); ++li) {
		li->second = lbp_count;
		lbp_count += 1;
	}
	// Update translation map
	for (std::map<unsigned int, unsigned int>::iterator li =
		lbp_trans.begin(); li != lbp_trans.end(); ++li) {
		li->second = lbp_trans_uniq[li->second];
	}
#ifdef DEBUG
	std::cout << lbp_count << " unique uniform LBP codes ("
		<< "P = " << P << ", R = " << R << ")" << std::endl;
#endif

	// Compute the dense LBP map
	for (int y = 0; y < image.height(); ++y) {
		for (int x = 0; x < image.width(); ++x) {
			double center = image_cont(x, y);
			unsigned int lbp = 0;
			for (unsigned int p = 0; p < P; ++p) {
				double rx = static_cast<double>(x) - R * sin(2.0 * M_PI *
					(static_cast<double>(p) / static_cast<double>(P)));
				double ry = static_cast<double>(y) + R * cos(2.0 * M_PI *
					(static_cast<double>(p) / static_cast<double>(P)));

				// Boundary conditions: pixels outside of the image plane are
				// extrapolated by libvigra.
				double lval = image_cont(rx, ry);
				lbp = (lbp << 1) | (lval >= center ? 1 : 0);
			}
			lbp = IsUniformPattern(lbp) ? lbp_trans[lbp] : 0;
			image_lbp(y, x) = lbp;
		}
	}
}

int LocalBinaryPattern::MemoryBound(const vigra::FVector3Image& image) const {
	return (image.width() * image.height() * sizeof(unsigned int));
}

int LocalBinaryPattern::DescriptorSizeFromPixels(int pixel_width,
	int pixel_height) const {
	assert(lbp_count > 0);	// initialized?
	return (lbp_count);
}

int LocalBinaryPattern::SuggestedPixelShift() const {
	// LBP's are evaluated at every pixel
	return (1);
}

void LocalBinaryPattern::ExtractDescriptor(const vigra::FVector3Image& image,
	int x, int y, int pixel_width, int pixel_height,
	std::vector<double>& desc, unsigned int desc_base_index) const {
	assert(desc.size() >= (static_cast<unsigned int>(
		DescriptorSizeFromPixels(pixel_width, pixel_height)) + desc_base_index));
	std::fill(desc.begin() + desc_base_index, desc.begin()
		+ desc_base_index + DescriptorSizeFromPixels(pixel_width, pixel_height),
		0);
	for (int py = 0; py < pixel_height; ++py)
		for (int px = 0; px < pixel_width; ++px)
			desc[desc_base_index + image_lbp(y + py, x + px)] += 1.0;

	// L_1 normalization
	gmm::scale(gmm::sub_vector(desc, gmm::sub_interval(desc_base_index,
		DescriptorSizeFromPixels(pixel_width, pixel_height))),
		1.0 / static_cast<double>(pixel_height * pixel_width));

#ifdef DEBUG
	for (unsigned int n = 0;
		n < DescriptorSizeFromPixels(pixel_width, pixel_height); ++n)
		std::cout << "lbp[" << n << "]  " << desc[desc_base_index + n] << std::endl;
	std::cout << std::endl;
#endif
}

bool LocalBinaryPattern::IsUniformPattern(unsigned int lbp) const {
	int count = 0;
	int last_bit = (lbp >> (P - 1)) & 1;
	for (int k = P - 1; k >= 0; --k) {
		if (lbp & 1 != last_bit) {
			count += 1;
			if (count == 3)
				return (false);
		}
		lbp = lbp >> 1;
	}
	return (true);
}

unsigned int LocalBinaryPattern::RotationMinimal(unsigned int lbp) const {
	unsigned int lbp_min = lbp;
	for (unsigned int p = 1; p < P; ++p) {
		lbp = (lbp >> 1) | ((lbp & 1) << (P - 1));
		if (lbp < lbp_min)
			lbp_min = lbp;
	}
	return (lbp_min);
}

}

