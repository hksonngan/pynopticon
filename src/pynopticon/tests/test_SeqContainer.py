import unittest
from pynopticon.slots import SeqContainer
import pynopticon

class TestSeqContainer(unittest.TestCase):
#     def testInvalidInput(self):
#         self.assertRaises(TypeError, SeqContainer, (1,2,3))
#         self.assertRaises(TypeError, SeqContainer, {'test':1})
#         self.assertRaises(TypeError, SeqContainer, 'teststring')
#         self.assertRaises(TypeError, SeqContainer, 1)
#         self.assertRaises(TypeError, SeqContainer, None)
        
    def testCorrectInput(self):
        SeqContainer(range(10))
        SeqContainer(self.iterator)
        SeqContainer(self.iterator, useLazyEvaluation=True)

    def testIterating(self):
        for i,j in zip(self.seqContainer, range(10)):
            self.assertEqual(i,j, 'Values do not match')

    def iterator(self):
        for i in range(10):
            yield i

    def testToList(self):
        self.assertEqual(list(self.seqContainer), range(10))


class TestList(TestSeqContainer):
    def setUp(self):
        self.seqContainer = SeqContainer(range(10), useLazyEvaluation=False)     

class TestGenerator(TestSeqContainer):
    def setUp(self):
        self.seqContainer = SeqContainer(generator=pynopticon.weakmethod(self, 'iterator'), useLazyEvaluation=True)

#class TestGeneratorToList(TestSeqContainer):
#    def setUp(self):
#        self.seqContainer = SeqContainer(self.iterator, useLazyEvaluation=False)


testAll = ['testIterating', 'testToList']

def suiteInput():
    tests = ['testCorrectInput']
    return unittest.TestSuite(map(TestSeqContainer, tests))

def suiteList():
    return unittest.TestSuite(map(TestList, testAll))

def suiteGenerator():
    return unittest.TestSuite(map(TestGenerator, testAll))

#def suiteGeneratorToList():
#    return unittest.TestSuite(map(TestGeneratorToList, testAll))

unittest.TextTestRunner(verbosity=2).run(suiteInput())
unittest.TextTestRunner(verbosity=2).run(suiteList())
unittest.TextTestRunner(verbosity=2).run(suiteGenerator())
#unittest.TextTestRunner(verbosity=2).run(suiteGeneratorToList())
