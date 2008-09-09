/* Region Covariance features, due to Tuzel, Porikli and Meer.
 *
 * Copyright (C) 2008 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#ifndef	FEATURES_REGIONCOVARIANCE_H
#define	FEATURES_REGIONCOVARIANCE_H

#include <vector>
#include <gmm/gmm.h>
#include <vigra/stdimagefunctions.hxx>

#include "DenseFeature.h"
#include "IntegralImage.h"
#include "utility.h"

namespace Features {

/* Implements the fast region covariance descriptor as described in
 *
 * [Tuzel2007]  Oncel Tuzel, Fatih Porikli and Peter Meer, "Human Detection
 *   via Classification of Riemannian Manifolds", CVPR 2007,
 * and
 * [Tuzel2006]  Oncel Tuzel, Fatih Porikli and Peter Meer, "Region Covariance:
 *   A Fast Descriptor for Detection and Classification", ECCV 2006.
 *
 * We use the tangent space projection technique to map the covariance
 * features into a vector space.  Hence normal machine learning techniques
 * can be used with this features.
 */
class RegionCovariance : public DenseFeature {
public:
	// normalize_with_image: If true, the normalization is performed with
	//     respect to the covariance matrix of the entire image, if false the
	//     normalization is with respect to the single covariance matrix.
	RegionCovariance(bool normalize_with_image = true);

	virtual void InitializeImage(const vigra::FVector3Image& image);
	virtual int MemoryBound(const vigra::FVector3Image& image) const;
	virtual int DescriptorSizeFromPixels(int pixel_width, int pixel_height) const;
	virtual int SuggestedPixelShift() const;
	virtual void ExtractDescriptor(const vigra::FVector3Image& image,
		int x, int y, int pixel_width, int pixel_height,
		std::vector<double>& desc, unsigned int desc_base_index = 0) const;

private:
	// The ridge added to every covariance matrix (for numerical stability)
	static const double ridge = 1e-3;

	// Number of features
	static const unsigned int feature_count = 7;	// 9
	static const bool perform_L2_normalization = true;

	// true: normalize with image, false: normalize by subwindow
	bool normalize_with_image;

	// d first order integral images: feature maps
	std::vector<IntegralImage> iim_1;

	// (d*(d-1))/2 second order integral images: f_i*f_j
	// The order is given as 1*2, 1*3, ..., 1*d, 2*3, 2*4, ..., 2*d, ..
	std::vector<IntegralImage> iim_2;

	// Covariance matrix for the entire image, precomputed once.
	gmm::dense_matrix<double> Cimage;

	// Normalization of the covariance matrix, see end of section 2 of
	// [Tuzel2007].  The result is the same as if each feature in C would have
	// been normalized individually to zero mean and unit standard deviation.
	//
	// The first method normalizes C intrinsically with itself.  The second
	// method normalizes C with respect to Cbase.  Usually Cbase is the entire
	// image, and C belongs to a subwindow within the image.
	void NormalizeCovarianceMatrix(gmm::dense_matrix<double>& C) const;
	void NormalizeCovarianceMatrix(gmm::dense_matrix<double>& C,
		const gmm::dense_matrix<double>& Cbase) const;

	// Compute the unnormalized covariance matrix for a window with upper-left
	// corner (x, y) of size (pixel_width, pixel_height).  A ridge is added to
	// the matrix and the regularized matrix is stored in C.  C needs to have
	// a the right size already but its values will be properly initialized.
	void ComputeCovarianceMatrix(int x, int y,
		int pixel_width, int pixel_height, gmm::dense_matrix<double>& C) const;
};

}

#endif

