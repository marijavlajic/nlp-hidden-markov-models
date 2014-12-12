import sys
from hidden_markov_model import CountsGenerator
from viterbi_algorithm import RareNGramProcessor, ClassNGramProcessor

def run(train_filename, counts_filename, test_filename):
    RareNGramProcessor(CountsGenerator.run(train_filename, counts_filename)[0], test_filename)
    ClassNGramProcessor(CountsGenerator.run(train_filename, counts_filename)[1], test_filename)

run(*sys.argv[1:4])
