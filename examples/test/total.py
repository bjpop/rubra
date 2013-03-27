#!/bin/env python

# sum up all the numbers in the first column of the
# first line of each input file and print the result

# used in the example pipeline

import sys

count = 0
for file in sys.argv[1:]:
    with open(file) as f:
        for line in f:
            ws = line.split()
            count += int(ws[0])
            break

print(count)
