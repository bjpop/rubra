#!/bin/env python

'''
Authors: Bernie Pope, Gayle Philip, Clare Sloggett

Description:

Simple pipeline to demonstrate how to use the base tools.
Counts the number of lines in a set of files and then sums
them up.

'''

from ruffus import (suffix, transform, merge)
from rubra.run_stage import (run_stage)

# the input files
data_files = ['test/data1.txt', 'test/data2.txt']

# count the number of lines in a file
@transform(data_files, suffix('.txt'), '.count')
def count_lines(file, output):
    run_stage('count_lines', file, output)

# sum the counts from the previous stage
@merge(count_lines, 'test/total.txt')
def total(files, output):
    files = ' '.join(files)
    run_stage('total', files, output)
