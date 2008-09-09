
#include <cppunit/BriefTestProgressListener.h>
#include <cppunit/CompilerOutputter.h>
#include <cppunit/extensions/TestFactoryRegistry.h>
#include <cppunit/TestResult.h>
#include <cppunit/TestResultCollector.h>
#include <cppunit/TestRunner.h>
#include <cppunit/config/SourcePrefix.h>

#include <vector>
#include <iostream>

#include <vigra/stdimage.hxx>
#include <vigra/copyimage.hxx>
#include <vigra/colorconversions.hxx>
#include <vigra/transformimage.hxx>

#include <stdlib.h>
#include <math.h>

#include "DenseFeature_test.h"
#include "DenseFeature.h"
#include "SlidingWindow.h"
#include "HoG.h"
#include "LBP.h"
#include "RegionCovariance.h"
#include "ColorHistogram.h"
#include "LocalSelfSimilarity.h"
#include "EdgeHistogram.h"
#include "utility.h"

CPPUNIT_TEST_SUITE_REGISTRATION(DenseFeatureTest);

void DenseFeatureTest::Extract() {
	vigra::FVector3Image image;
	std::string filename = "testdata/test.png";
	bool success = Features::ImageLoader::LoadImage(filename, image);
	CPPUNIT_ASSERT(success);

	// Use HoG class to test dense image feature abstraction
	Features::HistogramOfGradients hog;
	hog.InitializeImage(image);

	int pixel_width = 32;
	int pixel_height = 48;
	std::vector<double> desc(
		hog.DescriptorSizeFromPixels(pixel_width, pixel_height));

	CPPUNIT_ASSERT(hog.PixelsToBlocks(image.width())-1 == hog.BlocksX(image));
	CPPUNIT_ASSERT(hog.PixelsToBlocks(image.height())-1 == hog.BlocksY(image));

	/* std::cout << "Suggested pixel shift: "
		<< hog.SuggestedPixelShift() << std::endl; */

	Features::SlidingWindow_iterator swi(image, pixel_width, pixel_height,
		hog.SuggestedPixelShift());
	for ( ; swi.IsValid(); ++swi) {
		const Features::SlidingWindow& cur = *swi;
		if (cur.scale > 0)	// only do first scale for now
			break;

		/* std::cout << "win: (" << cur.x << "," << cur.y << "), size ("
			<< cur.width << "," << cur.height << ")" << std::endl; */
		hog.ExtractDescriptor(image, cur.x, cur.y,
			cur.width, cur.height, desc);
	}
}

void DenseFeatureTest::HoGShift() {
	vigra::FVector3Image image;
	std::string filename = "testdata/test.png";
	bool success = Features::ImageLoader::LoadImage(filename, image);
	CPPUNIT_ASSERT(success);

	// Use HoG class to test dense image feature abstraction
	Features::HistogramOfGradients hog1;
	Features::HistogramOfGradients hog2;

	ShiftTest(hog1, hog2, image);
}

void DenseFeatureTest::LBPShift() {
	vigra::FVector3Image image;
	std::string filename = "testdata/test.png";
	bool success = Features::ImageLoader::LoadImage(filename, image);
	CPPUNIT_ASSERT(success);

	// Use LBP class to test dense image feature abstraction
	Features::LocalBinaryPattern lbp1;
	Features::LocalBinaryPattern lbp2;
	ShiftTest(lbp1, lbp2, image);

	Features::LocalBinaryPattern lbp3(11, 2.0);
	Features::LocalBinaryPattern lbp4(11, 2.0);
	ShiftTest(lbp3, lbp4, image);
}

