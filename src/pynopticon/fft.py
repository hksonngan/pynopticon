import pynopticon
import pynopticon.transforms
import pynopticon.ImageDataset

imgDataset = pynopticon.ImageDataset.ImageDataset()
imgDataset.loadFromXML('PNAS.xml')
imgDataset.prepare()

fft = pynopticon.transforms.Fft2()

avg = pynopticon.transforms.Average()

fft.inputSlot.registerInput(imgDataset.outputSlotTrain)
#pynopticon.saveSlots('fft.pickle', fft.outputSlot)
#fft = pynopticon.loadSlots('fft.pickle')


avg.inputSlotLabels.registerInput(imgDataset.outputSlotLabelsTrain)
avg.inputSlotData.registerInput(fft.outputSlot)

list(avg.outputSlot)
