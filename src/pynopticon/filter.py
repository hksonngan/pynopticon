import pynopticon
import pynopticon.slots
from PIL import ImageFilter

class Filter(object):
    def __init__(self, filter=None, useLazyEvaluation=pynopticon.useLazyEvaluation):

	self.filters = {'blur': ImageFilter.BLUR,
			'contour': ImageFilter.CONTOUR,
			'detail': ImageFilter.DETAIL,
			'edge_enhance': ImageFilter.EDGE_ENHANCE,
			'edge_enhance_more': ImageFilter.EDGE_ENHANCE_MORE,
			'emboss': ImageFilter.EMBOSS,
			'find_edges': ImageFilter.FIND_EDGES,
			'sharpen': ImageFilter.SHARPEN,
			'smooth': ImageFilter.SMOOTH,
			'smooth_more': ImageFilter.SMOOTH_MORE,
                        'none': None}
			   
        self.useLazyEvaluation = useLazyEvaluation

	# Define types
	inputType = pynopticon.slots.ImageType(format=["PIL"])

	# Define slots
	self.inputSlot = pynopticon.slots.InputSlot(name='Images', acceptsType = inputType, useLazyEvaluation=useLazyEvaluation)
	self.outputSlot = pynopticon.slots.OutputSlot(name='Filtered Images',
                                                 inputSlot=self.inputSlot,
                                                 processFunc=pynopticon.weakmethod(self, 'applyfilter'),
                                                 slotType='sequential',
                                                 useLazyEvaluation=self.useLazyEvaluation)
	self.filter = filter

	
    def applyfilter(self, img):
	if pynopticon.verbosity > 0:
	    print "Applying filter %s..." % self.filter
        if self.filter == 'none':
            return img
	return img.filter(self.filters[self.filter])

        