void DenseFeatureTest::LocalSelfSimilarityShift1() {
	vigra::FVector3Image image;
	std::string filename = "testdata/test.png";
	bool success = Features::ImageLoader::LoadImage(filename, image);
	CPPUNIT_ASSERT(success);

	// Use LBP class to test dense image feature abstraction
	Features::LocalSelfSimilarity df1;
	Features::LocalSelfSimilarity df2;

	// Produce a shifted image, then compare the extracted features on the
	// shifted windows.
	df1.InitializeImage(image);
	int shift_width_x = 2 * df1.SuggestedPixelShift();
	int shift_width_y = 1 * df1.SuggestedPixelShift();
	vigra::FVector3Image image_shifted(image.width() + shift_width_x,
		image.height() + shift_width_y);
	vigra::initImage(vigra::destImageRange(image_shifted),
		vigra::NumericTraits<vigra::FVector3Image::PixelType>::zero());
	vigra::copyImage(vigra::srcImageRange(image),
		vigra::destImage(image_shifted,
			vigra::Point2D(shift_width_x, shift_width_y)));
	df2.InitializeImage(image_shifted);

	int pixel_width = 5;
	int pixel_height = 5;
	CPPUNIT_ASSERT(df1.DescriptorSizeFromPixels(pixel_width, pixel_height) ==
		df2.DescriptorSizeFromPixels(pixel_width, pixel_height));
	std::vector<double> desc1(
		df1.DescriptorSizeFromPixels(pixel_width, pixel_height));
	std::vector<double> desc2(
		df2.DescriptorSizeFromPixels(pixel_width, pixel_height));

	df1.ExtractDescriptor(image, 120, 100, 5, 5, desc1);
	df2.ExtractDescriptor(image_shifted, 120 + shift_width_x,
		100 + shift_width_y, 5, 5, desc2);

	for (unsigned int n = 0; n < desc1.size(); ++n)
		CPPUNIT_ASSERT_DOUBLES_EQUAL(desc1[n], desc2[n], 0.05);
}

void DenseFeatureTest::LocalSelfSimilarityShift() {
	vigra::FVector3Image image;
	std::string filename = "testdata/test.png";
	bool success = Features::ImageLoader::LoadImage(filename, image);
	CPPUNIT_ASSERT(success);

	// Use LBP class to test dense image feature abstraction
	Features::LocalSelfSimilarity lss1;
	Features::LocalSelfSimilarity lss2;
	ShiftTest(lss1, lss2, image, 41);
}

void DenseFeatureTest::RegionCovarianceShift() {
	vigra::FVector3Image image;
	std::string filename = "testdata/test.png";
	bool success = Features::ImageLoader::LoadImage(filename, image);
	CPPUNIT_ASSERT(success);

	// Use RegionCovariance features
	Features::RegionCovariance rcov1sw(false);
	Features::RegionCovariance rcov2sw(false);
	ShiftTest(rcov1sw, rcov2sw, image);

#if 0
	// The image wide normalization should fail because of the boundary pixels
	// we add the global normlization factors get modified.
	std::cout << "Image normalization" << std::endl;
	Features::RegionCovariance rcov1(true);
	Features::RegionCovariance rcov2(true);
	ShiftTest(rcov1, rcov2, image);
#endif
}

void DenseFeatureTest::RegionCovarianceIntensityTest() {
	vigra::FVector3Image image;
	std::string filename = "testdata/test-max250.png";
	bool success = Features::ImageLoader::LoadImage(filename, image);
	CPPUNIT_ASSERT(success);

	// Use RegionCovariance features
	// i) subwindow normalization
	Features::RegionCovariance rcov1sw(false);
	Features::RegionCovariance rcov2sw(false);
	IntensityInvarianceTest(rcov1sw, rcov2sw, image);

	// ii) image normalization
	Features::RegionCovariance rcov1(true);
	Features::RegionCovariance rcov2(true);
	IntensityInvarianceTest(rcov1, rcov2, image);
}

void DenseFeatureTest::EdgeHistogramIntensityTest() {
	vigra::FVector3Image image;
	std::string filename = "testdata/test-max250.png";
	bool success = Features::ImageLoader::LoadImage(filename, image);
	CPPUNIT_ASSERT(success);

	Features::EdgeHistogram eh1;
	Features::EdgeHistogram eh2;
	IntensityInvarianceTest(eh1, eh2, image, 0.05);
}

void DenseFeatureTest::EdgeHistogramShiftTest() {
	vigra::FVector3Image image;
	std::string filename = "testdata/test-max250.png";
	bool success = Features::ImageLoader::LoadImage(filename, image);
	CPPUNIT_ASSERT(success);

	Features::EdgeHistogram eh1;
	Features::EdgeHistogram eh2;
	ShiftTest(eh1, eh2, image);
}

void DenseFeatureTest::ColorHistogramShift() {
	vigra::FVector3Image image;
	std::string filename = "testdata/test.png";
	bool success = Features::ImageLoader::LoadImage(filename, image);
	CPPUNIT_ASSERT(success);

	// Use color histogram features
	Features::ColorHistogram chist1("lab");
	Features::ColorHistogram chist2("lab");
	ShiftTest(chist1, chist2, image);
}

