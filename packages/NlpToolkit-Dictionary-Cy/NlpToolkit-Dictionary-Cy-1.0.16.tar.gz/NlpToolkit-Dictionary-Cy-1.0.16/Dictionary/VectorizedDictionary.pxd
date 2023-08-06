from Dictionary.Dictionary cimport Dictionary
from Dictionary.VectorizedWord cimport VectorizedWord


cdef class VectorizedDictionary(Dictionary):

    cpdef addWord(self, VectorizedWord word)
    cpdef VectorizedWord mostSimilarWord(self, str name)
    cpdef list mostSimilarKWords(self, str name, int k)
    cpdef list kMeansClustering(self, int iteration, int k)
    cdef makeComparator(self, VectorizedWord comparedWord)