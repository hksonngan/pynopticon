import sys
import os
import platform

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Extension

try:
    import numpy
    import scipy
    import PIL
except:
    print "You need to have numpy, scipy and PIL installed."
    
import glob

siftModule = Extension('_sift',
		       language = 'c++',
		       sources = glob.glob('src/vlfeat/vl/*.c') + ['src/vlfeat/python/sift.c'],
		       extra_compile_args=['-pedantic', '-std=c89', '-O3' ,'-Wno-unused-function', '-Wno-long-long', '-D__LITTLE_ENDIAN__', '-std=c99'],
		       include_dirs = [numpy.get_include(), 'src/vlfeat'],
		       extra_link_args = ['-lm'])

kmeansModule = Extension('libmpikmeans',
		       language = 'c++',
		       sources = ['src/mpi_kmeans/mpi_kmeans.cxx'],
		       extra_compile_args=['-Wl,-soname=libmpikmeans.so','-O3'])

chi2Module = Extension('libchi2',
                       language = 'c',
                       sources = ['src/mpi-chi2/chi2float.c','src/mpi-chi2/chi2double.c'],
                       include_dirs = ['src/mpi-chi2'],
                       extra_compile_args=['-D__MAIN__','-ffast-math','-fomit-frame-pointer','-O3','-march=nocona'],
                       extra_link_args = ['-shared','-O3', '-march=nocona', '-ffast-math', '-Wl,-soname=libchi2.so'])

setup (name = 'pynopticon',
       version = '0.1',
       description = 'Object Recognition Toolkit for Orange',
       author = 'Thomas V. Wiecki',
       author_email = 'thomas.wiecki@gmail.com',
       url = 'http://www.python.org/doc/current/ext/building.html',
       long_description = '''...''',
       ext_modules = [siftModule, kmeansModule], #, chi2Module], ToDo
       packages = ['pynopticon', 'pynopticon.orngWidgets', 'pynopticon.tests'],
       package_dir={'': 'src'},
       include_package_data = True,
       dependency_links = ['http://www.pythonware.com/products/pil/'],
       install_requires=['setuptools', 'numpy', 'scipy', 'PIL'],#, 'arpack'],
       test_suite = "pynopticon.tests.test_all",
       zip_safe = False
       )

