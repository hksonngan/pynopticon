import itertools
import pynopticon
import weakref

class Slots(object):
    """Stores multiple (Input or Output)Slots.
    Each slot can be accessed by its name. Slots['name']."""
    def __init__(self, slots = None):
        self.slots = set(slots)
    
    def __getitem__(self, item):
        for i in self.slots:
            if i.name == item:
                return i
        # Not found
        raise AttributeError, "Slot not found"

    def add(self, slot):
        self.slots.add(slot)
        

class InputSlot(object):
    """Defines an input slot for a module. One output slot can attach
    to an input slot (by calling inputslot.registerInput(senderslot).

    InputSlot(name, senderSlot=None, acceptsType=None,
              bulk=False, useLazyEvaluation=pynopticon.useLazyEvaluation)

    name:         name of the slot, can be any string
    senderSlot:   optional, registers senderSlot
    acceptsType:  optional, a pynopticon.datatype object, if not supplied
                  all types will be accepted.
    bulk:         optional, converts (if necessary) the whole input at
                  once instead of sequentially.
    useLazyEvaluation: optional
    
    """
    def __init__(self, name, senderSlot=None, acceptsType=None, bulk=False, useLazyEvaluation=pynopticon.useLazyEvaluation):
        self.name = name
        self.acceptsType = acceptsType
        self.container = None
        self.converters = None
        self.bulk = bulk
        self.useLazyEvaluation = useLazyEvaluation
        self.senderSlot = None
        self.outputType = None
        
        if senderSlot is not None:
            self.registerInput(senderSlot)
        
    def __iter__(self):
        if not self.senderSlot:
            raise AttributeError, "No senderSlot registered!"
        return iter(self.container)

    def convertSequential(self):
        for item in self.senderSlot().container:
            if self.converters is not None: # self.converts contains functions
                if len(self.converters) > 0:
                    for converter in self.converters:
                        item = converter(item)
            yield item

    def convertBulk(self):
        # Get all input data
        bunch = list(self.senderSlot().container)
        # Convert using the functions in self.converters
        if self.converters is not None:
            if len(self.converters) > 0:
                for converter in self.converters:
                    bunch = converter(bunch)

        for i in bunch:
            yield i
            
    def registerInput(self, senderSlot):
        """Register senderSlot as an inputSlot. inputType and
        outputType have to match (or be convertable).
        """
        if pynopticon.useTypeChecking and self.acceptsType is not None:
            if senderSlot.outputType is not None:
                senderType = senderSlot.outputType
            elif senderSlot.inputSlot.outputType is not None:
                # If the output slot does not transform the input
                # type, it may be found in the inputslot
                senderType = senderSlot.inputSlot.outputType
            else:
                raise ValueError, "No types specified"
            # Check if sender type is compatible with us or if we can
            # convert (compatible() will return converter functions)
            compatible = self.acceptsType.compatible(senderType)
            if compatible == False:
                raise TypeError, "Slots are not compatible"
            # Else compatible() returns the new type and conversion funcs
            (self.outputType, self.converters) = compatible
            

        # Register the new slot
        self.senderSlot = weakref.ref(senderSlot)
    
        # Callback to tell the senderSlot container to update its data
        # (if necessary)
        # senderSlot.container.recompute()

        if pynopticon.useCaching:
            # Register us to the senderSlot
            senderSlot.container.registerReference(self)

        # Initialize the container to store the data (or the reference to it)
        if not self.bulk:
            self.container = SeqContainer(generator=pynopticon.weakmethod(self, 'convertSequential'), useLazyEvaluation=self.useLazyEvaluation)
        else:
            self.container = SeqContainer(generator=pynopticon.weakmethod(self, 'convertBulk'), useLazyEvaluation=self.useLazyEvaluation)

        
class MultiInputSlot(InputSlot):
    """Defines an input slot that can receive multiple connections"""
    def __init__(self, name, senderSlot=None, acceptsType=None, bulk=False, useLazyEvaluation=pynopticon.useLazyEvaluation):
        self.name = name
        
        if acceptsType:
            raise NotImplementedError, "Converting is not supported for MultiInputSlots"
        self.acceptsType = None
        
        self.container = None
        self.converters = None
        self.bulk = bulk
        self.useLazyEvaluation = useLazyEvaluation

        # Temporary storage of senderSlot
        self.senderSlot = None
        
        # We keep weakrefs for all connected inputs
        self.senderSlots = weakref.WeakValueDictionary()

        self.iterPool = []
        
        self.outputType = None
        
    def __iter__(self):
        return self

    def next(self):
        # Get iterators if necessary
        if len(self.iterPool) == 0:
            for sender in self.senderSlots.itervalues():
                self.iterPool.append(iter(sender))
                
        data = []

        # Pool one item from every slot
        for iterator in self.iterPool:
            try:
                data.append(iterator.next())
            except StopIteration:
                # Reset iterPool
                self.iterPool = []
                raise StopIteration
        
        # Return list of pooled elements
        return data

    
    def registerInput(self, senderSlot, senderID=None):
        """Register one input"""
        # Call parent to handle all connecting of one single slot
        super(MultiInputSlot, self).registerInput(senderSlot)

        if not senderID:
            senderID = id(senderSlot)
            
        # All variables are now set, we now store them in the weakValueDict
        # because the local variables will be overwritten when the next slot connects.
        self.senderSlots[senderID] = senderSlot

        # Make sure noone uses those variables
        self.senderSlot = None
        self.container = None
        self.outputType = None
        self.converters = None
        
