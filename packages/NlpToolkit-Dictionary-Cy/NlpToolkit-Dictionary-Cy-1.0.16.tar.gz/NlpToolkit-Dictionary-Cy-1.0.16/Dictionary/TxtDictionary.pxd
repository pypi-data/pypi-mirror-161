from Dictionary.Trie.Trie cimport Trie
from Dictionary.Dictionary cimport Dictionary
from Dictionary.TxtWord cimport TxtWord
from Dictionary.Word cimport Word


cdef class TxtDictionary(Dictionary):

    cdef dict __misspelledWords

    cpdef addNumber(self, str name)
    cpdef addRealNumber(self, str name)
    cpdef addFraction(self, str name)
    cpdef addTime(self, str name)
    cpdef bint addProperNoun(self, str name)
    cpdef bint addNoun(self, str name)
    cpdef bint addVerb(self, str name)
    cpdef bint addAdjective(self, str name)
    cpdef bint addAdverb(self, str name)
    cpdef bint addPronoun(self, str name)
    cpdef bint addWithFlag(self, str name, str flag)
    cpdef mergeDictionary(self, str secondFileName, str mergedFileName)
    cpdef __loadFromText(self, str fileName)
    cpdef __loadMisspelledWords(self, str fileName)
    cpdef str getCorrectForm(self, str misspelledWord)
    cpdef saveAsTxt(self, str fileName)
    cpdef __addWordWhenRootSoften(self, Trie trie, Py_UNICODE last, str root, TxtWord word)
    cpdef Trie prepareTrie(self)