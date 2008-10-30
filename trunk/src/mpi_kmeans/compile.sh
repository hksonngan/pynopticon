cython mpi_kmeans_cy.pyx
g++ -g -pthread -fPIC -I/usr/include/python2.5 -I/usr/lib/python2.5/site-packages/numpy/core/include -c mpi_kmeans_cy.c
g++ -g -Wall -fPIC -O3 -pthread -c mpi_kmeans.cxx
g++ -g -Wl -lc -pthread -shared -pthread -fPIC -fwrapv -O2 -Wall -lpython2.5 mpi_kmeans_cy.o mpi_kmeans.o -o mpi_kmeans_cy.so