class OutputSlot(object):
    """Defines an output slot which receives data, computes and sends data.
    It is highly configurable. In essence, there are three ways to
    define a valid OutputSlot:
    
    1. provide an inputSlot to read from AND one processFunc (or
    multiple processFuncs) to get called AND a slotType ('sequential'
    or 'bulk') to define if the processFunc(s) should be called for
    each single element from inputSlot (i.e. 'sequential') or if
    processFunc(s) should get called once with all data from
    inputSlot (i.e. 'bulk')

    2. provide an iterator function (you have to specify the input and
    computing yourself) - to be used if you need data from multiple
    inputSlots or if generate data without input.

    3. provide a sequence - can be any iterable.
    """
    def __init__(self, name, inputSlot=None, processFunc=None,
                 outputType=None, slotType=None, iterator=None, sequence=None, classes=None,
                 useLazyEvaluation=pynopticon.useLazyEvaluation, useCaching=pynopticon.useCaching):

        self.name = name
        self.inputSlot = inputSlot
        self.outputType = outputType
        self.iterator = iterator
        self.sequence = sequence
        self.processFunc = processFunc

        # Create an output container
        if self.sequence is not None:
            self.container = SeqContainer(sequence=self.sequence, classes=classes, useLazyEvaluation=useLazyEvaluation, useCaching=useCaching)
        elif self.iterator is not None: # User defined iterator
            self.container = SeqContainer(generator=self.iterator, classes=classes, useLazyEvaluation=useLazyEvaluation, useCaching=useCaching)
        elif slotType == 'sequential': # Sequential iterator
            if self.processFunc is None and self.processFuncs is None:
                raise AttributeError, "You must provide processFunc or processFuncs to use generic iterators"
            self.container = SeqContainer(generator=pynopticon.weakmethod(self, 'seqIterator'), classes=classes, useLazyEvaluation=useLazyEvaluation, useCaching=useCaching)
        elif slotType == 'bulk': # Bulk iterator
            if self.processFunc is None and self.processFuncs is None:
                raise AttributeError, "You must provide processFunc or processFuncs to use generic iterators"
            self.container = SeqContainer(generator=pynopticon.weakmethod(self, 'bulkIterator'), classes=classes, useLazyEvaluation=useLazyEvaluation, useCaching=useCaching)
        else:
            self.container = None
            
    def __iter__(self):
        if not self.container:
            raise AttributeError, "self.container is not set"
        return iter(self.container)
    
    def seqIterator(self):
        """Generator which iterates over the input elements, calling
        processFuncs and yields the processed element, one at a time.
        """
        for item in self.inputSlot.container:
            if pynopticon.useOrange:
                from PyQt4.QtGui import qApp
                qApp.processEvents()
            item = self.processFunc(item)
            yield item
            

    def bulkIterator(self):
        """Generator which iteratates over the input elements, saves them
        and calls the processFuncs on the complete input data.
        (e.g. clustering, normalization). """
        inData = list(self.inputSlot.container)

        outData = self.processFunc(inData)
            
        for item in outData:
            yield item
 

