Rubra: a bioinformatics pipeline.
---------------------------------

https://github.com/bjpop/rubra

Description:
------------

Rubra is a pipeline system for bioinformatics workflows. It is built on top
of the Ruffus (http://www.ruffus.org.uk/) Python library, and adds support
for running pipeline stages on a distributed compute cluster.

Authors:
--------

Bernie Pope, Clare Sloggett, Gayle Philip.

Licence:
--------

Usage:
------

usage: rubra.py [-h] [--pipeline PIPELINE_FILE] --config CONFIG_FILE
                [CONFIG_FILE ...] [--verbose {0,1,2}]
                [--style {print,run,flowchart}] [--force TASKNAME]
                [--end TASKNAME] [--rebuild {fromstart,fromend}]

A bioniformatics pipeline system.

optional arguments:
  -h, --help            show this help message and exit
  --pipeline PIPELINE_FILE
                        Your Ruffus pipeline stages (a Python module)
  --config CONFIG_FILE [CONFIG_FILE ...]
                        One or more configuration files (Python modules)
  --verbose {0,1,2}     Output verbosity level: 0 = quiet; 1 = normal; 2 =
                        chatty (default is 1)
  --style {print,run,flowchart}
                        Pipeline behaviour: print; run; flowchart (default is
                        print)
  --force TASKNAME      tasks which are forced to be out of date regardless of
                        timestamps
  --end TASKNAME        end points (tasks) for the pipeline
  --rebuild {fromstart,fromend}
                        rebuild outputs by working back from end tasks or
                        forwards from start tasks (default is fromend)

Example:
--------

Below is a little example pipeline which you can find in the Rubra source
tree. It counts the number of lines in two files (potentially in parallel,
and then sums the results together). The input files are in the test
subdirectory.

   ./rubra.py --pipeline example_pipeline.py --config example_config.py --style run

The final result is written to the file test/total.txt

Configuration:
--------------

Options for the whole pipeline:

Options for each stage of the pipeline:
