from Dictionary.Trie.TrieNode cimport TrieNode
from Dictionary.Word cimport Word
from Dictionary.TxtWord cimport TxtWord


cdef class Trie:

    cdef TrieNode __rootNode

    cpdef addWord(self, str word, Word root)
    cpdef set getWordsWithPrefix(self, str surfaceForm)
    cpdef TxtWord getCompundWordStartingWith(self, str _hash)