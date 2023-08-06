from Dictionary.Word cimport Word
from Math.Vector cimport Vector


cdef class VectorizedWord(Word):

    cdef Vector __vector

    cpdef Vector getVector(self)
