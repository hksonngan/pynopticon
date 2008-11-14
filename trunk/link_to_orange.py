import os.path
import shutil

try:
    import OWGUI
except ImportError:
    print "Orange could not be imported."

try:
    import pynopticon
except ImportError:
    print "Pynopticon could not be imported, you need to install it first."

def link_to_orange():
    
    
    orangeWidgetsPath = os.path.join(os.path.split(OWGUI.__file__)[0], 'Pynopticon')
    pncWidgetsPath = os.path.join(pynopticon.__path__[0], 'widgets')
    print "Copying pynopticon widgets to orange widgets directory..."
    shutil.copytree(pncWidgetsPath, orangeWidgetsPath)

    print "Successfull"

    

if __name__=='__main__':
    link_to_orange()
