from Dictionary.Trie.TrieNode cimport TrieNode
from Dictionary.Word cimport Word
from Dictionary.TxtWord cimport TxtWord


cdef class Trie:

    def __init__(self):
        """
        A constructor of Trie class which creates a new TrieNode as rootNode.
        """
        self.__rootNode = TrieNode()

    cpdef addWord(self, str word, Word root):
        """
        The addWord method which takes a String word and a Word root as inputs and adds given word and root to the
        rootNode.

        PARAMETERS
        ----------
        word : str
            String input.
        root : Word
            Word input.
        """
        self.__rootNode.addWord(word, root)

    cpdef set getWordsWithPrefix(self, str surfaceForm):
        """
        The getWordsWithPrefix method which takes a String surfaceForm as an input. First it creates a TrieNode current
        and assigns the rootNode to it, then it creates a new set words. It loops i times where i ranges from 0 to
        length of surfaceForm and assigns current's child that corresponds to the surfaceForm's char at index i and
        assigns it as TrieNode current. If current is not None, it adds all words of current to the words set.

        PARAMETERS
        ----------
        surfaceForm : str
            String input.

        RETURNS
        -------
        set
            words set.
        """
        cdef int i
        cdef TrieNode current
        cdef set words
        current = self.__rootNode
        words = set()
        for i in range(len(surfaceForm)):
            current = current.getChild(surfaceForm[i])
            if current is not None:
                words.update(current.getWords())
            else:
                break
        return words

    cpdef TxtWord getCompundWordStartingWith(self, str _hash):
        """
        The getCompoundWordStartingWith method takes a String hash. First it creates a TrieNode current and assigns
        the rootNode to it. Then it loops i times where i ranges from 0 to length of given hash and assigns current's
        child that corresponds to the hash's char at index i and assigns it as current. If current is None, it returns
        null.

        If current is not None, it loops through the words of current TrieNode and if it is a Portmanteau word, it
        directly returns the word.

        PARAMETERS
        ----------
        _hash : str
            String input.

        RETURNS
        -------
        TxtWord
            None if TrieNode is None, otherwise portmanteau word.
        """
        cdef int i
        cdef TrieNode current
        current = self.__rootNode
        for i in range(len(_hash)):
            current = current.getChild(_hash[i])
            if current is None:
                return None
        if current is not None:
            for word in current.getWords():
                if word.isPortmanteau():
                    return word
        return None
