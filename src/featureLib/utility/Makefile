
include ../Makefile.config

#OBJS=DenseFeature.o HoG.o LBP.o RegionCovariance.o LocalSelfSimilarity.o \
	ColorHistogram.o EdgeHistogram.o IntegralImage.o

OBJS=utility.o

###
all:	libutility.a

clean:
	rm -f *.o
	rm -f libutility.a

###
### Production build targets
###
libutility.a: $(OBJS)
	ar rc libutility.a $(OBJS)
	ranlib libutility.a

utility: utility.o
	$(CPP) $(CPPFLAGS) $(INCLUDE) -o utility.o \
		$(CPPUNIT_LIB) $(VIGRA_LIB) $(FEATURES_UTILITY_LIB)
