from decimal import Decimal
from collections import defaultdict
import count_freqs as cf
from processor import Processor

class NGramProcessor(Processor):
    """
    Base class for processing ngrams.
    """

    def __init__(self, counts_filename, input_filename):
        """
        Takes counts_filename and input_filename containing test data
        and implements gene tagger using Viterbi algorithm.
        """
        
        super(NGramProcessor, self).__init__(counts_filename)
        self.__input_filename = input_filename
        self.__ngram_run("bigram", self.__bigram)
        self.__ngram_run("trigram", self.__trigram)

    def _process_ngram(self, second_tag, word):
        """
        Abstract method which should implement a particular 
        classification algorithm.
        """

        raise NotImplementedError()

    def _extension(self):
        """
        Extension added to the output file that identifies 
        the classification algorithm.
        """

        raise NotImplementedError()

    def _emission_params(self, word, tag):
        """
        Calculates emission parameters using methods defined in count_freqs.py.
        """

        return self._hmm.emission_counts[(word, tag[0])]/self._hmm.ngram_counts[0][tag]

    def __trigram_params(self, *ngram_components):
        """
        Calculates trigram parameters using methods defined in count_freqs.py.
        """

        trigram = self._hmm.ngram_counts[2][(ngram_components)]
        bigram = self._hmm.ngram_counts[1][(ngram_components[0:2])]
        return trigram / bigram

    def __ngram_run(self, file_suffix, ngram_function):
        """
        Takes a file_suffix to be appended to the output file.

        This method sets up and passes to the ngram function 
        the following arguments:
        * corpus
        * tags
        * input file
        * output file

        ngram_function takes the above arguments and calculates an ngram,
        e.g. bigram or trigram.
        """

        corpus = [word for word, tag in self._hmm.emission_counts]
        tags = [tag for tag in self._hmm.ngram_counts[0]]

        input_file = open(self.__input_filename, "r")
        output_file = open(self.filename(self.__input_filename, file_suffix, self._extension()), "w")

        ngram_function(corpus, tags, input_file, output_file)

        input_file.close()
        output_file.close()

    def __bigram(self, corpus, tags, input_file, output_file):
        """
        A bigram implementation suitable to be passed to the ngram_function.
        """

        emission_parameters = defaultdict(float)
        for line in input_file:
            word = line.strip()
            if word:
                for tag in tags:
                    if not word in corpus:
                        emission_parameters[tag] = self._process_ngram(tag[0], word)
                    else:
                        emission_parameters[tag] = self._emission_params(word, tag)
                output_file.write(word+" "+
                                  max(emission_parameters, key=emission_parameters.get)[0]+"\n")
            else:
                output_file.write("\n")

    def __trigram(self, corpus, tags, input_file, output_file):
        """
        A trigram implementation suitable to be passed to the ngram_function.
        """

        for sentence in cf.sentence_iterator(cf.simple_conll_corpus_iterator(input_file)):
            sentence_length = len(sentence)
            tag_sentence = ["*", "*"]+[[tag[0] for tag in tags] for i in sentence]
            backpointer = defaultdict(lambda: defaultdict(dict))
            probability = defaultdict(lambda: defaultdict(dict))
            probability[-1, "*", "*"] = 1.0

            for word_index in range(sentence_length):
                word = sentence[word_index][1]
                for first_tag in tag_sentence[word_index+1]:
                    for second_tag in tag_sentence[word_index+2]:
                        max_probability = 0.
                        max_backpointer = []
                        for current_tag in tag_sentence[word_index]:
                            if not word in corpus:
                                emission_parameters = self._process_ngram(second_tag, word)
                            else:
                                emission_parameters = self._emission_params(word, (second_tag,))
                            sequence_probability = \
                                probability[word_index-1, current_tag, first_tag]
                            trigram = self.__trigram_params(current_tag, first_tag, second_tag)
                            current_probability = \
                                Decimal(sequence_probability) * \
                                Decimal(trigram) * \
                                Decimal(emission_parameters)
                            if current_probability > max_probability:
                                max_probability = current_probability
                                max_backpointer = current_tag
                        probability[word_index, first_tag, second_tag] = max_probability
                        backpointer[word_index, first_tag, second_tag] = max_backpointer

            result_tags = [[] for i in range(sentence_length)]
            max_probability = 0.
            for first_tag in tag_sentence[-2]:
                for second_tag in tag_sentence[-1]:
                    sequence_probability = probability[sentence_length-1, first_tag, second_tag]
                    trigram = self.__trigram_params(first_tag, second_tag, "STOP")
                    current_probability = \
                        Decimal(sequence_probability) * \
                        Decimal(trigram)
                    if current_probability > max_probability:
                        max_probability = current_probability
                        result_tags[sentence_length-1] = second_tag
                        result_tags[sentence_length-2] = first_tag

            for word_index in range(sentence_length-3, -1, -1):
                result_tags[word_index] = \
                    backpointer[word_index+2, result_tags[word_index+1], result_tags[word_index+2]]

            for i in range(sentence_length):
                output_file.write(sentence[i][1]+" "+result_tags[i]+"\n")
            output_file.write("\n")


class RareNGramProcessor(NGramProcessor):
    """
    Calculates ngrams using classification algorithm which replaces all words
    occurring fewer than 5 times with _RARE_.
    """

    def _process_ngram(self, second_tag, _):
        return self._emission_params("_RARE_", (second_tag,))

    def _extension(self):
        return "rare"


class ClassNGramProcessor(NGramProcessor):
    """
    Calculates ngrams using classification algorithm that classifies all _RARE_
    words as:
    * _NUMERIC_ -- if they contain at least one numeric character;
    * _ALLCAPS_ -- if the consits entirely of capital letters;
    * _LASTCAPS -- if not all letters are capital, but last is.
    """

    def _process_ngram(self, second_tag, word):
        if any(c.isdigit() for c in word):
            emission_parameters = self._emission_params("_NUMERIC_", (second_tag,))
        elif word.isupper():
            emission_parameters = self._emission_params("_ALLCAPS_", (second_tag,))
        elif word[-1].isupper():
            emission_parameters = self._emission_params("_LASTCAPS_", (second_tag,))
        else:
            emission_parameters = self._emission_params("_RARE_", (second_tag,))
        return emission_parameters

    def _extension(self):
        return "class"


