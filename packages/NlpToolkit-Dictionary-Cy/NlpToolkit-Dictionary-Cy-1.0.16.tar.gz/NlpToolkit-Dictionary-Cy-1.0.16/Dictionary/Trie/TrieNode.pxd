from Dictionary.Word cimport Word


cdef class TrieNode:

    cdef dict __children
    cdef set __words

    cpdef addWord(self, str word, Word root, int index=*)
    cpdef TrieNode getChild(self, char ch)
    cpdef set getWords(self)
