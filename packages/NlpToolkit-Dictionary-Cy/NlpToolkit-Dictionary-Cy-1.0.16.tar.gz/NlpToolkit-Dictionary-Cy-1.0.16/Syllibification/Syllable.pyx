cdef class Syllable:

    def __init__(self, syllable: str):
        """
        A constructor of Syllable class which takes a String as an input and initializes syllable variable with given input.

        PARAMETERS
        ----------
        syllable : str
            String input.
        """
        self.__syllable = syllable

    cpdef str getText(self):
        """
        Getter for the syllable variable.

        RETURNS
        -------
        str
            The syllable variable.
        """
        return self.__syllable
