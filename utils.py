# Various useful utilities for the pipeline.

import os.path
import sys
import yaml
import subprocess
from ruffus.proxy_logger import *
import logging
import os
from shell_command import shellCommand
from cluster_job import (PBS_Script, runJobAndWait)
import re

# XXX I don't think the defaults really belong here.
defaultOptionsModule = 'pipeline_config'
defaultWalltime = None # use the default walltime of the scheduler
defaultModules = []
defaultQueue = 'batch'
defaultMemInGB = None # use the default mem of the scheduler
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

def initLog(options):
    logDir = options.pipeline['logDir']
    logFile = os.path.join(logDir, options.pipeline['logFile'])
    mkDir(logDir)
    loggerArgs={}
    loggerArgs["file_name"] = logFile
    loggerArgs["level"] = logging.DEBUG
    loggerArgs["rotating"] = False
    loggerArgs["maxBytes"]=20000
    loggerArgs["backupCount"]=10
    loggerArgs["formatter"]="%(asctime)s - %(message)s"
    (proxy, mutex) = make_shared_logger_and_proxy (setup_std_shared_logger, "NGS_pipeline", loggerArgs)
    return { 'proxy': proxy, 'mutex': mutex }

# Look for a particular option in a stage, otherwise return the result
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
    logDir = options.pipeline['logDir']
    verbosity = options.pipeline['verbose']
    script = PBS_Script(command=comm, walltime=time, name=stage, memInGB=mem, queue=queue, moduleList=mods, logDir=logDir)
    return runJobAndWait(script, stage, logDir, verbosity)

# check the exit status of the command and if == 0 then write a checkpoint file to indicate success.
def runStageCheck(stage, flag_file, logger, options, *args):
    status = runStage(stage, logger, options, *args)
    if status == 0:
        open(flag_file, 'w').close()
    else:
        command = getCommand(stage, options)
        commandStr = command(*args)
        print('Error: command failed: %s' % commandStr)

# returns exit status of the executed command or None
def runStage(stage, logger, options, *args):
    command = getCommand(stage, options)
    commandStr = command(*args)
    logStr = stage + ': ' + commandStr
    logInfo(logStr, logger)
    if getStageOptions(options, stage, 'distributed'):
        exitStatus = distributedCommand(stage, commandStr, options)
        return exitStatus
    else:
        (stdoutStr, stderrStr, exitStatus) = shellCommand(commandStr)
        if exitStatus != 0:
            msg = ("Failed to run '%s'\n%s%sNon-zero exit status %s" %
                   (commandStr, stdoutStr, stderrStr, exitStatus))
            logInfo(msg, logger)
        return exitStatus

# This converts a short-hand command string, such as:
#   'bwa aln -t 8 %ref %seq > %out'
# into:
#   'lambda x1, x2, x3: "bwa aln -t 8 %s %s > %s" % (x1, x2, x3)'
def commandToLambda(command):
    (expanded,numPats) = re.subn('%[^ ]*', '%s', command)
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
    with logger['mutex']: logger['proxy'].info(msg)

def splitPath(path):
    (prefix, base) = os.path.split(path)
    (name, ext) = os.path.splitext(base)
    return (prefix, name, ext)

def validateOptions(options):
    reference = options['reference']
    if not reference:
        exit('One reference file must be specified')
    sequences = options['sequences']
    if len(sequences) == 0:
        exit('At least one sequence file must be specified')
    return options

def getOptionsModule(args):
    if args.opts is not None:
        return args.opts
    else:
        return defaultOptionsModule

def getOptions(args):
    configModule = getOptionsModule(args)
    try:
        options = __import__(configModule)
    except ImportError:
        exit('Could not find configuation file: %s' % (configModule + '.py'))
    if args.style is not None:
        options.pipeline['style'] = args.style
    if args.verbose is not None:
        options.pipeline['verbose'] = args.verbose
    if args.force is not None:
        options.pipeline['force'] = args.force
    if args.end is not None:
        options.pipeline['end'] = args.end
    return options

def mkLogFile(logDir, fullFilename, extension):
    prefix,name,ext = splitPath(fullFilename)
    return os.path.join(logDir, name + extension)

def mkTempFilename(file):
    return file + '.tmp'

# truncate a file to zero bytes, and preserve its original modification time
def zeroFile(file):
    if os.path.exists(file):
        # save the current time of the file
        timeInfo = os.stat(file)
        try:
            f = open(file,'w')
        except IOError:
            pass
        else:
            f.truncate(0)
            f.close()
            # change the time of the file back to what it was
            os.utime(file,(timeInfo.st_atime, timeInfo.st_mtime))
