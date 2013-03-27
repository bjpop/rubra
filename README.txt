Rubra: a bioinformatics pipeline.
---------------------------------

https://github.com/bjpop/rubra

License:
--------

Rubra is licensed under the MIT license. See LICENSE.txt.

Description:
------------

Rubra is a pipeline system for bioinformatics workflows. It is built on top
of the Ruffus (http://www.ruffus.org.uk/) Python library, and adds support
for running pipeline stages on a distributed compute cluster.

Authors:
--------

Bernie Pope, Clare Sloggett, Gayle Philip, Matthew Wakefield

Usage:
------

usage: rubra [-h] [--pipeline PIPELINE_FILE] --config CONFIG_FILE
                [CONFIG_FILE ...] [--verbose {0,1,2}]
                [--style {print,run,flowchart}] [--force TASKNAME]
                [--end TASKNAME] [--rebuild {fromstart,fromend}]

A bioinformatics pipeline system.

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
tree. It counts the number of lines in two files (test/data1.txt and
test/data2.txt), and then sums the results together.

   rubra --pipeline example_pipeline.py --config example_config.py --style run

There are 2 lines in the first file and 1 line in the second file. So the
result is 3, which is written to the output file test/total.txt.

The --pipeline argument is a Python script which contains the actual
code for each pipeline stage (using Ruffus notation). The --config
argument is a Python script which contains configuration options for the
whole pipeline, plus options for each stage (including the shell command
to run in the stage). The --style argument says what to do with the pipeline:
"run" means "perform the out-of-date steps in the pipeline". The default
style is "print" which just displays what the pipeline would do if it were
run. You can get a diagram of the pipeline using the "flowchart" style.

Configuration:
--------------

Configuration options are written into one or more Python scripts, which
are passed to Rubra via the --config command line argument.

Some options are required, and some are, well, optional.

Options for the whole pipeline:
-------------------------------

    pipeline = {
        "logDir": "log",
        "logFile": "pipeline.log",
        "procs": 2,
        "end": ["total"],
    }


Options for each stage of the pipeline:
---------------------------------------

    stageDefaults = {
        "distributed": False,
        "walltime": "00:10:00",
        "memInGB": 1,
        "queue": "batch",
        "modules": ["python-gcc"]
    }

    stages = {
        "countLines": {
            "command": "wc -l %file > %out",
        },
        "total": {
            "command": "./test/total.py %files > %out",
        },
    }
