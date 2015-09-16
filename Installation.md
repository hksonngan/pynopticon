# Building and Installing #

You have two options in downloading and installing Pynopticon:
  1. Using the [easy\_install script](http://peak.telecommunity.com/DevCenter/EasyInstall)
  1. Traditional download (see below)

## Windows ##
### Installation of the base package (no GUI) ###
  1. If not already installed, download and install Python 2.5.x available from [http://python.org](http://python.org/download/) (Python 2.6 is not yet supported)
  1. If not already installed, download and install the following dependencies: [numpy](http://numpy.scipy.org), [scipy](http://www.scipy.org) and [PIL](http://www.pythonware.com/products/pil/)
  1. Download the Pynopticon windows installer from the download section and start it.
  1. Since this will only install the libraries you may also want to install 'Orange' to get a GUI. For this, please follow the instructions "Additional installation of the GUI" below.

### Additional installation of the GUI ###

  1. Follow the steps from 'Basic install' for your OS
  1. Download and install the [Orange Toolbox](http://www.ailab.si/orange/) (make sure to use the Qt4 version daily-snapshot, **not** version 1.0) following the installation instructions from the Orange website.
  1. In order to make Orange find out about Pynopticon run the python script 'link\_to\_orange.py' from C:\python25\lib\site-packages\pynopticon (this copies the widgets directory from the Pynopticon base directory into the OrangeWidgets dir of Orange)
  1. Upon starting Orange there should be a new tab in the toolbar named 'Pynopticon'

## Linux ##

### Installation of the base package (no GUI) ###

  1. If not already installed, install Python 2.5 (available in your packet manager)
  1. Download Pynopticon from the download section.
  1. Unpack it.
  1. Run 'setup.py build' and 'setup.py install'.
  1. Since this will only install the libraries you may also want to install 'Orange' to get a GUI. For this, please follow the instructions "Additional installation of the GUI" below.

### Additional installation of the GUI ###

  1. Follow the steps from 'Basic install' for your OS
  1. Download and install the [Orange Toolbox](http://www.ailab.si/orange/) (make sure to use the Qt4 version daily-snapshot with extensions, **not** version 1.0) following the installation instructions from the Orange website (Orange is available for Windows and Linux).
  1. In order to make Orange find out about Pynopticon run the python script 'link\_to\_orange.py' from /usr/lib/python2.5/site-packages/pynopticon (this copies the widgets directory from the Pynopticon base directory into the OrangeWidgets dir of Orange)
  1. Upon starting Orange there should be a new tab in the toolbar named 'Pynopticon'

### (Additional) Compile additional feature extractors ###

Included in Pynopticon are feature extractors written by Sebastian Nowozin. They should compile fine under Linux (dependencies include [Vigra](http://kogs-www.informatik.uni-hamburg.de/~koethe/vigra/) and the [Boost C++ Libraries](http://www.boost.org/)).
  1. Change directory to pynopticon/src/featureLib
  1. Call make.sh
  1. When all dependencies are installed everything should compile fine.
  1. Copy the executable pynopticon/src/featureLib/regcovextract/regcovextract into the bin subdirectory of your pynopticon installation (Linux: /usr/lib/python2.5/site-packages/pynopticon, Windows: c:\Python2.5\).

(**If you manage to compile the source under windows please send me an e-mail with the binary!**)