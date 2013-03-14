#!/bin/env python

'''
Authors: Bernie Pope, Gayle Philip, Clare Sloggett

Description:

Main module of the pipeline, initialises the system, and then calls
the ruffus functions to either run, print or graph the pipeline.

The tasks of the pipeline are defined in another file: example_pipeline.py

'''

import sys
from ruffus import (pipeline_run, pipeline_printout, pipeline_printout_graph,
    black_hole_logger)
from utils import (getOptions, setOptions, startLogger)
from cmdline_args import get_cmdline_args
import example_pipeline 

def main():
    # options must be set first
    args = get_cmdline_args()
    options = getOptions(args)
    setOptions(options)

    logDir = options.pipeline['logDir']
    startLogger()
    pipelineOptions = options.pipeline
    endTasks = pipelineOptions['end']
    forcedTasks = pipelineOptions['force']
    style = pipelineOptions['style']
    if pipelineOptions['rebuild'] == 'fromstart':
        rebuildMode = True
    elif pipelineOptions['rebuild'] == 'fromtargets':
        rebuildMode = False
    else:
        rebuildMode = True
    if style == 'run':
        # Perform the pipeline steps (run the pipeline).
        pipeline_run(
           # End points of the pipeline.
           endTasks, 
           # How many ruffus tasks to run.
           multiprocess=pipelineOptions['procs'], 
           logger=black_hole_logger,
           # Force the pipeline to start from here, regarless of whether the
           # stage is up-to-date or not.
           forcedtorun_tasks=forcedTasks, 
           # Choose the mode in which ruffus decides how much work needs to be
           # done.
           gnu_make_maximal_rebuild_mode=rebuildMode)
    elif style == 'flowchart':
        # Draw the pipeline as a diagram.
        pipeline_printout_graph(
            'flowchart.svg',
            'svg',
            endTasks,
            no_key_legend=False)
    elif style == 'print':
        # Print a textual description of what the piplines would do,
        #but don't actuall run it.
        pipeline_printout(
           sys.stdout,
           endTasks,
           verbose=5,
           wrap_width=100000,
           forcedtorun_tasks=forcedTasks,
           gnu_make_maximal_rebuild_mode=rebuildMode)

if __name__ == '__main__':
    main()
