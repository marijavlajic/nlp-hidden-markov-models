import count_freqs as cf

class Processor(object):
    """
    Base class for processors that use markov chain model object.
    """

    def __init__(self, counts_filename):
        """
        Takes a counts_filename of the format "n WORDTAG tag word" 
        produced by count_freqs.py (provided in the assignment)
        and creates instance variable _hmm, an instance of the Hmm class 
        provided by the count_freqs module.
        """

        counts_file = open(counts_filename, "r")
        hidden_markov_model = cf.Hmm(3)
        hidden_markov_model.read_counts(counts_file)
        counts_file.close()
        self._hmm = hidden_markov_model

    @staticmethod
    def filename(*components):
        """
        Joins list of filename components with a dot.
        """

        return ".".join(str(c) for c in components)
