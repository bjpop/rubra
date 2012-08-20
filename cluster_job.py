# Generate a PBS script for a job, and general utilities for
# waiting for a job to complete.

from shell_command import shellCommand
import sys
from time import sleep
from tempfile import NamedTemporaryFile
import os

# XXX maybe these values could be supplied in a config file?
QSTAT_MAX_TRIES = 5   # number of times to try qstat before failing
QSTAT_ERROR_DELAY = 1 # seconds to sleep while waiting for qstat to recover
QSTAT_DELAY = 10      # seconds to sleep while waiting for job to complete

# this assumes that qstat info for a job will stick around for a while after the job has finished.
def isJobCompleted(jobID):
   count = 0
   while True:
       (stdout, stderr, exitStatus) = shellCommand("qstat -f %s" % jobID)
       # qstat appears to have worked correctly, we can stop trying.
       if exitStatus == 0 or count >= QSTAT_MAX_TRIES:
           break
       count += 1
       sleep(QSTAT_ERROR_DELAY)
   if exitStatus != 0:
       #return (True, exitStatus)
       raise Exception("qstat -f %s returned non-zero exit status %d times, panicking" % (jobID, count))
   else:
       # try to fetch the exit status of the job command from the output of qstat.
       jobState = None
       exitStatus = None
       for line in stdout.split('\n'):
           ws = line.split()
           if len(ws) == 3:
               if ws[0] == 'job_state' and ws[1] == '=':
                   jobState = ws[2]
               elif ws[0] == 'exit_status' and ws[1] == '=' and ws[2].isdigit():
                   exitStatus = int(ws[2])
       if jobState.upper() == 'C':
           # Job has completed.
           return (True, exitStatus)
       else:
           # Job has not completed.
           return (False, exitStatus)

# returns exit status of job (or None if it can't be determined)
def waitForJobCompletion(jobID):
   isFinished, exitCode = isJobCompleted(jobID)
   while(not isFinished):
       sleep(QSTAT_DELAY)
       isFinished, exitCode = isJobCompleted(jobID)
   return exitCode

# returns exit status of job (or None if it can't be determined)
def runJobAndWait(script, stage, logDir='', verbose=0):
    jobID = script.launch()
    prettyJobID = jobID.split('.')[0]
    logFilename = os.path.join(logDir, stage + '.' + prettyJobID + '.pbs')
    with open(logFilename, 'w') as logFile:
        logFile.write(str(script))
    if verbose > 0:
        print('stage = %s, jobID = %s' % (stage, prettyJobID))
    return waitForJobCompletion(jobID)

# Generate a PBS script for a job.
class PBS_Script(object):
    def __init__(self, command, walltime=None, name=None, memInGB=None, queue='batch', moduleList=None, logDir=None):
        self.command = command
        self.queue = queue
        self.name = name
        self.memInGB = memInGB
        self.walltime = walltime
        self.moduleList = moduleList
        self.logDir = logDir

    # render the job script as a string.
    def __str__(self):
        script = ['#!/bin/bash']
        # XXX fixme
        # should include job id in the output name.
        # should use the proper log directory.
        script.append('#PBS -q %s' % self.queue)
        if self.logDir:
           script.append('#PBS -o %s' % self.logDir)
           script.append('#PBS -e %s' % self.logDir)
        # should put the name of the file in here if possible
        if self.name:
            script.append('#PBS -N %s' % self.name)
        if self.memInGB:
            if self.queue == 'smp':
                script.append('#PBS -l mem=%sgb' % self.memInGB)
            elif self.queue == 'terri':
                script.append('#PBS -l procs=8,ppn=8 pvmem=%sgb' % self.memInGB)
            else:
                script.append('#PBS -l pvmem=%sgb' % self.memInGB)
        if self.walltime:
            script.append('#PBS -l walltime=%s' % self.walltime)
        if type(self.moduleList) == list and len(self.moduleList) > 0:
            for item in self.moduleList:
               script.append('module load %s' % item)
        script.append('cd $PBS_O_WORKDIR')
        script.append(self.command)
        return '\n'.join(script) + '\n'

    # create a temporary file to store the job script and then
    # launch it with qsub.
    def launch(self):
        file = NamedTemporaryFile()
        file.write(str(self))
        file.flush()
        command = 'qsub ' + file.name
        (stdout, stderr, returnCode) = shellCommand(command)
        file.close()
        if returnCode == 0:
            return stdout
        else:
            raise(Exception('qsub command failed with exit status: ' + str(returnCode)))
