/* Dense image features.
 *
 * Copyright (C) 2007 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#include <vigra/stdimage.hxx>

#include "DenseFeature.h"

namespace Features {

DenseFeature::DenseFeature() {
}

DenseFeature::~DenseFeature() {
}

void DenseFeature::InitializeImage(const vigra::FVector3Image& image) {
}

int DenseFeature::MemoryBound(const vigra::FVector3Image& image) const {
	return (-1);
}

int DenseFeature::DescriptorSizeFromPixels(int pixel_width,
	int pixel_height) const {
	return (-1);
}

int DenseFeature::SuggestedPixelShift() const {
	return (-1);
}

void DenseFeature::ExtractDescriptor(const vigra::FVector3Image& image,
	int x, int y, int pixel_width, int pixel_height,
	std::vector<double>& desc, unsigned int desc_base_index) const {
}

}

