/* Dense general image feature.
 *
 * This class provides a the general interface to dense image features.
 *
 * Copyright (C) 2007 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#ifndef FEATURES_DENSEFEATURE_H
#define FEATURES_DENSEFEATURE_H

#include <vector>
#include <vigra/stdimagefunctions.hxx>

namespace Features {

/* A dense image feature: it can be evaluated for any subwindow of the image.
 */
class DenseFeature {
public:
	DenseFeature();
	virtual ~DenseFeature();

	/* Initialize a new image for the following sliding window feature
	 * extraction.  This function should contain the most expensive
	 * pre-computations in order to allow fast subwindow descriptor
	 * computation.  When called with a new image, the previous one is
	 * discarded.  The image is given in RGB.
	 */
	virtual void InitializeImage(const vigra::FVector3Image& image);

	/* Provide an upper bound on the amount of memory required to preprocess
	 * the given image.
	 *
	 * Return an upper bound in bytes on permanently used bytes when
	 * InitializeImage is called with the given image.  Temporarily a lot more
	 * memory may be used due to processing in InitializeImage.
	 */
	virtual int MemoryBound(const vigra::FVector3Image& image) const;

	/* The number of descriptor elements (linearized) for a pixel window of
	 * the given dimensions.  Every call to ExtractDescriptor() with the same
	 * pixel_width and pixel_height parameters should exactly obey this size.
	 */
	virtual int DescriptorSizeFromPixels(int pixel_width, int pixel_height) const;

	/* Suggest an intrinsic pixel shift for this feature type.  Even though
	 * the feature is dense and can be evaluated at each pixel, sometimes this
	 * does not make sense as the underlying feature representation is binned.
	 * This suggests the minimal pixel shift upon which the descriptor starts
	 * to change.
	 *
	 * The shift size must not depend on the image but be globally fixed for
	 * this feature type.  Also, if the image is shifted by exactly this shift
	 * size, the user may very well expect exactly the same features at the
	 * shifted locations, except nearby the border of the shifted region (for
	 * example, gradient computations implicitly use a small neighborhood
	 * which might be affected by the background near the border).
	 */
	virtual int SuggestedPixelShift() const;

	/* Extract a descriptor for a window from zero-based top-left (y,x) of
	 * width/height (pixel_width,pixel_height).  Store the result in desc.
	 * The descriptor must be preallocated and of the correct size.  If the
	 * desc_base_index is given and non-zero, the descriptor is stored with an
	 * offset.  This allows efficient concatenation of multiple descriptor
	 * types.
	 *
	 * Note: The given subwindow must be completely contained inside the image
	 * set with InitializeImage.
	 */
	virtual void ExtractDescriptor(const vigra::FVector3Image& image,
		int x, int y, int pixel_width, int pixel_height,
		std::vector<double>& desc, unsigned int desc_base_index = 0) const;
};

}

#endif

