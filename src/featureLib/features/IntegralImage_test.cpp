
#include <cppunit/BriefTestProgressListener.h>
#include <cppunit/CompilerOutputter.h>
#include <cppunit/extensions/TestFactoryRegistry.h>
#include <cppunit/TestResult.h>
#include <cppunit/TestResultCollector.h>
#include <cppunit/TestRunner.h>
#include <cppunit/config/SourcePrefix.h>

#include <vector>
#include <iostream>
#include <gmm/gmm.h>

#include "IntegralImage.h"
#include "IntegralImage_test.h"

CPPUNIT_TEST_SUITE_REGISTRATION(IntegralImageTest);

void IntegralImageTest::Simple() {
	//  1 0 0 0 2 3
	//  0 1 0 0 4 5
	//  0 0 1 0 6 7
	// 11 0 0 1 8 9
	gmm::dense_matrix<double> input(4, 6);
	gmm::clear(input);
	input(0, 0) = 1;
	input(1, 1) = 1;
	input(2, 2) = 1;
	input(3, 3) = 1;
	input(3, 0) = 11;
	input(0, 4) = 2;
	input(0, 5) = 3;
	input(1, 4) = 4;
	input(1, 5) = 5;
	input(2, 4) = 6;
	input(2, 5) = 7;
	input(3, 4) = 8;
	input(3, 5) = 9;
	Features::IntegralImage iim(input);

	// Test to recover the original input
	for (unsigned int r = 0; r < gmm::mat_nrows(input); ++r) {
		for (unsigned int c = 0; c < gmm::mat_ncols(input); ++c) {
			double input_val = input(r, c);
			double iim_val = iim(r, c, r, c);
#ifdef DEBUG
			std::cout << "test1: (r,c) " << r << ", " << c << "   "
				<< "input " << input_val << "  iim " << iim_val
				<< std::endl;
#endif
			CPPUNIT_ASSERT_DOUBLES_EQUAL(input_val, iim_val, 1e-5);
		}
	}

	// Compute all possible true integrals naively and compare with the
	// integral image value
	for (unsigned int r1 = 0; r1 < gmm::mat_nrows(input); ++r1) {
		for (unsigned int c1 = 0; c1 < gmm::mat_ncols(input); ++c1) {
			for (unsigned int r2 = r1; r2 < gmm::mat_nrows(input); ++r2) {
				for (unsigned int c2 = c1; c2 < gmm::mat_ncols(input); ++c2) {
					// Compute the true value naively
					double true_value = 0;
					for (unsigned int r = r1; r <= r2; ++r)
						for (unsigned int c = c1; c <= c2; ++c)
							true_value += input(r, c);

					// Compute the value by integral image
					double iim_value = iim(r1, c1, r2, c2);
#ifdef DEBUG
					std::cout << "(r1,c1) " << r1 << ", " << c1 << "   "
						<< "(r2,c2) " << r2 << ", " << c2 << "   "
						<< "true " << true_value << "  iim " << iim_value
						<< std::endl;
#endif
					CPPUNIT_ASSERT_DOUBLES_EQUAL(true_value, iim_value, 1e-5);
				}
			}
		}
	}
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


