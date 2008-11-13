.. toctree::
   :maxdepth: 2

**********************
Tutorials and examples
**********************

=======================================================================
Tutorial on using the GUI to build a quick object recognition pipeline.
=======================================================================

Make sure you have Pynopticon and Orange installed correctly and linked the two together (read the Installation instructions). For the theoretical background on what each step in the pipeline does read the Introduction.

    * From the toolbar choose the tab titled Pynopticon.
    * First, we need an input module to load some data to be processed - drag the widget ImageLoader onto the workspace.
    * Next, we want to choose which data we want our classifier to train on - double click on the new ImageLoader widget on the workspace.
    * For testing purposes lets choose a predefined dataset - click on the button Load Dataset in the ImageLoader widget.
    * Select the file called Caltech_small.xml and click on Open.
    * You can see two new categories, you can click on them and see the individual images, if you double click on them the image gets displayed.
    * Next we want to extract some features - drag the SIFT widget onto the workspace.
    * Since we want to extract the features from our dataset click and hold on the little square on the right of the ImageLoader widget. You can now connect the output of this widget to input of the SIFT widget by moving the line to the little square on the left of the SIFT widget.
    * Note that neither any images are loaded nor any computations are performed since the data is not yet needed anywhere.
    * As the next step we want to perform clustering - drag the K-Means widget onto the workspace.
    * Double click on the new K-Means widget - you can make several choices here, we want to increase the number of clusters a little, so set that parameter to 500. Normally, we do not need to cluster over all the data, so set the subsample parameter to 0.5 so that we use 50% of the feature descriptors.
    * Connect the SIFT widget to the K-Means widget.
    * In the next step we want to quantize the feature descriptors - draw the Quantize widget into the workplace.
    * This widget needs two inputs, the cluster centers (aka codebook) and the descriptors. Connect the K-Means and the SIFT widget to the Quantize widget.
    * Next pull the Histogram widget onto the workplace, double click and set the number of bins to the number of clusters (500).
    * Connect the Quantize widget to the Histogram widget.
    * We now have a complete feature extraction pipeline.
    * In order to train an Orange classifier we first have to convert the data to Orange's format. This is done by the SlotToExampleTable widget, pull it onto the workspace. This widget needs to inputs, the histograms from the Histogram widget and the labels of the data from the ImageLoader widget, connect them!
    * After you made the final connection the program should start computing because in order to create the Orange datatable we need all the data processed. This can take a while (depending on your input data) as there are a lot of expensive computations taking place so you can probably have a coffee. Note, that eventhough we have to compute features of every image, Pynopticon does only store one image at a time in memory.
    * After the data is computed you can now train a classifier, go to the Classifier tab and drag the Decision Tree widget onto the workspace and connect the SlotToExampleTable widget to the Decision Tree widget. The percentage bar above the classifier shows you that it is training.
    * In order to see how well you trained your classifier you can choose from the Evaluation tab the TestLearners widget and draw it onto the workspace. Connect the Decision Tree widget and the SlotToExampleTable to the TestLearners widget.
    * If you double click on the TestLearners widget you can see in the table on the right under C the percentage of correctly classified images.
    * Congratulations, you just trained your first object recognition classifier! 

===============================================
Example on how to use Pynopticon without a GUI.
===============================================

The complete feature extraction pipeline described in the Beginners section can also be realized without the GUI and built into your custom Python program. Here is an example program realizing all the steps from above (without the classification) that should be rather self explanatory if you read the above tutorial!

Taken from example.py::

    import pynopticon as pnc

    def examplePipeline():
        ##########################
	# Create different objects
	##########################

	# Create the ImageLoader object
	imgLoader = pnc.ImageDataset.ImageDataset()
	# Load a predefined dataset from an XML file
	imgLoader.loadFromXML("GarfieldBarrel.xml", demos=True)
	# Since we are finished with out dataset we call prepare()
	imgLoader.prepare()

	# Create a feature extractor (in this case the sift extractor using the Valedi implemenatation
	sift = pnc.features.SiftValedi()

	# Create a kmeans-cluster object and set numClusters=50 (50 cluster centroids)
	kmeans = pnc.cluster.Kmeans(numClusters=50)

	# Create a Quantization object
	quant = pnc.cluster.Quantize()

	# Create a Histogram object to bin the descriptors later on using 50 bins
	# (one for every cluster)
	histo = pnc.histogram.Histogram(bins=50)

	###############################
	# Connect the objects via slots
	###############################

	pnc.connect(imgLoader.outputSlotTrain, sift.inputSlot)
	pnc.connect(sift.outputSlot, kmeans.inputSlot)
	pnc.connect(sift.outputSlot, quant.inputSlotVec)
	pnc.connect(kmeans.outputSlot, quant.inputSlotCodebook)
	pnc.connect(quant.outputSlot, histo.inputSlot)

	# Get the histograms as a list of numpy arrays
	histograms = list(histo.outputSlot)

	# train classificator etc....

==========================================
Example on how to create your own modules.
==========================================

Creating your own modules to be used in the Pynopticon framework is quite simple. In general, you define input and output slots and your processing function. All the communication with the other widgets, connection handling and lazy evaluation is done in the background.

Additional user provided modules are highly welcome, so if you create a new module send it so that we can include it in the next release!

Here is an example program that defines an module which calls a process function on every input element::

    import pynopticon as pnc

    class exampleSlot(object):
	def __init__(self):
	    # For every slot we can define the type of data that is
	    # exepected or outputted, for more info have a look at
	    # slots.py

	    # Input is expected to be images in PIL format
	    inputType = pnc.slots.ImageType(format=["PIL"], color_space=["gray"])
	    # Output is a flat array (a 2D array consisting of vectors)
	    outputType = pnc.slots.VectorType(name='Example', shape='flatarray')

	    # Next we have to define an input and an output slot which
	    # will handle the data sending and receiving
	    self.inputSlot = pnc.slots.InputSlot(name='Images',
						 acceptsType = inputType)

	    # We have several options of defining an output slot (see the
	    # help for slots.OutputSlots for more infos).  Here, we create
	    # an output slot that receives data from our just defined
	    # inputSlot and calls the function self.process() on every
	    # element.  The reason we are using pnc.weakmethod(class,
	    # method) instead of handing self.process directly is purely
	    # technical.
	    self.outputSlot = pnc.slots.OutputSlot(name='Example',
						   inputSlot = self.inputSlot,
						   processFunc = pnc.weakmethod(self, 'process'),
						   outputType = outputType)

	def process(self, img):
	    descr = do_funky_computations(img)
	    return descr
