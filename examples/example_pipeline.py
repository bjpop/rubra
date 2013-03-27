#!/bin/env python

'''
Authors: Bernie Pope, Gayle Philip, Clare Sloggett

Description:

Simple pipeline to demonstrate how to use the base tools.
Counts the number of lines in a set of files and then sums
them up.

'''

from ruffus import *
from rubra.utils import (runStageCheck)

# the input files
data_files = ['test/data1.txt', 'test/data2.txt']


# count the number of lines in a file
@transform(data_files, suffix('.txt'), ['.count', '.count.Success'])
def countLines(file, outputs):
    output, flagFile = outputs
    runStageCheck('countLines', flagFile, file, output)


# sum the counts from the previous stage
@merge(countLines, ['test/total.txt', 'test/total.Success'])
def total(files, outputs):
    files = ' '.join(map(lambda pair: pair[0], files))
    output, flagFile = outputs
    runStageCheck('total', flagFile, files, output)
