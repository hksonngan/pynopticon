# Tutorial on using the GUI to build a quick object recognition pipeline. #

Make sure you have Pynopticon and Orange installed correctly and linked together properly (read the [Installation](Installation.md) instructions). For the theoretical background on what each step in the pipeline does read the [Introduction](Introduction.md).

  * From the toolbar choose the tab titled _Pynopticon_.
  * First, we need an input module to load some data to be processed - drag the widget _ImageLoader_ onto the workspace.
  * Next, we want to choose which data we want our classifier to train on - double click on the new _ImageLoader_ widget on the workspace.
  * For testing purposes lets choose a predefined dataset - click on the button _Load Dataset_ in the _ImageLoader_ widget.
  * Select the file called _GarfieldBarrel.xml_ and click on _Open_.
  * You can see two new categories, you can click on them and see the individual images, if you double click on them the image gets displayed.
  * Click on the apply button in the _ImageLoader_ widget. _Note that you have to press apply every time you (re)load your scheme._
  * Next we want to extract some features - drag the _SIFT_ widget onto the workspace.
  * Since we want to extract the features from our dataset click and hold on the little square on the right of the _ImageLoader_ widget. You can now connect the output of this widget to input of the _SIFT_ widget by dragging the line to the little square on the left of the _SIFT_ widget.
  * Note that Pynopticon is not doing anything yet, no images are loaded nor any computations performed. This is because of the lazy evaluation technique which ensures that computations and loading only happen once the data is actually needed (like when training a classifier).
  * Our next step is to perform a clustering of the many features - drag the _K-Means_ widget onto the workspace.
  * Double click on the new _K-Means_ widget - you can make several choices here, we want to increase the number of clusters a little, so set that parameter to 50.
  * Connect the _SIFT_ widget to the _K-Means_ widget.
  * In the next step we want to quantize the feature descriptors - draw the _Quantize_ widget into the workplace.
  * This widget needs two inputs, the cluster centers (aka codebook) and the descriptors. Connect the _K-Means_ and the _SIFT_ widget to the _Quantize_ widget.
  * Next pull the _Histogram_ widget onto the workplace, double click and set the number of bins to the number of clusters (50).
  * Connect the _Quantize_ widget to the _Histogram_ widget.
  * We now have a complete feature extraction pipeline.
  * In order to train an Orange classifier we first have to convert the data to Orange's format. This is done by the _SlotToExampleTable_ widget, pull it onto the workspace. This widget needs two inputs, the histograms from the _Histogram_ widget and the labels of the data from the _ImageLoader_ widget, connect them!
  * After you made the final connection the program should start computing because in order to create the Orange datatable we need all the data to be processed. This can take a while as there are a lot of expensive computations performed so this is probably a good time for you to have a cup of coffee. Note, that even though we have to compute features of **every** image, Pynopticon does only store one image at a time in memory (i.e. lazy evaluation).
  * After the data is computed you can now train a classifier, go to the _Classifier_ tab and drag the _SVM_ widget onto the workspace and connect the _SlotToExampleTable_ widget to the _SVM_ widget. The percentage bar above the classifier shows you that it is training.
  * In order to see how well you trained your classifier you can choose from the _Evaluation_ tab the _TestLearners_ widget and draw it onto the workspace. Connect the _SVM_ widget and the _SlotToExampleTable_ to the _TestLearners_ widget.
  * If you double click on the _TestLearners_ widget you can see in the table on the right under C the percentage of correctly classified images, it should be somewhere around 90%.
  * Congratulations, you just trained your first object recognition classifier!


# Example on how to use Pynopticon without a GUI. #

The complete feature extraction pipeline described in the _Beginners_ section can also be realized without the GUI and built into your custom Python program. Here is an example program realizing all the steps from above (without the classification) that should be rather self explanatory if you read the above tutorial!

Taken from example.py:
```
def examplePipeline():
    ###############################################
    # Create an object for every step of the procedure
    ###############################################

    # Create the ImageLoader object
    imgLoader = pnc.ImageDataset.ImageDataset()
    # Load the images (here, we use a predefined dataset from an xml-file)
    imgLoader.loadFromXML("GarfieldBarrel.xml", demos=True)
    # Loading complete - prepare the ImageLoader for further steps
    imgLoader.prepare()

    # Create the feature extractor object 
    #(in this case the sift extractor,  using the valedi implementation)
    sift = pnc.features.SiftValedi()

    # Create a k-means-cluster object with 50 clusters 
    kmeans = pnc.cluster.Kmeans(numClusters=50)

    # Create a quantization object
    quant = pnc.cluster.Quantize()

    # Create a histogram object to bin the descriptors into 50 bins (one for every cluster)
    histo = pnc.histogram.Histogram(bins=50)

    ###############################################
    # Connect the objects via slots
    ###############################################
    pnc.connect(imgLoader.outputSlotTrain, sift.inputSlot)
    pnc.connect(sift.outputSlot, kmeans.inputSlot)
    pnc.connect(sift.outputSlot, quant.inputSlotVec)
    pnc.connect(kmeans.outputSlot, quant.inputSlotCodebook)
    pnc.connect(quant.outputSlot, histo.inputSlot)

    ###############################################
    # Get the histograms as a list of numpy arrays
    ###############################################
    histograms = list(histo.outputSlot)

    # train classificator etc....

```

# For Developers - Example on how to create your own modules. #

Creating your own modules to be used in the Pynopticon framework is quite simple. In general, you define input and output slots and your processing function. All the communication with the other widgets, connection handling and lazy evaluation is done in the background.

**Additional user provided modules are highly welcome, so if you create a new module send it in so we can include it in the next release!**

Here is an example program that defines an module which calls a process function on every input element:

```
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

```