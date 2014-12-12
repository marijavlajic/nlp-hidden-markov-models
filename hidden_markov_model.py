from collections import defaultdict
import subprocess
from processor import Processor


class CountsProcessor(Processor):
    """
    Base class for processing counts files.
    """

    def __init__(self, counts_filename, corpus_filename):
        """
        Takes counts_filename, as referenced in parent class,
        and corpus_filename in the format "word tag" and sets up
        output filenames for subclasses.
        """

        super(CountsProcessor, self).__init__(counts_filename)
        self.__suffix, self._output = self._process()
        self.__corpus_filename = corpus_filename

    def write_corpus_file(self):
        """
        Takes corpus_filename as passed in the contructor and writes
        "rareified/classified" output corpus file of the same format.
        """
        with open(self.__corpus_filename, "r") as input_file:
            with open(self.filename(self.__corpus_filename, self.__suffix), "w") as output_file:
                for line in input_file:
                    words = line.split(" ")
                    found = False
                    for key in self._output:
                        if words[0] in self._output[key]:
                            output_file.write(" ".join([key, words[1]]))
                            found = True
                            break
                    if not found:
                        output_file.write(line)

                input_file.close()
                output_file.close()

    @staticmethod
    def corpus_file_to_counts_file(corpus_filename, counts_filename):
        """
        Calls count_freqs.py provided in the assignments; 
        takes corpus file to create counts file.
        """

        counts_file = open(counts_filename, "w")
        subprocess.call(["python", "count_freqs.py", corpus_filename],
                        stdout=counts_file)
        counts_file.close()

    def _process(self):
        raise NotImplementedError()


class RareProcessor(CountsProcessor):
    """
    Implements the processor which replaces all words 
    occurring fewer than 5 times with _RARE_.
    """

    def _process(self):
        rare_words = set()
        corpus = [word for word, tag in self._hmm.emission_counts]

        for word in corpus:
            count = 0
            for tag in self._hmm.ngram_counts[0]:
                count += self._hmm.emission_counts[(word, tag[0])]
            if count < 5:
                rare_words.add(word)

        return "rare", {"_RARE_": rare_words}


class ClassProcessor(CountsProcessor):
    """
    Implements the processor to additionally classify _RARE_ words as:
    * _NUMERIC_ -- if they contain at least one numeric character;
    * _ALLCAPS_ -- if the consits entirely of capital letters;
    * _LASTCAPS -- if not all letters are capital, but last is.
    """

    def _process(self):
        output_sets = defaultdict(set)
        corpus = [word for word, tag in self._hmm.emission_counts]

        for word in corpus:
            count = 0
            for tag in self._hmm.ngram_counts[0]:
                count += self._hmm.emission_counts[(word, tag[0])]
            if count < 5:
                if any(c.isdigit() for c in word):
                    output_sets["_NUMERIC_"].add(word)
                elif word.isupper():
                    output_sets["_ALLCAPS_"].add(word)
                elif word[-1].isupper():
                    output_sets["_LASTCAPS_"].add(word)
                else:
                    output_sets["_RARE_"].add(word)

        return "class", output_sets


class CountsGenerator(object):
    """
    Generates counts files using RareProcessor and ClassProcessor.
    """

    @staticmethod
    def run(corpus_filename, counts_filename):
        CountsProcessor.corpus_file_to_counts_file(corpus_filename, counts_filename)

        RareProcessor(counts_filename, corpus_filename).write_corpus_file()
        ClassProcessor(counts_filename, corpus_filename).write_corpus_file()

        output_corpus_filename_rare = Processor.filename(corpus_filename, "rare")
        output_counts_filename_rare = Processor.filename(counts_filename, "rare")
        CountsProcessor.corpus_file_to_counts_file(output_corpus_filename_rare,
                                                   output_counts_filename_rare)

        output_corpus_filename_class = Processor.filename(corpus_filename, "class")
        output_counts_filename_class = Processor.filename(counts_filename, "class")
        CountsProcessor.corpus_file_to_counts_file(output_corpus_filename_class,
                                                   output_counts_filename_class)

        return output_counts_filename_rare, output_counts_filename_class

