#!/usr/bin/env python

'''
Authors: Bernie Pope, Gayle Philip, Clare Sloggett, Matt Wakefield

Description:

Main module of the pipeline, initialises the system, and then calls
the ruffus functions to either run, print or graph the pipeline.
'''

import sys
import os
from ruffus import (pipeline_run, pipeline_printout, pipeline_printout_graph,
    black_hole_logger, cmdline)
from config import (read_configuration_files, set_config, GLOBAL_PIPELINE_CONFIG)
from logger import (start_logger)
from run_stage import finalize_drmaa_session 
from utils import (drop_py_suffix, mk_dir)
from cmdline_args import get_cmdline_args

def main():
    'The entry point for rubra'
    # read the command line arguments
    args = get_cmdline_args()

    # We want to look for modules in the directory local to the pipeline,
    # just as if the pipeline script had been called directly.
    # This includes the script itself and the config files imported 
    # by read_configuration_files
    sys.path.insert(0, os.path.dirname(args.pipeline))

    # options must be set before pipeline is imported
    config = read_configuration_files(args)
    # store config in global so it can be read from within
    # the pipeline without having to pass it to every
    # stage as an argument
    set_config(config)
    print(config)
    print(GLOBAL_PIPELINE_CONFIG)

    # import the pipeline so its stages are defined
    # the name of the pipeline is given on the command line
    __import__(drop_py_suffix(args.pipeline))

    mk_dir(config.pipeline['log_dir'])
    mk_dir(config.pipeline['script_dir'])

    start_logger()

    # Execute the pipeline
    cmdline.run(args)

    # Finalize the DRMAA session if it was configured
    if global_drmaa_session is not None:
        finalize_drmaa_session()

if __name__ == '__main__':
    main()
