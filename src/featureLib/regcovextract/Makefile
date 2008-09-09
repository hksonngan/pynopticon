
include ../Makefile.config

###
all:	regcovextract

clean:
	rm -f *.o
	rm -f regcovextract

###
### Production build targets
###
regcovextract: regcovextract.o
	$(CPP) $(CPPFLAGS) $(INCLUDE) -static -o regcovextract regcovextract.o \
		$(FEATURES_LIB) $(FEATURES_UTILITY_LIB) $(VIGRA_LIB) $(BOOST_LIB)

