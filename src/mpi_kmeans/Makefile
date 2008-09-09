#
# choose between intel compiler and gcc 
# 
#CC = gcc-4.1
#CFLAGS=-O3 -ffast-math -fomit-frame-pointer -fPIC -mtune=k8 -march=k8

CC=gcc

#CFLAGS= -xP -fast -DCOMPILE_WITH_ICC
CFLAGS=-03
VERBOSEFLAG=-DKMEANS_VERBOSE

#MATLABDIR=/agbs/share/sw/matlab

#TARGETS=mpi_kmeans
#LIBS=-lm -lmex
INCLUDES=-I$(MATLABDIR)/extern/include

# 32 bit version
#SUFFIX=mexglx
#LDIRS=-L$(MATLABDIR)/bin/glnx86 

# 64 bit version
#SUFFIX=mexa64
#LDIRS=-L$(MATLABDIR)/bin/glnxa64

all: $(TARGETS:%=%.$(SUFFIX))

mpi_kmeans.o: mpi_kmeans.cxx mpi_kmeans.h
	$(CC) $(CFLAGS)  -c -o mpi_kmeans.o mpi_kmeans.cxx

%.o:	%.cxx
	$(CC) $(CFLAGS) $(INCLUDES) $(VERBOSEFLAG) -c -o $@ $*.cxx

mpi_kmeans_ordinary.$(SUFFIX): mpi_kmeans_ordinary.o
	$(CC) mpi_kmeans_ordinary.o $(LDIRS) $(LIBS) -shared -o mpi_kmeans_ordinary.$(SUFFIX) 

%.$(SUFFIX):	mpi_kmeans.o %.o
	$(CC) $*.o $(LDIRS) $(LIBS) -shared -o $*.$(SUFFIX) mpi_kmeans.o


### Targets

clean:	
	rm -f *.mexglx *.mexa64 *.o *~ *.so

shared:	mpi_kmeans.cxx mpi_kmeans.h
	g++ -shared -Wl,-soname=libmpikmeans.so -fPIC -O3 -Wall -o libmpikmeans.so mpi_kmeans.cxx