void DenseFeatureTest::ShiftTest(
	Features::DenseFeature& df1, Features::DenseFeature& df2,
	const vigra::FVector3Image& image, int border_ignore_size) const {
	// Produce a shifted image, then compare the extracted features on the
	// shifted windows.
	df1.InitializeImage(image);
	int shift_width_x = 2 * df1.SuggestedPixelShift();
	int shift_width_y = 1 * df1.SuggestedPixelShift();
	vigra::FVector3Image image_shifted(image.width() + shift_width_x,
		image.height() + shift_width_y);
	vigra::initImage(vigra::destImageRange(image_shifted),
		vigra::NumericTraits<vigra::FVector3Image::PixelType>::zero());
	vigra::copyImage(vigra::srcImageRange(image),
		vigra::destImage(image_shifted,
			vigra::Point2D(shift_width_x, shift_width_y)));
	df2.InitializeImage(image_shifted);

	// Assert the shifted image to be exactly the same as the original one
	for (int y = 0; y < image.height(); ++y) {
		for (int x = 0; x < image.width(); ++x) {
			CPPUNIT_ASSERT_EQUAL(image(x, y),
				image_shifted(x + shift_width_x, y + shift_width_y));
		}
	}

	int pixel_width = 32;
	int pixel_height = 48;
	CPPUNIT_ASSERT(df1.DescriptorSizeFromPixels(pixel_width, pixel_height) ==
		df2.DescriptorSizeFromPixels(pixel_width, pixel_height));
	std::vector<double> desc1(
		df1.DescriptorSizeFromPixels(pixel_width, pixel_height));
	std::vector<double> desc2(
		df2.DescriptorSizeFromPixels(pixel_width, pixel_height));

	Features::SlidingWindow_iterator swi(image, pixel_width, pixel_height,
		df1.SuggestedPixelShift());
	for ( ; swi.IsValid(); ++swi) {
		const Features::SlidingWindow& cur = *swi;
		if (cur.scale > 0)	// only do first scale for now
			break;

		// We exclude the border region because the feature computation (for
		// example the vigra gradient computations) cause a strong response
		// due to extrapolation at the image boundary.
		if (cur.x < border_ignore_size || cur.y < border_ignore_size
			|| (cur.x + pixel_width) >= (image.width() - border_ignore_size)
			|| (cur.y + pixel_height) >= (image.height() - border_ignore_size))
			continue;

#ifdef DEBUG
		std::cout << "win: (" << cur.x << "," << cur.y << "), size ("
			<< cur.width << "," << cur.height << ")" << std::endl;
#endif
		df1.ExtractDescriptor(image, cur.x, cur.y,
			cur.width, cur.height, desc1);
		df2.ExtractDescriptor(image_shifted,
			cur.x + shift_width_x, cur.y + shift_width_y,
			cur.width, cur.height, desc2);

		double norm1 = 0;
		double norm2 = 0;
		for (unsigned int n = 0; n < desc1.size(); ++n) {
			norm1 += desc1[n] * desc1[n];
			norm2 += desc2[n] * desc2[n];
			CPPUNIT_ASSERT_DOUBLES_EQUAL(desc1[n], desc2[n], 0.05);
		}
		CPPUNIT_ASSERT_DOUBLES_EQUAL(norm1, norm2, 0.05);
	}
}

