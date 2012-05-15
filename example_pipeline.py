#!/bin/env python

'''
Authors: Bernie Pope, Gayle Philip, Clare Sloggett

Description:

Simple pipeline to demonstrate how to use the base tools.
Counts the number of lines in a set of files and then sums
them up.

'''

import sys
from ruffus import *
from utils import (runStageCheck, getOptions, initLog)
from cmdline_args import get_cmdline_args

args = get_cmdline_args()
options = getOptions(args)
logDir = options.pipeline['logDir']
logger = initLog(options)

# the input files
data_files = ['test_data/data1.txt', 'test_data/data2.txt']

# count the number of lines in a file
@transform(data_files, suffix('.txt'), ['.count', '.count.Success'])
def countLines(file, outputs):
    output,flagFile = outputs
    runStageCheck('countLines', flagFile, logger, options, file, output)

# sum the counts from the previous stage
@merge(countLines,  ['test_data/total.txt', 'test_data/total.Success'])
def total(files, outputs):
    files = ' '.join(map(lambda pair: pair[0], files))
    output,flagFile = outputs
    runStageCheck('total', flagFile, logger, options, files, output)

# Invoke the pipeline.
# XXX can we shift this to another file?
pipelineOptions = options.pipeline
endTasks = pipelineOptions['end']
forcedTasks = pipelineOptions['force']
style = pipelineOptions['style']
if pipelineOptions['rebuild'] == 'fromstart':
    rebuildMode = True
elif pipelineOptions['rebuild'] == 'fromtargets':
    rebuildMode = False
else:
    rebuildMod = True
if style == 'run':
    # Perform the pipeline steps.
    pipeline_run(endTasks, multiprocess = pipelineOptions['procs'],
                 logger = black_hole_logger, forcedtorun_tasks = forcedTasks,
                 gnu_make_maximal_rebuild_mode=rebuildMode)
elif style == 'flowchart':
    # Draw the pipeline as a diagram.
    pipeline_printout_graph ('flowchart.svg', 'svg', endTasks, no_key_legend = False)
elif style == 'print':
   pipeline_printout(sys.stdout, endTasks, verbose = 5, wrap_width=100000,
                     forcedtorun_tasks = forcedTasks, gnu_make_maximal_rebuild_mode=rebuildMode)
