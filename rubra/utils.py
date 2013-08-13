# Various useful utilities for the pipeline.

import sys
import errno
import subprocess
from ruffus.proxy_logger import *
import logging
import imp
import os
import os.path
from shell_command import shellCommand
#from cluster_job import PBS_Script
from cluster_job import SLURM_Job 
import re


# A simple container object
class Bag:
    pass

# XXX I don't think the defaults really belong here.
defaultOptionsModule = ['pipeline_config']
defaultWalltime = None  # use the default walltime of the scheduler
defaultModules = []
defaultQueue = 'batch'
defaultMemInGB = None  # use the default mem of the scheduler
defaultDistributed = False
defaultLogDir = 'log'
defaultLogFile = 'pipeline.log'
defaultStyle = 'run'
defaultProcs = 4
defaultPaired = False

stageDefaults = {
    'distributed': defaultDistributed,
    'walltime': defaultWalltime,
    'memInGB': defaultMemInGB,
    'modules': defaultModules,
    'queue': defaultQueue
}

pipeline = {
    'logDir': defaultLogDir,
    'logFile': defaultLogFile,
    'style': defaultStyle,
    'procs': defaultProcs,
    'paired': defaultPaired,
    'verbose': 0
}

defaultConfig = {
    'reference': None,
    'sequences': [],
    'optionsModule': defaultOptionsModule,
    'stageDefaults': stageDefaults,
    'pipeline': pipeline
}


def mkDir(dir):
    if not os.path.exists(dir):
        try:
            os.mkdir(dir, 0777)
        except IOError, e:
            sys.exit('%s\nFailed to make directory %s' % (e, dir))


def mkLink(source, target):
    try:
        os.symlink(source, target)
    except OSError, e:
        if e.errno != errno.EEXIST:
            sys.exit('%s\nFailed to create symlink %s from %s' %
                     (e, target, source))
            # or just raise?


def mkForceLink(source, target):
    """Create a symlink, overwriting any existing symlink."""
    if os.path.isfile(target):
        os.remove(target)
    os.symlink(source, target)


def initLog(options):
    logDir = options.pipeline['logDir']
    logFile = os.path.join(logDir, options.pipeline['logFile'])
    mkDir(logDir)
    loggerArgs = {}
    loggerArgs["file_name"] = logFile
    loggerArgs["level"] = logging.DEBUG
    loggerArgs["rotating"] = False
    loggerArgs["maxBytes"] = 20000
    loggerArgs["backupCount"] = 10
    loggerArgs["formatter"] = "%(asctime)s - %(message)s"
    proxy, mutex = make_shared_logger_and_proxy(setup_std_shared_logger,
                                                "NGS_pipeline", loggerArgs)
    return {'proxy': proxy, 'mutex': mutex}


# Look for a particular option in a stage, otherwise return the default 
def getStageOptions(options, stage, optionName):
    try:
        return options.stages[stage][optionName]
    except KeyError:
        return options.stageDefaults[optionName]


# returns the exit status of the job if possible otherwise None
def distributedCommand(stage, comm, options):
    time = getStageOptions(options, stage, 'walltime')
    mods = getStageOptions(options, stage, 'modules')
    queue = getStageOptions(options, stage, 'queue')
    mem = getStageOptions(options, stage, 'memInGB')
    try:
        literals = getStageOptions(options, stage, 'jobscript')
    except KeyError:
        literals = None
    logDir = options.pipeline['logDir']
    verbosity = options.pipeline['verbose']
    #script = PBS_Script(command=comm, walltime=time, name=stage, memInGB=mem,
    #                    queue=queue, moduleList=mods, logDir=logDir, literals=literals)
    #return script.runJobAndWait(stage, logDir, verbosity)
    job_command = SLURM_Job(command=comm, walltime=time, name=stage, memInGB=mem,
                            queue=queue, moduleList=mods, logDir=logDir)
    return job_command.run_job_and_wait(stage, verbosity)


# check the exit status of the command and if == 0 then write a checkpoint
# file to indicate success.
def runStageCheck(stage, flag_file, *args):
    status = runStage(stage, *args)
    if status == 0:
        open(flag_file, 'w').close()
    else:
        command = getCommand(stage, pipeline_options)
        commandStr = command(*args)
        print('Error: command failed: %s' % commandStr)


# returns exit status of the executed command or None
def runStage(stage, *args):
    command = getCommand(stage, pipeline_options)
    commandStr = command(*args)
    logStr = stage + ': ' + commandStr
    logInfo(logStr, pipeline_logger)
    if getStageOptions(pipeline_options, stage, 'distributed'):
        exitStatus = distributedCommand(stage, commandStr, pipeline_options)
        return exitStatus
    else:
        (stdoutStr, stderrStr, exitStatus) = shellCommand(commandStr)
        if exitStatus != 0:
            msg = ("Failed to run '%s'\n%s%sNon-zero exit status %s" %
                   (commandStr, stdoutStr, stderrStr, exitStatus))
            logInfo(msg, pipeline_logger)
        return exitStatus


# This converts a short-hand command string, such as:
#   'bwa aln -t 8 %ref %seq > %out'
# into:
#   'lambda x1, x2, x3: "bwa aln -t 8 %s %s > %s" % (x1, x2, x3)'
def commandToLambda(command):
    expanded, numPats = re.subn('%[^ ]*', '%s', command)
    args = []
    for n in range(numPats):
        args.append("x" + str(n))
    argsTuple = str(','.join(args))
    lamStr = 'lambda %s : "%s" %% (%s)' % (argsTuple, expanded, argsTuple)
    return lamStr


def getCommand(name, options):
    try:
        commandStr = getStageOptions(options, name, 'command')
        return eval(commandToLambda(commandStr))
    except KeyError:
        exit("command: %s, is not defined in the options file" % name)


def logInfo(msg, logger):
    with logger['mutex']:
        logger['proxy'].info(msg)


def splitPath(path):
    (prefix, base) = os.path.split(path)
    (name, ext) = os.path.splitext(base)
    return (prefix, name, ext)


# drop the .py suffix from a filename,
# otherwise return the name unchanged.
def drop_py_suffix(filename):
    prefix, suffix = os.path.splitext(filename)
    if suffix == '.py':
        return prefix
    else:
        return filename


# XXX should sanity check that all the required options are
# specified somwhere, either on command line or in config files.
def getOptions(args):
    options = Bag()
    options.pipeline = {}

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
                setattr(options, name, getattr(imported, name))

    # Command line options can override what is in the config files,
    # so these settings must be done _after_ reading the config files.

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

    return options


def mkLogFile(logDir, fullFilename, extension):
    prefix, name, ext = splitPath(fullFilename)
    return os.path.join(logDir, name + extension)


def mkTempFilename(file):
    return file + '.tmp'


# truncate a file to zero bytes, and preserve its original modification time
def zeroFile(file):
    if os.path.exists(file):
        # save the current time of the file
        timeInfo = os.stat(file)
        try:
            f = open(file, 'w')
        except IOError:
            pass
        else:
            f.truncate(0)
            f.close()
            # change the time of the file back to what it was
            os.utime(file, (timeInfo.st_atime, timeInfo.st_mtime))

pipeline_logger = None


def startLogger():
    global pipeline_logger
    pipeline_logger = initLog(pipeline_options)

pipeline_options = None


def setOptions(options):
    global pipeline_options
    pipeline_options = options
