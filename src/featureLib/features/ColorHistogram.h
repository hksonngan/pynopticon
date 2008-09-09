/* Color histogram features.
 *
 * Copyright (C) 2008 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#ifndef FEATURES_COLORHISTOGRAM_H
#define FEATURES_COLORHISTOGRAM_H

#include <vector>
#include <string>
#include <gmm/gmm.h>
#include <vigra/rgbvalue.hxx>
#include <vigra/functortraits.hxx>

#include "DenseFeature.h"
#include "IntegralImage.h"

namespace Features {

/* Transform an RGB image into a given colorspace (CIE LAB, Luv) and
 * discretize the colorcube into a fixed number of bins.  For each subwindow
 * in the image, all interior pixels are binned into a histogram.  The
 * descriptor is the L1-normalized histogram.
 */
class ColorHistogram : public DenseFeature {
public:
	/* Color histogram constructor,
	 * The colorspace string is one of "lab", "luv" or "rgb".
	 *
	 * CIE LAB: (from Wikipedia) "Uniform changes of components in the L*a*b*
	 * color model aim to correspond to uniform changes in perceived color. So
	 * the relative perceptual differences between any two colors in L*a*b*
	 * can be approximated by treating each color as a point in a three
	 * dimensional space (with three components: L*, a*, b*) and taking the
	 * Euclidean distance between them."
	 *
	 * bins_per_dim: The number of discrete bins per dimension.  The final
	 * histogram/descriptor will be bins_per_dim^3.
	 *
	 * The alternative constructor allows separate binning for each dimension.
	 * This is useful for colorspaces such as CIE LAB, where color and
	 * luminosity is along different axes.  If the colorspace separates
	 * luminosity from color, then luminosity is stored in dimension 1.
	 */
	ColorHistogram(const std::string& colorspace, unsigned int bins_per_dim = 5);
	ColorHistogram(const std::string& colorspace, unsigned int bins_dim1,
		unsigned int bins_dim2, unsigned int bins_dim3);

	/* DenseFeature interface
	 */
	virtual void InitializeImage(const vigra::FVector3Image& image);
	virtual int MemoryBound(const vigra::FVector3Image& image) const;
	virtual int DescriptorSizeFromPixels(int pixel_width, int pixel_height) const;
	virtual int SuggestedPixelShift() const;

	/* The computation is linear in the number of pixels used.
	 * The descriptor is a histogram of a discretized colorspace cube, where
	 * the 1-norm of the histogram is normalized to one.
	 */
	virtual void ExtractDescriptor(const vigra::FVector3Image& image,
		int x, int y, int pixel_width, int pixel_height,
		std::vector<double>& desc, unsigned int desc_base_index = 0) const;

private:
	std::string colorspace;
	std::vector<unsigned int> bins_per_dim;

	// bin_map(y, x) is the histogram bin the (x,y) pixel belongs to.
	gmm::dense_matrix<unsigned int> bin_map;

	void NormalizePlanes(vigra::FVector3Image& cspace,
		double dim1_add, double dim2_add, double dim3_add,
		double dim1_div, double dim2_div, double dim3_div) const;

	void CheckImage(const vigra::FVector3Image& image) const;
};

}

#endif

