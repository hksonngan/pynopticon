.. toctree::
   :maxdepth: 2


***********************
Building and Installing
***********************

You have two options in downloading and installing Pynopticon. Your first choice should be to use easy_install, the alternative way is the traditional download.

============================================
Basic installation (Windows + Linux, no GUI)
============================================

  #. If not already installed, install Python 2.5 (available in your packet manager (Linux) or under [http://python.org/download/ http://python.org/download/])
  #. Download Pynopticon from the download section.
  #. Unpack it.
  #. Run 'setup.py build' and 'setup.py install'.

====================================
Installing the GUI (Windows + Linux)
====================================

  #. Follow the steps from 'Basic install'
  #. Download and install the [http://www.ailab.si/orange/ Orange Toolbox] (make sure to use the Qt4 version from the snapshot, *not* version 1.0) following the installation instructions from the Orange website.
  #. Create a (symbolic) link from the pynopticon/orngWidgets directory to orange/OrangeWidgets/Pynopticon
  #. When you then start Orange there should be a new tab in the toolbar named 'Pynopticon'

==================================================
(Additional) Compile additional feature extractors
==================================================

Included in Pynopticon are feature extractors written by Sebastian
Nowozin. They should compile fine under Linux (dependencies include
[http://kogs-www.informatik.uni-hamburg.de/~koethe/vigra/ Vigra] and
the [http://www.boost.org/ Boost C++ Libraries]). 

  #. Change directory to pynopticon/src/featureLib
  #. Call make.sh
  #. When all dependencies are installed everything should compile fine.
  #. Copy the executable pynopticon/src/featureLib/regcovextract/regcovextract into the bin subdirectory of your pynopticon installation (Linux: /usr/lib/python2.5/site-packages/pynopticon, Windows: c:\Python2.5\).

(*If you manage to compile the source under windows please send me an e-mail with the binary!*)
