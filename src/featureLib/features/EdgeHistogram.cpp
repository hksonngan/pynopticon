/* Edge Histogram features, the same as the "PHOG" feature of Bosch and
 * Zisserman but we consider only one cell (i.e. one histogram).
 *
 * Copyright (C) 2008 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#include <assert.h>
#include <iostream>

#include <vigra/stdimage.hxx>
#include <vigra/impex.hxx>
#include <vigra/edgedetection.hxx>

#include <gmm/gmm.h>

#include "EdgeHistogram.h"

namespace Features {

EdgeHistogram::EdgeHistogram(unsigned int bin_count, bool undirected_edges)
	: bin_count(bin_count), undirected_edges(undirected_edges) {
}

void EdgeHistogram::InitializeImage(const vigra::FVector3Image& image) {
	// Consider grayscale image
	vigra::FImage image_gray(image.width(), image.height());
	vigra::transformImage(srcImageRange(image), destImage(image_gray),
		VectorMeanTransformAccessor<vigra::FVector3Image::Accessor>());

	// 1. Compute canny edge image
	vigra::BImage canny(image_gray.width(), image_gray.height());
	canny = 0;
	vigra::cannyEdgeImage(srcImageRange(image_gray), destImage(canny),
		1, 15, 255);	// scale, threshold, edgevalue
	//vigra::exportImage(srcImageRange(canny), "canny.png");

	// 2. Get gradient magnitude and orientation of original image
	vigra::FVector2Image gradient(canny.width(), canny.height());
	vigra::gradientBasedTransform(srcImageRange(image_gray),
		destImage(gradient),
		MagnitudeOrientationGradientFunctor<float>(undirected_edges));

	// 3. Produce matrices: histogram bin and gradient magnitude for each pixel
	bin_image.resize(gradient.height(), gradient.width());
	gmm::fill(bin_image, 0);
	bin_value.resize(gradient.height(), gradient.width());
	gmm::fill(bin_value, 0);
	for (int y = 0; y < gradient.height(); ++y) {
		for (int x = 0; x < gradient.width(); ++x) {
			// No edge -> skip
			if (canny(x, y) == 0)
				continue;

			// Edge: calculate bin index and gradient magnitude
			double magnitude = gradient(x, y)[0];
			double orientation = gradient(x, y)[1];	// range 0 to 1.
			assert(orientation >= 0.0 && orientation <= 1.0);
			if (orientation >= 1.0)
				orientation = 0.0;
			orientation *= static_cast<double>(bin_count);
			int orientation_index = static_cast<int>(orientation) % bin_count;

			// Bin value of zero denotes no edge.
			bin_image(y, x) = orientation_index + 1;
			bin_value(y, x) = magnitude;
		}
	}
}

int EdgeHistogram::MemoryBound(const vigra::FVector3Image& image) const {
	return (image.width() * image.height() * (2*sizeof(float) + 1));
}

int EdgeHistogram::DescriptorSizeFromPixels(int pixel_width,
	int pixel_height) const {
	return (bin_count);
}

int EdgeHistogram::SuggestedPixelShift() const {
	return (1);
}

void EdgeHistogram::ExtractDescriptor(const vigra::FVector3Image& image,
	int x, int y, int pixel_width, int pixel_height,
	std::vector<double>& desc, unsigned int desc_base_index) const {
	std::fill(desc.begin() + desc_base_index, desc.begin()
		+ desc_base_index + DescriptorSizeFromPixels(pixel_width, pixel_height),
		0);

	// Bin all edges in the subwindow
	double sum = 0.0;
	for (int py = 0; py < pixel_height; ++py) {
		for (int px = 0; px < pixel_width; ++px) {
			unsigned int bin_index = bin_image(y + py, x + px);
			if (bin_index == 0)
				continue;
			double val = bin_value(y + py, x + px);
			desc[desc_base_index + bin_index - 1] += val;
			sum += val;
		}
	}

	// 1-norm normalization, if possible
	if (fabs(sum) < 1e-8)
		return;
	for (unsigned int bin = 0; bin < bin_count; ++bin)
		desc[desc_base_index + bin] /= sum;
}

}

