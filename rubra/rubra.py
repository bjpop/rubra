#!/usr/bin/env python

'''
Authors: Bernie Pope, Gayle Philip, Clare Sloggett

Description:

Main module of the pipeline, initialises the system, and then calls
the ruffus functions to either run, print or graph the pipeline.
'''

import sys
import os
from ruffus import (pipeline_run, pipeline_printout, pipeline_printout_graph,
                    black_hole_logger)
from utils import (getOptions, setOptions, startLogger, drop_py_suffix)
from cmdline_args import get_cmdline_args


def main():

    args = get_cmdline_args()

    # We want to look for modules in the directory local to the pipeline,
    # just as if the pipeline script had been called directly.
    # This includes the script itself and the config files imported by getOptions
    sys.path.insert(0, os.path.dirname(args.pipeline))

    # options must be set before pipeline is imported
    options = getOptions(args)
    setOptions(options)

    # import the pipeline so its stages are defined
    # the name of the pipeline is given on the command line
    __import__(drop_py_suffix(args.pipeline))

    logDir = options.pipeline['logDir']
    startLogger()
    pipelineOptions = options.pipeline
    endTasks = pipelineOptions['end']
    forcedTasks = pipelineOptions['force']
    style = pipelineOptions['style']
    if pipelineOptions['rebuild'] == 'fromstart':
        rebuildMode = True
    elif pipelineOptions['rebuild'] == 'fromend':
        rebuildMode = False
    else:
        rebuildMode = True
    if style in ['run', 'touchfiles']:
        touchfiles_flag = (style=='touchfiles')
        # Perform the pipeline steps (run the pipeline).
        pipeline_run(
            # End points of the pipeline.
            endTasks,
            # How many ruffus tasks to run.
            multiprocess=pipelineOptions['procs'],
            logger=black_hole_logger,
            # Force the pipeline to start from here, regardless of whether the
            # stage is up-to-date or not.
            forcedtorun_tasks=forcedTasks,
            # If the style was touchfiles, we will set a flag to bring 
            # files up to date without running anything
            touch_files_only=touchfiles_flag,
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
