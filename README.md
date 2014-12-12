Description
===========

This project is a part of the [Natural Language Processing](https://www.coursera.org/course/nlangp)
Coursera Course.  It implements the [Hidden Markov model](http://en.wikipedia.org/wiki/Hidden_Markov_model)
using [Viterbi algorithm](http://en.wikipedia.org/wiki/Viterbi_algorithm).

Project Files
=============

* docs/assignment.pdf - describes the Coursera assignment.
* count_freqs.py - module provided in the assignment.

* main.py - takes data/gene.train, data/gene.counts, data/gene.dev as arguments.
* processor.py - base class for processors that use markov chain model object.
* hidden_markov_model.py - generates counts files from corpus files.
* viterbi_algorithm.py - generates tags for test files.

Running
=======

To run it (with Python 2.x) do:

    $ python main.py "data/gene.train" "data/gene.counts" "data/gene.dev"

Note: data/gene.train and data/gene.dev are input files; data/gene.counts is an
intermediary filename.

Output
======

The code produces the following output:

* gene.dev.bigram.rare
* gene.dev.trigram.rare
* gene.dev.bigram.class
* gene.dev.trigram.class

All files are of the format "word tag".

The output files differ in the way they treat rare words:
* .rare files classify all words with corpus frequency lower than 5 as rare.
* .class files further divide the rare class into:
  * words with at least one numeric character.
  * words that consist entirely of capital letters.
  * words that are not all caps, but end end with a capital letter.

The code runs two tagging methods, identified by .bigram. and .trigram.
extensions.

All output and intermediary files have been added to the repository in the
data/ directory.