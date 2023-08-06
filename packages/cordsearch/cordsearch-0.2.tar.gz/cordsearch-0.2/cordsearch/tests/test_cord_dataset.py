import unittest
import datasets
import numpy

from cordsearch import CordDataset as CD


class TestCordDataset(unittest.TestCase):

    def test_data(self):
        self.assertTrue(type(CD().train) == datasets.arrow_dataset.Dataset)
        self.assertTrue(type(CD().abstracts) == list)
        self.assertTrue(type(CD().bodytexts) == list)

    def test_sentence(self):
        self.assertTrue(type(CD().abstract_sentence(1, 1)) == str)
        self.assertTrue(type(CD().bodytext_sentence(1, 1)) == str)

    def test_parse(self):
        self.assertTrue(type(CD().parse_abstract(1)) == list)
        self.assertTrue(type(CD().parse_bodytext(1)) == list)

    def test_embedding(self):
        self.assertTrue(numpy.shape(CD().abstract_sentence_embeddings(1, 1)) == (384,))
        self.assertTrue(numpy.shape(CD().bodytext_sentence_embeddings(1, 1)) == (384,))
        self.assertTrue(numpy.shape(CD().abstract_embeddings(1)) == (384,))
        self.assertTrue(numpy.shape(CD().bodytext_embeddings(1)) == (384,))

    def test_compute(self):
        self.assertTrue(type(CD().compute_similarity(
            CD().abstract_sentence_embeddings(1, 1),
            CD().abstract_sentence_embeddings(1, 4)
            )) == numpy.float32)


if __name__ == '__main__':
    unittest.main()
