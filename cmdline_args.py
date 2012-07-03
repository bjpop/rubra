# Process the unix command line of the pipeline.

import getopt
import sys

def usage():
    print("""Usage: %s
    [-h | --help]
    --opts=<pipeline options files>
    --style=<run | print | flowchart>
    --force=<force this task to run>
    --end=<final task>
    --rebuild=<fromtarget | fromstart>
    --verbose=<0 | 1 | 2>""") % sys.argv[0]

longFlags = ["help", "verbose=", "opts=", "style=", "force=", "end=", "rebuild="]
shortFlags = "h"

class CmdArgs(object):
    def __init__(self):
        self.opts = None    # pipeline options file names
        self.style = None   # what to do with the pipeline, run it, print it, draw a flowchart
        self.verbose = None # how much output to produce when the pipeline runs
        self.force = None   # tasks which are forced to be out of date regardless of timestamps
        self.end = None     # targets for the pipeline
        self.rebuild = None  # rebuild outputs by working back from targets or forwards from start points

def get_cmdline_args():
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortFlags, longFlags)
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    args = CmdArgs()
    for o, a in opts:
        if o == "--opts":
            args.opts = a.split(',')
        elif o == "--style":
            if a in ("run", "print", "flowchart"):
                args.style = a
            else:
                exit("Invalid style argument, must be one of: run, print, flowchart.")
        elif o in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif o == '--verbose':
            if a in ('0','1','2'):
                args.verbose = int(a)
            else:
                exit("Invalid verbose level, must be one of: 0, 1, 2.")
        elif o == '--force':
            if args.force == None:
                args.force = [a]
            else:
                args.force.append(a)
        elif o == '--end':
            if args.end == None:
                args.end = [a]
            else:
                args.end.append(a)
        elif o == '--rebuild':
            if a in ('fromtargets', 'fromstart'):
                args.rebuild = a
            else:
                exit("Invalid rebuild argument, must be one of: fromtargets, fromstart.")
    return args
