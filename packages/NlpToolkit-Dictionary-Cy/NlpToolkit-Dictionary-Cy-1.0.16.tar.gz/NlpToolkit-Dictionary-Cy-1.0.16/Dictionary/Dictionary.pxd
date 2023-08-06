from Dictionary.Word cimport Word


cdef class Dictionary:

    cdef list words
    cdef str filename
    cdef object comparator

    cpdef Word getWord(self, str name)
    cpdef int getWordIndex(self, str name)
    cpdef removeWord(self, str name)
    cpdef int size(self)
    cpdef Word getWordWithIndex(self, int index)
    cpdef int longestWordSize(self)
    cpdef int __getPosition(self, Word word)
    cpdef int getWordStartingWith(self, str _hash)
