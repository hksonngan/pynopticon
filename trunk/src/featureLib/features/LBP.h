/* Local Binary Patterns (LBP), following Ojala et al.
 *
 * Copyright (C) 2007 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#ifndef FEATURES_LBP_H
#define FEATURES_LBP_H

#include <vector>
#include <gmm/gmm.h>
#include <vigra/stdimagefunctions.hxx>

#include "DenseFeature.h"
#include "utility.h"

namespace Features {

/* We use the exact features described in
 *   [Ojala2002], Timo Ojala, Matti Pietikainen, Topi Maenpaa,
 *   "Multiresolution Gray-Scale and Rotation Invariant Texture Classification
 *   with Local Binary Patterns", IEEE PAMI, Vol. 24, No. 7, July 2002.
 *
 * The actual descriptor produced is simply the normalized histogram of
 * uniform LBP codes within the region.  Normalization is L_1.
 */
class LocalBinaryPattern : public DenseFeature {
public:
	/* P: The number of circular surrounding pixels to measure.  The pixels
	 *    are located equiangular around the center pixel.
	 * R: Radius between center pixel and surrounding pixels.  Can be
	 *    fractional, the pixels are measured using a spline-interpolated
	 *    image.
	 */
	LocalBinaryPattern(unsigned int P = 8, double R = 1.0);

	/* Overridden methods from DenseFeature class
	 */
	virtual void InitializeImage(const vigra::FVector3Image& image);
	virtual int MemoryBound(const vigra::FVector3Image& image) const;
	virtual int DescriptorSizeFromPixels(int pixel_width, int pixel_height) const;
	virtual int SuggestedPixelShift() const;
	virtual void ExtractDescriptor(const vigra::FVector3Image& image,
		int x, int y, int pixel_width, int pixel_height,
		std::vector<double>& desc, unsigned int desc_base_index = 0) const;

protected:
	// After InitializeImage, the dense LBP field is stored here.  The field
	// has the same dimensions as the input image.
	gmm::dense_matrix<unsigned int> image_lbp;

private:
	// The number of pixels to measure around the central pixel
	unsigned int P;

	// The radius in pixels between the center pixel and the surrounding
	// pixels.
	double R;

	// Number of total LBP codes in the current code.  This is needed for
	// computing histograms.
	unsigned int lbp_count;

	// Test whether the given LBP code is a "uniform" code.  It is uniform iff
	// there are exactly two transitions from 0-1 and 1-0 in the radial code.
	bool IsUniformPattern(unsigned int lbp) const;

	// Return the rotation invariant LBP corresponding to this one.  This is
	// simply the minimum bit-shifted variant of the given LBP pattern code.
	unsigned int RotationMinimal(unsigned int lbp) const;
};

}

#endif

