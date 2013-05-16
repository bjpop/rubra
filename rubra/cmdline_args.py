# Process the unix command line of the pipeline.

import argparse
from version import rubra_version

def get_cmdline_args():
    return parser.parse_args()

parser = argparse.ArgumentParser(
    description='A bioinformatics pipeline system.')

parser.add_argument(
    'pipeline',
    metavar='PIPELINE_FILE',
    type=str,
    help='Your Ruffus pipeline stages (a Python module)')
parser.add_argument(
    '--config',
    metavar='CONFIG_FILE',
    type=str,
    nargs='+',
    required=True,
    help='One or more configuration files (Python modules)')
parser.add_argument(
    '--verbose',
    type=int,
    choices=(0, 1, 2),
    required=False,
    default=1,
    help='Output verbosity level: 0 = quiet; 1 = normal; \
          2 = chatty (default is 1)')
parser.add_argument(
    '--style',
    type=str,
    choices=('print', 'run', 'flowchart', 'touchfiles'),
    required=False,
    default='print',
    help='Pipeline behaviour: print; run; touchfiles; flowchart (default is print)')
parser.add_argument(
    '--force',
    metavar='TASKNAME',
    type=str,
    required=False,
    default=[],
    nargs='+',
    help='tasks which are forced to be out of date regardless of timestamps')
parser.add_argument(
    '--end',
    metavar='TASKNAME',
    type=str,
    required=False,
    help='end points (tasks) for the pipeline')
parser.add_argument(
    '--rebuild',
    type=str,
    choices=('fromstart', 'fromend'),
    required=False,
    default='fromstart',
    help='rebuild outputs by working back from end tasks or forwards \
          from start tasks (default is fromstart)')
parser.add_argument(
    '--version', action='version', version='%(prog)s ' + rubra_version)
