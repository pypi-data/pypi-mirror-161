from Dictionary.Word cimport Word


cdef class ExceptionalWord(Word):

    cdef str __root
    cdef object __pos

    cpdef str getRoot(self)
    cpdef object getPos(self)