class SeqContainer(object):
    """Central class to store sequential data. It has basic
    list properties with some additional features:
    - Instead of a list, a generator function (NOT the called
    generator function) can be used, it will only get called and
    evaluated when the data is really needed (i.e. lazy evaluation).
    - Once data has been pooled from SeqContainer it will be reset
    so it is possible to iterate multiple times over the same
    SeqContainer.
    - You can have multiple references iterating over SeqContainer as
    every reference will receive its own iterator.
    """
    def __init__(self, sequence=None, generator=None, classes=None, useLazyEvaluation=pynopticon.useLazyEvaluation, useCaching=pynopticon.useCaching):
        self.sequence = sequence
        self.generator = generator
        self.data = None
        self.useLazyEvaluation = useLazyEvaluation
        self.useCaching = useCaching
        self.classes = classes

        self.references = weakref.WeakValueDictionary()    # Registered objects with appropriate group ID
        self.iterpool = []     # For storing the iterators of each
                               # group until every group member
                               # received it

    def recompute(self):
        """Update computed data"""
        if not self.useLazyEvaluation:
            # Input changed and we have to update our data, set
            # self.data to none so the next time getDataAsIter() gets
            # called the data will be recomputed
            print "RECOMPUTE"
            self.data = None
            
    def getDataAsIter(self):
        """Return the stored data in a way it can be passed to iter()."""
        if self.generator is not None and self.sequence is None:
            # Input type is a generator function
            if self.useLazyEvaluation:
                return(self.generator()) # Call the generator
            else:
                if self.data is not None:
                    # Data already computed, return
                    return (self.data)
                else:
                    # Compute data from generator and save it
                    generator = self.generator()
                    self.data = list(generator)
                    return (self.data)

        elif self.sequence is not None and self.generator is None:
            if self.useLazyEvaluation:
                # Makes no sense to use generator here
                self.useLazyEvaluation = False
            return(self.sequence)
        else:
            raise ValueError, "generator AND sequence given"

    def __iter__(self):
        if len(self.references) <= 1:
            return iter(self.getDataAsIter())

        if len(self.iterpool) == 0:
            # Create a pool of cached iterators
            self.iterpool = list(itertools.tee(self.getDataAsIter(), len(self.references)))

        # Hand one cached iterator to the group member.
        return self.iterpool.pop()
    
    def registerReference(self, obj):
        """Register an object. Registered objects receive cached
        iterators (for more details see the description of the
        SeqContainer class)"""
        if self.useCaching:
            self.references[id(obj)] = obj


class BaseType(object):
    def __init__(self, **kwargs):
        self.dataType = kwargs
        self.attributes = {}
        self.conversions = {}
        
    def __iter__(self):
        return iter(self.dataType)

    def __getitem__(self, item):
        return self.dataType[item]

    def __setitem__(self, item, value):
        self.dataType[item] = value
        
    def compatible(self, inputType):
        """Check if toType is compatible with my own type. If it is
        not compatible, try find fitting conversion functions.

        Output: False or (type, [conversionfuncs])"""

        
        if inputType.__class__ is not self.__class__:
            return False

        import copy
        # Copy inputType
        toType = copy.deepcopy(inputType)

        compatible = True
        convert = True
        
        for key in toType:
            # If key is not present, we assume compatibility
            if key not in self.dataType:
                continue

            if toType[key] in self.dataType[key]:
                continue # Compatible

            compatible = False

        if compatible:
            return (toType, [])

        # Can we convert?
        for conversion in self.conversions:
            for key in conversion:
                if key == 'function':
                    continue
                for inType in self.dataType[key]:
                    if toType[key] != inType:
                        if conversion[key][0] != toType[key] and conversion[key][1] != inType:
                            convert = False

                if convert:
                    toType[key] = conversion[key][1]
                    return (toType, [conversion['function']])
                

        # No
        return False
            
        
class ImageType(BaseType):
    from PIL import Image
    from numpy import array
    
    def __init__(self, **kwargs):
        super(ImageType, self).__init__(**kwargs)
        
        self.attributes = {'format': ['PIL', 'numpy'],
                          'color_space': ['gray', 'RGB']
                           }

        self.conversions = [{'format': ('PIL', 'PIL'),
                             'color_space': ('RGB', 'gray'),
                             'function': pynopticon.weakmethod(self, 'convert_PIL_RGB_to_PIL_gray')},
                            {'format': ('PIL', 'numpy'),
                             'color_space': ('RGB', 'RGB'),
                             'function': pynopticon.weakmethod(self, 'convert_PIL_RGB_to_numpy_RGB')},
                            {'format': ('PIL', 'numpy'),
                             'color_space': ('RGB', 'gray'),
                             'function': pynopticon.weakmethod(self, 'convert_PIL_RGB_to_numpy_gray')}
                            ]
                            
    
    def convert_PIL_RGB_to_PIL_gray(self, image):
        if pynopticon.verbosity>0:
            print "Converting RGB image to gray color space"
        image = image.convert('L')
        return image

    def convert_PIL_RGB_to_numpy_RGB(self, image):
        return array(image)

    def convert_PIL_RGB_to_numpy_gray(self, image):
        return array(self.convert_PIL_RGB_to_PIL_gray(image))

class VectorType(BaseType):
    def __init__(self, **kwargs):
        super(VectorType, self).__init__(**kwargs)

        self.attributes = {'shape': ['nestedlist', 'nestedarray', 'flatarray', 'flatlist'],
                           'length': [type(1)]
                           }

        self.conversions = [{'shape': ('nestedlist', 'flatarray'),
                             'function': pynopticon.weakmethod(self, 'convert_nestedlist_to_flatarray')},
                            {'shape': ('nestedarray', 'flatarray'),
                             'function': pynopticon.weakmethod(self, 'convert_nestedlist_to_flatarray')}
                            ]

    def convert_nestedlist_to_flatarray(self, lst):
        from numpy import concatenate
        if pynopticon.verbosity>0:
            print "Concatenating..."
        x=concatenate(lst)
        print x.shape
        return x
