## Introduction ##
Pynopticon allows you to do object recognition (finding out if there is a certain object anywhere on an image) following a Bag of Features (BoF) approach. This approach is well established in the computer vision community, yields good overall results and is applicable to a wide range of object recognition problems.

### Bag of Features approach ###

The BoF approach works in essence by extracting various features from an image. Commonly used features are either global (e.g. Color Histograms on the whole image) or local (e.g. extracting Regions of Interest (RoI) and transforming them (one example of this approach is SIFT - Scale Invariant Feature Transform)).

In the next step these features can be clustered according to their similarity given the assumption that classes of features provide information about the contents of an image. For example when classifying images of animals one might extract many local features with just eyes on them, all these eyes are then grouped together during the clustering. So the next time you present(nich ganz gluecklich, aber der ganze satz war vorher murksig) an image with lots of features that lie in the eye category, the algorithm is very likely to assume there's an animal in the picture. Looking up in what cluster a feature lies is called 'quantization'. Counting how many features lie in a certain cluster results in a histogram. In sum, the result of all this processing is one histogram per image.

The next step in the object recognition pipeline is to train a classifier that detects which histogram pattern is likely to belong to a certain object category. Training this classifier can now be done with standard and well established machine learning algorithms, like a Support Vector Machine (SVM) or a Decision Tree.

### Motivation ###

The motivation for the development of Pynopticon is to make object recognition more accesible. During a university project I trained a classifier using the BoF approach and was suprised by how standardized it was, yet, how difficult it was to code all the individual steps and how they interact. To spare you duplicating this effort I wrote Pynopticon.

### Design Principles ###
Pynopticon consists of many individual modules which you can stick together in any sensible way you like; this makes it possible to create the object recognition pipeline which works best for your task.

Because working with large databases of images can use an excessive amount of memory, Pynopticon was designed with memory efficiency in mind. By using functional programming paradigms data is only stored in memory and computed when it is really needed. However, the user can also choose to save the computed data so that later on when you want to try out a few (new) things nothing has to be recomputed.

To make Pynopticon more accessible you can use it in combination with the excellent Orange Toolbox (http://www.ailab.si/orange/) which provides a sophisticated GUI, lots of machine learning algorithms and nice visualization features.

# Screenshot #
![http://pynopticon.googlecode.com/svn/wiki/screenshot.png](http://pynopticon.googlecode.com/svn/wiki/screenshot.png)

# Acknowlegdements #
The project was financially supported by the [Karl-Steinbuch-Stipendium](http://www.karl-steinbuch-stipendium.de/) awarded to Thomas Wiecki from the [MFG-Stiftung Baden-Württemberg](http://www.mfg.de/).

Thanks for ideas, support and/or beta-testing:
Bernhard Schölkopf, Matthias Bethge, Sebastian Nowozin, Christoph Lampert, Benedikt Janus and Andreas Dietzel. Thanks to Gregor Leblan of the Orange team for lots of help with their toolbox.