// This test examines whether the feature is invariant to slight changes in
// lighting
void DenseFeatureTest::IntensityInvarianceTest(
	Features::DenseFeature& df1, Features::DenseFeature& df2,
	vigra::FVector3Image image, double allowed_deviation) const {
	// Produce a copy of the image, only changing the intensity globally by a
	// shift.
	df1.InitializeImage(image);
	vigra::FVector3Image image_brighter_luv(image.width(), image.height());
	vigra::transformImage(srcImageRange(image), destImage(image_brighter_luv),
		vigra::RGB2LuvFunctor<float>());
	for (int y = 0; y < image.height(); ++y)
		for (int x = 0; x < image.width(); ++x)
			image_brighter_luv(x, y)[0] += 1;
	vigra::FVector3Image image_brighter(image.width(), image.height());
	vigra::transformImage(srcImageRange(image_brighter_luv),
		destImage(image_brighter), vigra::Luv2RGBFunctor<float>());
#if 0
	vigra::copyImage(vigra::srcImageRange(image),
		vigra::destImage(image_brighter));
#endif
	df2.InitializeImage(image_brighter);

	int pixel_width = 32;
	int pixel_height = 48;
	CPPUNIT_ASSERT(df1.DescriptorSizeFromPixels(pixel_width, pixel_height) ==
		df2.DescriptorSizeFromPixels(pixel_width, pixel_height));
	std::vector<double> desc1(
		df1.DescriptorSizeFromPixels(pixel_width, pixel_height));
	std::vector<double> desc2(
		df2.DescriptorSizeFromPixels(pixel_width, pixel_height));

	Features::SlidingWindow_iterator swi(image, pixel_width, pixel_height,
		df1.SuggestedPixelShift());
	for ( ; swi.IsValid(); ++swi) {
		const Features::SlidingWindow& cur = *swi;
		if (cur.scale > 0)	// only do first scale for now
			break;

#ifdef DEBUG
		std::cout << "win: (" << cur.x << "," << cur.y << "), size ("
			<< cur.width << "," << cur.height << ")" << std::endl;
#endif
		df1.ExtractDescriptor(image, cur.x, cur.y,
			cur.width, cur.height, desc1);
		df2.ExtractDescriptor(image_brighter, cur.x, cur.y,
			cur.width, cur.height, desc2);

		double norm1 = 0;
		double norm2 = 0;
		for (unsigned int n = 0; n < desc1.size(); ++n) {
			norm1 += desc1[n] * desc1[n];
			norm2 += desc2[n] * desc2[n];
			CPPUNIT_ASSERT_DOUBLES_EQUAL(desc1[n], desc2[n], allowed_deviation);
		}
		CPPUNIT_ASSERT_DOUBLES_EQUAL(norm1, norm2, allowed_deviation);
	}
}

void DenseFeatureTest::IgnoreDescriptorElementTest() {
	vigra::FVector3Image image;
	std::string filename = "testdata/test.png";
	bool success = Features::ImageLoader::LoadImage(filename, image);
	CPPUNIT_ASSERT(success);

	Features::ColorHistogram chist("lab");
	IgnoreDescriptorElementTestSingle(chist, image);
	Features::HistogramOfGradients hog;
	IgnoreDescriptorElementTestSingle(hog, image);
	Features::LocalBinaryPattern lbp;
	IgnoreDescriptorElementTestSingle(lbp, image);
	Features::LocalSelfSimilarity lss;
	IgnoreDescriptorElementTestSingle(lss, image);
	Features::RegionCovariance regcov;
	IgnoreDescriptorElementTestSingle(regcov, image);
	Features::EdgeHistogram phog;
	IgnoreDescriptorElementTestSingle(phog, image);
}

void DenseFeatureTest::IgnoreDescriptorElementTestSingle(
	Features::DenseFeature& df, const vigra::FVector3Image& image) const {
	df.InitializeImage(image);
	std::vector<double> desc(2 + df.DescriptorSizeFromPixels(50, 50));
	double val1 = 7.41;
	double val2 = 5.287;
	desc[0] = val1;
	desc[1] = val1;
	desc[1 + df.DescriptorSizeFromPixels(50, 50)] = val2;
	df.ExtractDescriptor(image, 0, 0, 50, 50, desc, 1);
	CPPUNIT_ASSERT_EQUAL(val1, desc[0]);
	CPPUNIT_ASSERT_EQUAL(val2, desc[1 + df.DescriptorSizeFromPixels(50, 50)]);
	CPPUNIT_ASSERT(fabs(desc[1] - val1) > 1e-1);
}


int main(int argc, char **argv) {
	CPPUNIT_NS::TestResult controller;
	CPPUNIT_NS::TestResultCollector result;
	controller.addListener(&result);        
	CPPUNIT_NS::BriefTestProgressListener progress;
	controller.addListener(&progress);      

	CPPUNIT_NS::TestRunner runner;
	runner.addTest(CPPUNIT_NS::TestFactoryRegistry::getRegistry().makeTest());
	runner.run(controller);

	CPPUNIT_NS::CompilerOutputter outputter(&result, CPPUNIT_NS::stdCOut());
	outputter.write(); 

	return (result.wasSuccessful() ? 0 : 1);
}
