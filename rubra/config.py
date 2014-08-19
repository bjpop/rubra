'''Pipeline configuration management.'''

import re
from utils import drop_py_suffix

GLOBAL_PIPELINE_CONFIG = None

def set_config(config):
    '''Save the pipeline configuration in a global variable so that
    it may be referred to in the pipeline.'''
    global GLOBAL_PIPELINE_CONFIG
    GLOBAL_PIPELINE_CONFIG = config

def get_config():
    '''Return the value of the global configuration file'''
    return GLOBAL_PIPELINE_CONFIG

def get_stage_options(options, stage, optionName):
    '''Look for a particular option in a stage, otherwise return the default'''
    try:
        return options.stages[stage][optionName]
    except KeyError:
        return options.stageDefaults[optionName]

def get_command(stage, options):
    '''Find the command string for a given stage'''
    try:
        commandStr = get_stage_options(options, stage, 'command')
        return eval(command_to_lambda(commandStr))
    except KeyError:
        exit("command: %s, is not defined in the options file" % name)

# XXX should sanity check that all the required options are
# specified somwhere, either on command line or in config files.
def read_configuration_files(args):

    class Bag:
        '''A simple container object'''
        pass

    config = Bag()
    config.pipeline = {}

    for module_file in args.config:
        # Check if the config module name ends in a .py suffix, if
        # so drop the suffix because Python module imports do not
        # allow it. XXX is this still necessary?
        module = drop_py_suffix(module_file)
        try:
            imported = __import__(module)
        except ImportError:
            exit('Could not find configuration file: %s' % module_file)
        for name in dir(imported):
            if name[:2] != '__':
                setattr(config, name, getattr(imported, name))

    '''
    options.pipeline['rebuild'] = args.rebuild  # will default on cmdline
    options.pipeline['style'] = args.style      # will default on cmdline
    options.pipeline['verbose'] = args.verbose  # will default on cmdline
    options.pipeline['force'] = args.force      # will default on cmdline
    if args.end:
        options.pipeline['end'] = [args.end]

    # make sure we have an 'end' target specified somewhere
    if 'end' not in options.pipeline:
        exit('end task(s) not specified on command line or in config file')

    # add the pipeline name prefix to all the force tasks and all the end
    # tasks.
    pipeline_name = drop_py_suffix(args.pipeline)
    options.pipeline['force'] = \
        map(lambda name: pipeline_name + '.' + name, options.pipeline['force'])
    options.pipeline['end'] = \
        map(lambda name: pipeline_name + '.' + name, options.pipeline['end'])
    '''
    return config


def command_to_lambda(command):
    '''This converts a short-hand command string, such as:
      'bwa aln -t 8 %ref %seq > %out'
    into:
      'lambda x1, x2, x3: "bwa aln -t 8 %s %s > %s" % (x1, x2, x3)'
    '''
    expanded, numPats = re.subn('%[^ ]*', '%s', command)
    args = []
    for n in range(numPats):
        args.append("x" + str(n))
    argsTuple = str(','.join(args))
    lamStr = 'lambda %s : "%s" %% (%s)' % (argsTuple, expanded, argsTuple)
    return lamStr
