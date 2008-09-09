/* Edge Histogram features, the same as the "PHOG" feature of Bosch and
 * Zisserman.
 *
 * Copyright (C) 2008 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#ifndef FEATURES_EDGEHISTOGRAM_H
#define FEATURES_EDGEHISTOGRAM_H

#include <vector>

#include <vigra/stdimage.hxx>
#include <gmm/gmm.h>

#include "DenseFeature.h"
#include "utility.h"

namespace Features {

class EdgeHistogram : public DenseFeature {
public:
	/* bin_count: The number of bins circularly.
	 * undirected_edges: If false, the polarization of the edges matters.  If
	 *   true, the edges are treated as undirected.
	 */
	EdgeHistogram(unsigned int bin_count = 12, bool undirected_edges = false);

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
	// Number of bins circularly.
	unsigned int bin_count;

	// Directed (true) or undirected (false) edges.
	bool undirected_edges;

	// The bin index 1+(0 to bin_count-1) for each pixel, (y,x) indexing
	gmm::dense_matrix<unsigned int> bin_image;

	// The gradient value for each pixel, (y,x) indexing
	gmm::dense_matrix<float> bin_value;
};

}

#endif

