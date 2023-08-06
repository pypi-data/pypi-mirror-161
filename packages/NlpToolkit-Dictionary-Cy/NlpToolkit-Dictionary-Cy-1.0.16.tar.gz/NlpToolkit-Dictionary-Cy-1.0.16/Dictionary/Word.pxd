cdef class Word:

    cdef str name

    cpdef int charCount(self)
    cpdef str getName(self)
    cpdef setName(self, str name)
    cpdef bint isPunctuation(self)
    cpdef list toCharacters(self)
