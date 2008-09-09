/* Utility code
 *
 * Copyright (C) 2007 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#ifndef	FEATURES_UTILITY_H
#define	FEATURES_UTILITY_H

#include <vigra/stdimage.hxx>
#include <vigra/stdimagefunctions.hxx>
#include <vigra/impex.hxx>

#include <gmm/gmm.h>

namespace Features {

template <typename MATRIX>
void instantiate_vectorfield(MATRIX& field,
	const typename gmm::linalg_traits<MATRIX>::value_type& init) {
	for (unsigned int row = 0; row < gmm::mat_nrows(field); ++row)
		for (unsigned int col = 0; col < gmm::mat_ncols(field); ++col)
			field(row, col) = init;
};

// Utility class to access gray versions of vector-valued images with the
// spline image class
template <class VECTORVALUE>
class VectorMeanAccessor {
public:
	typedef typename VECTORVALUE::value_type::value_type value_type;

	// Get mean value of the vector
	template <class ITERATOR> value_type operator()(ITERATOR const& i) const {
		value_type mean(0);
		for (unsigned int n = 0; n < i->size(); ++n)
			mean += (*i)[n];

		return (mean / static_cast<double>(i->size()));
	}
};

template <class VECTORVALUE>
class VectorMeanTransformAccessor {
public:
	typedef typename VECTORVALUE::value_type::value_type value_type;

	// Get mean value of the vector
	template <class ITERATOR> value_type operator()(ITERATOR const& i) const {
		value_type mean(0);
		for (unsigned int n = 0; n < i.size(); ++n)
			mean += i[n];

		return (mean / static_cast<double>(i.size()));
	}
};

class ImageLoader {
public:
	static bool LoadImage(const std::string& filename,
		vigra::FVector3Image& image, bool verbose = false);

private:
	ImageLoader();
};

/* Calculate each channel's gradient magnitude separately, then choose the
 * maximum magnitude channel and compute its gradient direction.
 * To be used with vigra::gradientBasedTransform().
 * [0] is magnitude, [1] direction.
 */
template <class ValueType>
class RGBMaxChannelGradientFunctor {
public:
	typedef vigra::RGBValue<ValueType> first_argument_type;
	typedef vigra::RGBValue<ValueType> second_argument_type;
	typedef typename vigra::BasicImage<
		vigra::TinyVector<ValueType, 2> >::value_type result_type;
	typedef typename vigra::BasicImage<
		vigra::TinyVector<ValueType, 2> >::value_type value_type;

	explicit RGBMaxChannelGradientFunctor(
		bool undirected_gradients = false)
		: undirected_gradients(undirected_gradients)
	{
	}

	/* Calculate:
	 * argmin_{c \in {R,G,B}} |sqrt(gx_c*gx_c + gy_c*gy_c)|
	 */
	result_type operator()(const first_argument_type& gx,
		const second_argument_type& gy) const {
		double m_red_sq = gx.red()*gx.red() + gy.red()*gy.red();
		double m_green_sq = gx.green()*gx.green() + gy.green()*gy.green();
		double m_blue_sq = gx.blue()*gx.blue() + gy.blue()*gy.blue();
		double m_max = m_red_sq;
		double d_max = VIGRA_CSTD::atan2(gy.red(), gx.red());
		if (m_green_sq > m_max) {
			m_max = m_green_sq;
			d_max = VIGRA_CSTD::atan2(gy.green(), gx.green());
		} if (m_blue_sq > m_max) {
			m_max = m_blue_sq;
			d_max = VIGRA_CSTD::atan2(gy.blue(), gx.blue());
		}
		m_max = VIGRA_CSTD::sqrt(m_max);

		// Bring direction to [0; 1].
		d_max += M_PI;
		if (undirected_gradients) {
			// Wrap 180-360 degrees back into 0-180.
			if (d_max >= M_PI)
				d_max -= M_PI;
			d_max /= M_PI;	// 0-180 range
		} else {
			d_max /= 2.0*M_PI;	// full 0-360 range
		}

		return (vigra::TinyVector<ValueType, 2>(m_max, d_max));
	}

private:
	bool undirected_gradients;
};

// To be used with floating point images.  Output element zero will contain
// the gradient magnitude, element one will contain the gradient orientation.
template <class ValueType>
class MagnitudeOrientationGradientFunctor {
public:
	typedef ValueType first_argument_type;
	typedef ValueType second_argument_type;
	typedef typename vigra::BasicImage<
		vigra::TinyVector<ValueType, 2> >::value_type result_type;
	typedef typename vigra::BasicImage<
		vigra::TinyVector<ValueType, 2> >::value_type value_type;

	// If undirected_gradients == true, the gradient direction is discarded.
	explicit MagnitudeOrientationGradientFunctor(
		bool undirected_gradients = false)
		: undirected_gradients(undirected_gradients)
	{
	}

	/* Calculate gradient magnitude (element zero) and orientation (element
	 * one).
	 */
	result_type operator()(const first_argument_type& gx,
		const second_argument_type& gy) const {
		double m = VIGRA_CSTD::sqrt(gx*gx + gy*gy);
		double d = VIGRA_CSTD::atan2(gy, gx);

		// Bring direction to [0; 1] range.
		d += M_PI;
		if (undirected_gradients) {
			// Wrap 180-360 degrees back into 0-180.
			if (d >= M_PI)
				d -= M_PI;
			d /= M_PI;	// 0-180 range
		} else {
			d /= 2.0*M_PI;	// full 0-360 range
		}

		return (vigra::TinyVector<ValueType, 2>(m, d));
	}

private:
	bool undirected_gradients;
};

}

#endif

