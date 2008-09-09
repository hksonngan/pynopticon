/* Color histogram features.
 *
 * Copyright (C) 2008 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#include <assert.h>
#include <iostream>
#include <limits>
#include <gmm/gmm.h>

#include <vigra/colorconversions.hxx>
#include <vigra/transformimage.hxx>

#include "ColorHistogram.h"
#include "utility.h"

namespace Features {

ColorHistogram::ColorHistogram(const std::string& colorspace,
	unsigned int bins_per_dim)
	: colorspace(colorspace) {
	for (int dim = 0; dim < 3; ++dim)
		this->bins_per_dim.push_back(bins_per_dim);
}

ColorHistogram::ColorHistogram(const std::string& colorspace,
	unsigned int bins_dim1, unsigned int bins_dim2, unsigned int bins_dim3)
	: colorspace(colorspace) {
	this->bins_per_dim.push_back(bins_dim1);
	this->bins_per_dim.push_back(bins_dim2);
	this->bins_per_dim.push_back(bins_dim3);
}

void ColorHistogram::InitializeImage(const vigra::FVector3Image& image) {
	// Convert and normalize into desired colorspace
	vigra::FVector3Image cspace(image.width(), image.height());
	CheckImage(image);
	if (colorspace == "rgb") {
		vigra::copyImage(srcImageRange(image), destImage(cspace));
		NormalizePlanes(cspace, 0.0, 0.0, 0.0,	// add
			255.0, 255.0, 255.0);	// divide
		CheckImage(cspace);
	} else if (colorspace == "luv") {
		vigra::transformImage(srcImageRange(image), destImage(cspace),
			vigra::RGB2LuvFunctor<float>());
		CheckImage(cspace);
		NormalizePlanes(cspace, 0.0, 83.077, 134.101,	// add
			100.0, 175.015 + 83.077, 107.393 + 134.101);	// divide
		CheckImage(cspace);
	} else if (colorspace == "lab") {
		vigra::transformImage(srcImageRange(image), destImage(cspace),
			vigra::RGB2LabFunctor<float>());
		CheckImage(cspace);
		NormalizePlanes(cspace, 0.0, 86.1813, 107.862,	// add
			100.0, 86.1813 + 98.2352, 107.862 + 94.4758);	// divide
		CheckImage(cspace);
	} else if (colorspace == "hsv") {
		// TODO
		assert(0);
	} else {
		std::cerr << "Invalid colorspace \"" << colorspace << "\" "
			<< "requested." << std::endl;
		assert(0);
	}
#ifdef DEBUG
	std::cout << "ColorHistogram::InitializeImage: " << colorspace
		<< " (" << image.width() << " x " << image.height() << ")" << std::endl;
#endif

	// Per-dimension binning factor: idx = factor_per_dim[d] * pixel[d].
	std::vector<double> factor_per_dim;
	factor_per_dim.push_back(static_cast<double>(bins_per_dim[0]));
	factor_per_dim.push_back(static_cast<double>(bins_per_dim[1]));
	factor_per_dim.push_back(static_cast<double>(bins_per_dim[2]));

	bin_map.resize(image.height(), image.width());
	for (int y = 0; y < cspace.height(); ++y) {
		for (int x = 0; x < cspace.width(); ++x) {
			int idx_dim1 = cspace(x, y)[0] * factor_per_dim[0];
			int idx_dim2 = cspace(x, y)[1] * factor_per_dim[1];
			int idx_dim3 = cspace(x, y)[2] * factor_per_dim[2];
			if (idx_dim1 < 0)
				idx_dim1 = 0;
			if (idx_dim2 < 0)
				idx_dim2 = 0;
			if (idx_dim3 < 0)
				idx_dim3 = 0;
			if (idx_dim1 >= static_cast<int>(bins_per_dim[0]))
				idx_dim1 = bins_per_dim[0] - 1;
			if (idx_dim2 >= static_cast<int>(bins_per_dim[1]))
				idx_dim2 = bins_per_dim[1] - 1;
			if (idx_dim3 >= static_cast<int>(bins_per_dim[2]))
				idx_dim3 = bins_per_dim[2] - 1;

			// Build joint histogram index
			// Choose a linearization order such that luminosity (for luv/lab)
			// is the lowest dimension, just so we can see patterns more
			// easily in the output
			unsigned int idx = idx_dim2 * (bins_per_dim[2] * bins_per_dim[0])
				+ idx_dim3 * bins_per_dim[0] + idx_dim1;
			bin_map(y, x) = idx;
		}
	}
}

int ColorHistogram::MemoryBound(const vigra::FVector3Image& image) const {
	return (image.width() * image.height() * sizeof(unsigned int));
}

int ColorHistogram::DescriptorSizeFromPixels(int pixel_width, int pixel_height) const {
	return (bins_per_dim[0] * bins_per_dim[1] * bins_per_dim[2]);
}

int ColorHistogram::SuggestedPixelShift() const {
	return (1);
}

void ColorHistogram::ExtractDescriptor(const vigra::FVector3Image& image,
	int x, int y, int pixel_width, int pixel_height,
	std::vector<double>& desc, unsigned int desc_base_index) const {
	// Initialize
	int desc_len = DescriptorSizeFromPixels(pixel_width, pixel_height);
	for (int didx = 0; didx < desc_len; ++didx)
		desc[desc_base_index + didx] = 0.0;

	// Sort all pixels to the histogram, normalize
	double norm_factor = 1.0 / static_cast<double>(pixel_width * pixel_height);
	for (int cy = 0; cy < pixel_height; ++cy) {
		for (int cx = 0; cx < pixel_width; ++cx) {
			unsigned int hist_idx = bin_map(y + cy, x + cx);
			desc[desc_base_index + hist_idx] += 1.0 * norm_factor;
		}
	}
#ifdef DEBUG
	std::cout << "hist: " << gmm::row_vector(desc) << std::endl;
#endif
}

void ColorHistogram::NormalizePlanes(vigra::FVector3Image& cspace,
	double dim1_add, double dim2_add, double dim3_add,
	double dim1_div, double dim2_div, double dim3_div) const {
	for (int y = 0; y < cspace.height(); ++y) {
		for (int x = 0; x < cspace.width(); ++x) {
			cspace(x, y)[0] = (cspace(x, y)[0] + dim1_add) / dim1_div;
			cspace(x, y)[1] = (cspace(x, y)[1] + dim2_add) / dim2_div;
			cspace(x, y)[2] = (cspace(x, y)[2] + dim3_add) / dim3_div;
		}
	}
}

// Perform some basic tests and statistics on the image
void ColorHistogram::CheckImage(const vigra::FVector3Image& image) const {
	std::vector<double> max(3);
	std::fill(max.begin(), max.end(), -std::numeric_limits<double>::max());
	std::vector<double> min(3);
	std::fill(min.begin(), min.end(), std::numeric_limits<double>::max());
	std::vector<double> mean(3);
	std::fill(mean.begin(), mean.end(), 0.0);
	double count = 0;
	for (int y = 0; y < image.height(); ++y) {
		for (int x = 0; x < image.width(); ++x) {
			for (int dim = 0; dim < 3; ++dim) {
				if (image(x, y)[dim] < min[dim])
					min[dim] = image(x, y)[dim];
				if (image(x, y)[dim] > max[dim])
					max[dim] = image(x, y)[dim];
				mean[dim] += image(x, y)[dim];
			}
			count += 1;
		}
	}
	for (int dim = 0; dim < 3; ++dim) {
		mean[dim] /= count;
#ifdef DEBUG
		std::cout << "Channel " << dim << ", min " << min[dim]
			<< ", max " << max[dim] << ", mean " << mean[dim]
			<< std::endl;
#endif
	}
}

}

