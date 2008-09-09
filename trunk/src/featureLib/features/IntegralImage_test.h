#ifndef FEATURES_INTEGRALIMAGE_TEST_H
#define FEATURES_INTEGRALIMAGE_TEST_H

#include <cppunit/extensions/HelperMacros.h>

class IntegralImageTest : public CPPUNIT_NS::TestFixture {
	CPPUNIT_TEST_SUITE(IntegralImageTest);
	CPPUNIT_TEST(Simple);
	CPPUNIT_TEST_SUITE_END();

protected:
	void Simple();
};

#endif


