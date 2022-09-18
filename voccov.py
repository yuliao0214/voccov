#!/usr/bin/env python3

import re
import string
import sys
import os
import argparse
from collections import defaultdict
import matplotlib.pyplot as plt

__all__ = ['WordFinder', 'Book']

coca_list = {}
with open('COCA60000.txt', 'r') as fin:
    coca_list = fin.read().split('\n')

lemmas = {}
with open('lemmas.txt') as fin:
    for line in fin:
        line = line.strip()
        headword = line.split('\t')[0]
        try:
            related = line.split('\t')[1]
        except IndexError:
            related = None
        lemmas[headword] = related

valid_words = set()
for headword, related in lemmas.items():
    valid_words.add(headword)
    if related:
        valid_words.update(set(related.split()))


class WordFinder(object):
    '''A compound structure of dictionary and set to store word mapping'''

    def __init__(self):
        """Initialize lame containers for 'quick' search

        Structure of main_table
        {
            'a':{
                     # All related words and the headword start with same letter
                     'abandon': {'abandons', 'abandoned', 'abandoning'},

                     'apply': {'applies', 'applied', 'applying'},

                     # headword with no related word
                     'abeam': None,
                     ...
                },
            'b': {...},
            'c': {...},
            ...
        }

        Structure of special_table
        {

            # 1+ related words does not share the same starting letter
            # with heasdword
            'although': {'altho', 'tho', 'though'},
            'bad': {'badder', 'baddest', 'badly', 'badness', 'worse', 'worst'},
            ...
        }

        """
        self.main_table = {}
        for char in string.ascii_lowercase:
            self.main_table[char] = {}
        self.special_table = {}

        for headword, related in lemmas.items():
            # Only 3 occurrences of uppercase in lemmas.txt, which include 'I'
            # Trading precision for simplicity
            headword = headword.lower()
            try:
                related = related.lower()
            except AttributeError:
                related = None
            if related:
                for word in related.split():
                    if word[0] != headword[0]:
                        self.special_table[headword] = set(related.split())
                        break
                else:
                    self.main_table[headword[0]][headword] = set(related.split())
            else:
                self.main_table[headword[0]][headword] = None

    def find_headword(self, word):
        """Search the 'table' and return the original form of a word"""
        word = word.lower()
        alpha_table = self.main_table[word[0]]
        if word in alpha_table:
            return word

        for headword, related in alpha_table.items():
            if related and (word in related):
                return headword

        for headword, related in self.special_table.items():
            if word == headword:
                return word
            if word in related:
                return headword
        # This should never happen after the removal of words not in valid_words
        # in Book.__init__()
        return None

    # TODO
    def find_related(self, headword):
        pass


def is_dirt(word):
    return word not in valid_words


def list_dedup(list_object):
    """Return the deduplicated copy of given list"""
    temp_list = []
    for item in list_object:
        if item not in temp_list:
            temp_list.append(item)
    return temp_list


class Book(object):
    def __init__(self, filepath):
        self.total = 0
        self.words = defaultdict(list)

        with open(filepath) as bookfile:

            # split input file
            content = bookfile.read().lower()
            temp_list = re.split(r'\b([a-zA-Z-]+)\b', content)
            temp_list = [item for item in temp_list if not is_dirt(item)]

            # do lemma
            finder = WordFinder()
            temp_list = [finder.find_headword(item) for item in temp_list]
            self.words = dict.fromkeys(temp_list, 0)

            # count word frequency in COCA, saved in words[word][0]
            for tmp in self.words:
                self.words[tmp] = [0] * 2
                if tmp in coca_list:
                    freq = coca_list.index(tmp)
                    self.words[tmp][0] = freq + 1

            # count word occurrence times in input file, saved in words[word][1]
            for tmp in temp_list:
                self.words[tmp][1] += 1
                self.total += 1

    def coverage(self, voca_num):
        sum_voca = 0
        for v in self.words.values():
            if v[0] <= voca_num:
                sum_voca += v[1]
        return sum_voca * 100 / self.total


if __name__ == '__main__':
    if sys.platform == 'nt':
        sys.stderr.write("I haven't tested the code on Windows. Feedback is welcome.\n")

    LINE_SEP = os.linesep
    num = []
    cov = []

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input_file')
    parser.add_argument('-o', '--output', dest='output_file')
    parser.add_argument('-s', '--sort', dest='sort', help='sorted by coca or occ')
    parser.add_argument('-r', '--reverse', action='store_true', help='reverse sort result')
    parser.add_argument('-p', '--plot', action="store_true", help='show coverage figure')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    if args.sort == "occ":
        sort = 1
    else:
        sort = 0

    book = Book(args.input_file)

    print("Total words:", book.total)
    for i in list(range(4, 20)) + list(range(20, 45, 5)) + list(range(50, 70, 10)):
        tmpnum = 1000 * i
        tmpcov = book.coverage(tmpnum)
        num.append(tmpnum)
        cov.append(tmpcov)
        print("%-5.d vocabulary coverage:%6.2f%%" % (tmpnum, tmpcov))

    report = []
    max_width = max(len(str(v)) for v in book.words.keys())
    report.append('{:<{}} {:<5} {:<5}'.format("WORD", max_width, "COCA", "OCC"))
    report.append('{:<{}} {:<5} {:<5}'.format("----", max_width, "----", "---"))

    for word in sorted(book.words, key=lambda x: book.words[x][sort], reverse=args.reverse):
        report.append('{:<{}} {:<5} {:<5}'.format(word, max_width, book.words[word][0], book.words[word][1]))

    if args.output_file:
     with open(args.output_file, 'w') as output:
         output.write(LINE_SEP.join(report))
         output.write(LINE_SEP)

    if args.plot:
        plt.title(os.path.basename(args.input_file) + " stat data")
        plt.xlabel("vocabulary")
        plt.ylabel("coverage")
        plt.plot(num, cov)
        plt.grid()
        plt.show()


