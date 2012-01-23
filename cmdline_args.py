# Process the unix command line of the pipeline.

import getopt
import sys

def usage():
    print("""Usage: %s
    [-h | --help]
    --opts=<pipeline options file>
    --style=<run | print | flowchart>
    --force=<force this task to run>
    --end=<final task>
    --verbose=<0 | 1 | 2>""") % sys.argv[0]

longFlags = ["help", "verbose=", "opts=", "style=", "force=", "end="]
shortFlags = "h"

class CmdArgs(object):
    def __init__(self):
        self.opts = None
        self.style = None
        self.verbose = None
        self.force = None
        self.end = None

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
            args.opts = a
        elif o == "--style":
            args.style = a
        elif o in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif o == '--verbose':
            if a in ('0','1','2'):
                args.verbose = int(a)
        elif o == '--force':
            if args.force is None:
                args.force = [a]
            else:
                args.force.append(a)
        elif o == '--end':
            if args.end is None:
                args.end = [a]
            else:
                args.end.append(a)
    return args
