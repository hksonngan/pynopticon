/* Region Covariance features, due to Tuzel, Porikli and Meer.
 *
 * Copyright (C) 2008 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#include <math.h>

#include <vigra/colorconversions.hxx>
#include <vigra/transformimage.hxx>
#include <vigra/combineimages.hxx>
#include <vigra/tensorutilities.hxx>
#include <vigra/boundarytensor.hxx>

#include "RegionCovariance.h"
#include "utility.h"

namespace Features {

RegionCovariance::RegionCovariance(bool normalize_with_image)
	: normalize_with_image(normalize_with_image) {
}

void RegionCovariance::InitializeImage(const vigra::FVector3Image& image) {
	// Discard previous image
	iim_1.clear();
	iim_2.clear();

	// 1. Extract feature maps explicitly, as in Tuzel
	std::vector<gmm::dense_matrix<double> > fmap;

	//     i) x/y coordinate maps, relative to window width/height
	gmm::dense_matrix<double> fmap_x(image.height(), image.width());
	gmm::dense_matrix<double> fmap_y(image.height(), image.width());
	for (int y = 0; y < image.height(); ++y) {
		for (int x = 0; x < image.width(); ++x) {
			fmap_x(y, x) = x;
			fmap_y(y, x) = y;
		}
	}
	fmap.push_back(fmap_x);
	fmap.push_back(fmap_y);

	//    ii) LUV colors
	vigra::FVector3Image luv(image.width(), image.height());
	vigra::transformImage(srcImageRange(image), destImage(luv),
		vigra::RGB2LuvFunctor<float>());
	gmm::dense_matrix<double> fmap_luv_l(image.height(), image.width());
	gmm::dense_matrix<double> fmap_luv_u(image.height(), image.width());
	gmm::dense_matrix<double> fmap_luv_v(image.height(), image.width());
	for (int y = 0; y < image.height(); ++y) {
		for (int x = 0; x < image.width(); ++x) {
			// L range: 0 <= L <= 100,
			// U range: -83.077 <= U <= 175.015
			// V range: -134.101 <= V <= 107.393
			//
			// But all features are implicitly normalized below, so the ranges
			// do not matter.
			fmap_luv_l(y, x) = luv(x, y)[0];
			fmap_luv_u(y, x) = luv(x, y)[1];
			fmap_luv_v(y, x) = luv(x, y)[2];
		}
	}
	fmap.push_back(fmap_luv_l);
	fmap.push_back(fmap_luv_u);
	fmap.push_back(fmap_luv_v);

	//   iii) gradient magnitude and orientation of the local maximum RGB
	//        plane
	// Each gradient(x,y) contains magnitude and direction (in 0-1 range)
	vigra::FVector2Image gradient(image.width(), image.height());
	// TODO: which one to chose here? luv or rgb?  luv would be more invariant
	//vigra::gradientBasedTransform(srcImageRange(image),
	vigra::gradientBasedTransform(srcImageRange(luv),
		destImage(gradient), RGBMaxChannelGradientFunctor<float>());
	gmm::dense_matrix<double> fmap_gm(image.height(), image.width());
	gmm::dense_matrix<double> fmap_go(image.height(), image.width());
	for (int y = 0; y < image.height(); ++y) {
		for (int x = 0; x < image.width(); ++x) {
			fmap_gm(y, x) = gradient(x, y)[0];	// magnitude
			fmap_go(y, x) = gradient(x, y)[1];	// orientation
		}
	}
	fmap.push_back(fmap_gm);
	fmap.push_back(fmap_go);

	//    iv) second order gradient x/y magnitudes
	// TODO

#if 0
	//     v) boundary and corner tensor, as implemented in libvigra, see the
	//        boundarytensor.cxx example in libvigra.
	vigra::FVector3Image btensor(image.width(), image.height());
	vigra::FVector3Image bandtensor(image.width(), image.height());
	for (unsigned int band = 0; band < 3; ++band) {
		vigra::VectorElementAccessor<vigra::FVector3Image::Accessor> va(band);
		vigra::boundaryTensor(srcImageRange(image, va),
			destImage(bandtensor), 2.0);	// TODO: configurable scale
		vigra::combineTwoImages(srcImageRange(btensor), srcImage(bandtensor),
			destImage(btensor), std::plus<vigra::FVector3Image::value_type>());
	}
	vigra::FImage bstrength(image.width(), image.height());	// boundary strength
	vigra::FImage cstrength(image.width(), image.height());	// corner strength
	vigra::FVector2Image estrength(image.width(), image.width());	// edge strength
	vigra::tensorTrace(srcImageRange(btensor), destImage(bstrength));
	vigra::tensorToEdgeCorner(srcImageRange(btensor),
		destImage(estrength), destImage(cstrength));

	gmm::dense_matrix<double> fmap_bstrength(image.height(), image.width());
	gmm::dense_matrix<double> fmap_cstrength(image.height(), image.width());
	for (int y = 0; y < image.height(); ++y) {
		for (int x = 0; x < image.width(); ++x) {
			fmap_bstrength(y, x) = bstrength(x, y);
			fmap_cstrength(y, x) = cstrength(x, y);
		}
	}
	fmap.push_back(fmap_bstrength);
	fmap.push_back(fmap_cstrength);
#endif

	// 2. Build integral images
	//     i) individual feature maps
	for (unsigned int si1 = 0; si1 < fmap.size(); ++si1)
		iim_1.push_back(IntegralImage(fmap[si1]));

	//    ii) product maps
	for (unsigned int si1 = 0; si1 < fmap.size(); ++si1)
		for (unsigned int si2 = si1; si2 < fmap.size(); ++si2)
			iim_2.push_back(IntegralImage(fmap[si1], fmap[si2]));

	assert(feature_count == iim_1.size());

	// Precompute the covariance matrix of the entire image for
	// subwindow normalization with respect to the entire image.
	Cimage.resize(feature_count, feature_count);
	ComputeCovarianceMatrix(0, 0, image.width(), image.height(), Cimage);
}

int RegionCovariance::MemoryBound(const vigra::FVector3Image& image) const {
	// Total number of integral images
	int res = 2 * feature_count + (feature_count * (feature_count - 1)) / 2;

	// Times number of pixels, each being a float
	return (res * sizeof(float) * image.width() * image.height());
}

int RegionCovariance::DescriptorSizeFromPixels(int pixel_width,
	int pixel_height) const {
	return (feature_count + (feature_count * (feature_count - 1)) / 2);
}

int RegionCovariance::SuggestedPixelShift() const {
	// Per-pixel evaluation is possible and makes sense, hence one.
	return (1);
}

void RegionCovariance::ExtractDescriptor(const vigra::FVector3Image& image,
	int x, int y, int pixel_width, int pixel_height,
	std::vector<double>& desc, unsigned int desc_base_index) const {
	assert(x >= 0 && y >= 0);
	assert((x + pixel_width) <= image.width());
	assert((y + pixel_height) <= image.height());
	assert(iim_1.size() == feature_count);
	assert(pixel_width > 1 && pixel_height > 1);

	// Build covariance matrix of the window
	gmm::dense_matrix<double> C(feature_count, feature_count);
	ComputeCovarianceMatrix(x, y, pixel_width, pixel_height, C);

	// Normalize, see end of section 2 of [Tuzel2007]
	if (normalize_with_image) {
		NormalizeCovarianceMatrix(C, Cimage);
	} else {
		//std::cout << "C before norm: " << std::endl << C << std::endl;
		NormalizeCovarianceMatrix(C);
		//std::cout << "C after norm: " << std::endl << C << std::endl;
	}

	// Map to the tangent space at I by
	//   log_X(Y) = X^0.5 log(X^-0.5 Y X^-0.5) X^0.5,
	// with X=I we have
	//   log_I(Y) = log(Y) = U log(lambda) U',
	// where U D U' is the Eigendecomposition of Y.
	//
	// For X != I, we would have to use the Denman-Beavers square root
	// iteration
	//     1. Y_0 = X, Z_0 = I
	//     2. For k = 1,...,K
	//         i) Y_{k+1} <- 0.5 * (Y_k + inv(Z_k))
	//        ii) Z_{k+1} <- 0.5 * (Z_k + inv(Y_k))
	// where Y_K \approx X^0.5 and Z_k \approx X^-0.5, with quadratic
	// convergence in K.
	gmm::dense_matrix<double> U(feature_count, feature_count);
	std::vector<double> lambda(feature_count);
	gmm::symmetric_qr_algorithm(C, lambda, U);
	gmm::dense_matrix<double> D(feature_count, feature_count);
	gmm::clear(D);
	for (unsigned int d = 0; d < feature_count; ++d)
		D(d, d) = log(lambda[d]);
	gmm::mult(U, D, C);	// U D
	gmm::copy(C, D);
	gmm::mult(D, gmm::transposed(U), C);	// C <- U D U'

	// Store the descriptor by linearizing the upper triangular part.
	// Afterwards normalize by L2 norm.
	unsigned int idx = 0;
	double norm = 0.0;
	for (unsigned int r = 0; r < feature_count; ++r) {
		for (unsigned int c = r; c < feature_count; ++c) {
			desc[desc_base_index + idx] = C(r, c);
			norm += C(r, c) * C(r, c);
			idx += 1;
		}
	}
	assert(DescriptorSizeFromPixels(pixel_width, pixel_height) ==
		static_cast<int>(idx));

	if (perform_L2_normalization) {
		// L2 normalization
		norm = sqrt(norm);
		for (unsigned int n = 0; n < idx; ++n)
			desc[desc_base_index + n] /= norm;
	}
}

void RegionCovariance::NormalizeCovarianceMatrix(
	gmm::dense_matrix<double>& C) const {
	NormalizeCovarianceMatrix(C, C);
}

// Normalize C, but with respect to Cbase.
void RegionCovariance::NormalizeCovarianceMatrix(
	gmm::dense_matrix<double>& C,
	const gmm::dense_matrix<double>& Cbase) const {
	assert(feature_count == gmm::mat_nrows(C));
	assert(feature_count == gmm::mat_ncols(C));
	assert(feature_count == gmm::mat_nrows(Cbase));
	assert(feature_count == gmm::mat_ncols(Cbase));
	std::vector<double> diag_sqrt(feature_count);
	for (unsigned int d = 0; d < feature_count; ++d) {
		assert(Cbase(d, d) >= 0.0);
		diag_sqrt[d] = sqrt(Cbase(d, d));
	}

	// Proper normalization
	for (unsigned int r = 0; r < feature_count; ++r) {
		for (unsigned int c = 0; c < feature_count; ++c) {
			assert(fabs(diag_sqrt[r] * diag_sqrt[c]) > 1e-8);
			C(r, c) /= diag_sqrt[r] * diag_sqrt[c];
		}
	}
}

void RegionCovariance::ComputeCovarianceMatrix(int x, int y,
	int pixel_width, int pixel_height, gmm::dense_matrix<double>& C) const {
	gmm::clear(C);
	double ncount = pixel_width * pixel_height;	// number of window pixels

	//   i) first obtain individual feature integrals
	std::vector<double> dself(feature_count);
	gmm::clear(dself);
	int xend = x + pixel_width - 1;
	int yend = y + pixel_height - 1;
	for (unsigned int d = 0; d < feature_count; ++d)
		dself[d] = iim_1[d](y, x, yend, xend);

	//  ii) off-diagonal
	unsigned int pidx = 0;
	for (unsigned int r = 0; r < feature_count; ++r) {
		for (unsigned int c = r; c < feature_count; ++c) {
			// C(i,j) = (1/(n-1)) (\sum_{k=1}^n z_k(i) z_k(j)
			//          - (1/n) \sum_{k=1}^n z_k(i) \sum_{k=1}^n z_k(j) )
			double cvalue = - (dself[r] * dself[c]) / ncount;
			cvalue += iim_2[pidx](y, x, yend, xend);
			cvalue /= ncount - 1.0;
			C(c, r) = C(r, c) = cvalue;

			pidx += 1;
		}
	}

	// Add a ridge for numerical stability upon inversion
	for (unsigned int r = 0; r < feature_count; ++r)
		C(r, r) += ridge;
}

}

