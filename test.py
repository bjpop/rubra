#!/bin/env python
# simple test for the job submission tools

from cluster_job import (PBS_Script, runJobAndWait)
from utils import mkDir

logDirName='log'
mkDir(logDirName)
script = PBS_Script(command='echo hello world', walltime='0:1:0', name='pipeline_test_job', memInGB=1, logDir=logDirName)
print('before job has run')
runJobAndWait(script, 'test_stage', logDir=logDirName, verbose=1)
print('after job has run')
