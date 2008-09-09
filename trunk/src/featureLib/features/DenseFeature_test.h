
#ifndef FEATURES_DENSEFEATURE_TEST_H
#define FEATURES_DENSEFEATURE_TEST_H

#include <cppunit/extensions/HelperMacros.h>

#include <vigra/stdimage.hxx>

#include "DenseFeature.h"

class DenseFeatureTest : public CPPUNIT_NS::TestFixture {
	CPPUNIT_TEST_SUITE(DenseFeatureTest);
	CPPUNIT_TEST(EdgeHistogramIntensityTest);
	CPPUNIT_TEST(EdgeHistogramShiftTest);
	CPPUNIT_TEST(IgnoreDescriptorElementTest);
	CPPUNIT_TEST(LocalSelfSimilarityShift1);
	CPPUNIT_TEST(LocalSelfSimilarityShift);
	CPPUNIT_TEST(RegionCovarianceIntensityTest);
	CPPUNIT_TEST(ColorHistogramShift);
	CPPUNIT_TEST(Extract);
	CPPUNIT_TEST(HoGShift);
	CPPUNIT_TEST(RegionCovarianceShift);
	CPPUNIT_TEST(LBPShift);
	CPPUNIT_TEST_SUITE_END();

protected:
	void Extract();
	void HoGShift();
	void RegionCovarianceShift();
	void RegionCovarianceIntensityTest();
	void LBPShift();
	void LocalSelfSimilarityShift();
	void LocalSelfSimilarityShift1();
	void ColorHistogramShift();
	void EdgeHistogramIntensityTest();
	void EdgeHistogramShiftTest();
	void IgnoreDescriptorElementTest();

	void ShiftTest(Features::DenseFeature& df1, Features::DenseFeature& df2,
		const vigra::FVector3Image& image, int border_ignore_size = 8) const;
	void IntensityInvarianceTest(Features::DenseFeature& df1,
		Features::DenseFeature& df2, vigra::FVector3Image image,
		double allowed_deviation = 0.01) const;
	void IgnoreDescriptorElementTestSingle(Features::DenseFeature& df,
		const vigra::FVector3Image& image) const;
};

#endif

