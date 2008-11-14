#    Pynopticon is a python object recognition framework using a bag of feature approach.
#    
#    Copyright (C) 2008  Thomas V. Wiecki
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import platform

# Seems to be needed, otherwise mpi_kmeans is not compiled with g++
import distutils.sysconfig
distutils.sysconfig.get_config_var('LIBS')
distutils.sysconfig.get_config_var('SYSLIBS')
import os; os.environ['CC'] = 'gcc'; os.environ['CXX'] = 'g++';
os.environ['CPP'] = 'g++'

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Extension

try:
    import numpy
except:
    print "You need to have numpy installed."
    
import glob

destDir="orange/add-ons/Pynopticon"

siftModule = Extension('_sift',
		       language = 'c',
		       sources = glob.glob('src/vlfeat/vl/*.c') + ['src/vlfeat/python/sift.c'],
		       extra_compile_args=['-pedantic', '-O3' ,'-Wno-unused-function', '-Wno-long-long', '-D__LITTLE_ENDIAN__'],
		       include_dirs = [numpy.get_include(), 'src/vlfeat'],
		       extra_link_args = ['-lm'])

kmeansModule = Extension('_mpi_kmeans',
			 language = 'c++',
			 include_dirs = [numpy.get_include()],
			 sources = ['src/mpi_kmeans/mpi_kmeans.cxx', 'src/mpi_kmeans/_mpi_kmeans.cxx'],
			 extra_compile_args=['-O3'],
			 extra_link_args = ['-lm','-lstdc++'],
			 libraries=['stdc++'])

libkmeansModule = Extension('libmpikmeans',
               language = 'c',
               sources = ['src/mpi_kmeans/mpi_kmeans.cxx'],
               extra_compile_args=['-Wl,-soname=libmpikmeans.so','-O3'])


chi2Module = Extension('libchi1',
                       language = 'c',
                       sources = ['src/mpi-chi2/chi2float.c','src/mpi-chi2/chi2double.c'],
                       include_dirs = ['src/mpi-chi2'],
                       extra_compile_args=['-D__MAIN__','-ffast-math','-fomit-frame-pointer','-O3','-march=nocona'],
                       extra_link_args = ['-shared','-O3', '-march=nocona', '-ffast-math', '-Wl,-soname=libchi2.so'])

setup (name = 'pynopticon',
       version = '0.1',
       description = 'Pynopticon is an object recognition framework written in python using a bag of feature approach.',
       author = 'Thomas V. Wiecki',
       author_email = 'thomas.wiecki@gmail.com',
       url = 'http://code.google.com/p/pynopticon/',
       long_description = '''Pynopticon is a toolbox that lets you create and train your own object
			     recognition classifiers. It makes rapid prototyping of object
			     recognition work flows a snap. Simply create a dataset of your
			     favorite image categories, choose some feature extraction methods
			     (e.g. SIFT), post-processing (clustering, histograms, normalization)
			     and a classifier to train (e.g. SVM, Bayes, Descision Trees) and leave
			     the rest to Pynopticon. Pynopticon builds upon the well designed
			     orange toolbox for machine learning and thus comes with a full
			     featured and user friendly GUI. Special care has been taken to let the
			     user decide if he wants to have a lower memory footprint or a be
			     computationally more efficient. All this makes Pynopticon a perfect
			     tool for lectures and their students, beginners in object recognition
			     but also computer vision researches who want to try out an idea
			     without having to write a complex program.''',
       ext_modules = [siftModule, kmeansModule], #, chi2Module], ToDo
       packages = ['pynopticon', 'pynopticon.widgets', 'pynopticon.tests'],
       package_dir={'': 'src'},
       include_package_data = True,
       dependency_links = ['http://www.pythonware.com/products/pil/'],
       install_requires=['setuptools', 'numpy', 'scipy', 'PIL'], #, 'arpack'],
       extras = {'normalizing' : ['arpack']},
       test_suite = "pynopticon.tests.test_all",
       #extra_path=("orange-pynopticon", destDir),
       zip_safe = False
       )

