
include ../Makefile.config

#OBJS=DenseFeature.o HoG.o LBP.o RegionCovariance.o LocalSelfSimilarity.o \
	ColorHistogram.o EdgeHistogram.o IntegralImage.o

OBJS=DenseFeature.o LBP.o RegionCovariance.o ColorHistogram.o EdgeHistogram.o IntegralImage.o

###
all:	libfeatures.a

check:	DenseFeature_test IntegralImage_test HoG_test LocalSelfSimilarity_test
	./DenseFeature_test && ./IntegralImage_test && ./HoG_test && \
		./LocalSelfSimilarity_test

clean:
	rm -f *.o
	rm -f libfeatures.a
	rm -f DenseFeature_test IntegralImage_test HoG_test LocalSelfSimilarity_test

###
### Production build targets
###
libfeatures.a: $(OBJS)
	i586-mingw32msvc-ar rc libfeatures.a $(OBJS)
	i586-mingw32msvc-ranlib libfeatures.a

###
### Testcases
###
DenseFeature_test:	DenseFeature_test.o $(OBJS)
	$(CPP) $(CPPFLAGS) $(INCLUDE) -o DenseFeature_test DenseFeature_test.o \
		$(OBJS) $(CPPUNIT_LIB) $(VIGRA_LIB) $(FEATURES_UTILITY_LIB)

IntegralImage_test: IntegralImage_test.o IntegralImage.o
	$(CPP) $(CPPFLAGS) $(INCLUDE) -o IntegralImage_test IntegralImage_test.o \
		IntegralImage.o $(CPPUNIT_LIB)

HoG_test: HoG_test.o HoG.o DenseFeature.o
	$(CPP) $(CPPFLAGS) $(INCLUDE) -o HoG_test HoG_test.o HoG.o \
		DenseFeature.o \
		$(CPPUNIT_LIB) $(VIGRA_LIB) $(FEATURES_UTILITY_LIB)

LocalSelfSimilarity_test: LocalSelfSimilarity_test.o LocalSelfSimilarity.o DenseFeature.o
	$(CPP) $(CPPFLAGS) $(INCLUDE) -o LocalSelfSimilarity_test LocalSelfSimilarity_test.o \
		LocalSelfSimilarity.o DenseFeature.o \
		$(CPPUNIT_LIB) $(VIGRA_LIB) $(FEATURES_UTILITY_LIB)

