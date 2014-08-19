# Various useful utilities for the pipeline.

import re
import subprocess
from logger import get_logger, log_info
from config import get_config, get_command, get_stage_options
from ruffus.drmaa_wrapper import run_job, error_drmaa_job
import drmaa

GLOBAL_DRMAA_SESSION = None

def get_global_drmaa_session():
    return GLOBAL_DRMAA_SESSION

def finalize_drmaa_session():
    global GLOBAL_DRMAA_SESSION
    if GLOBAL_DRMAA_SESSION is not None:
        GLOBAL_DRMAA_SESSION.exit()

# returns exit status of the executed command or None
def run_stage(stage, *args):
    global_config = get_config()
    command = get_command(stage, global_config)
    commandStr = command(*args)
    logStr = stage + ': ' + commandStr
    global_logger = get_logger()
    log_info(logStr, global_logger)
    if get_stage_options(global_config, stage, 'distributed'):
        distributedCommand(stage, commandStr, global_config)
    else:
        (stdoutStr, stderrStr, exitStatus) = shell_command(commandStr)
        if exitStatus != 0:
            msg = ("Failed to run '%s'\n%s%sNon-zero exit status %s" %
                   (commandStr, stdoutStr, stderrStr, exitStatus))
            raise Exception(msg)

# XXX need to set walltime and queue and do something about modules
def distributedCommand(stage, command, options):

    global GLOBAL_DRMAA_SESSION

    # initialise drmaa session the first time this is called
    if GLOBAL_DRMAA_SESSION is None:
        try:
            GLOBAL_DRMAA_SESSION = drmaa.Session()
            GLOBAL_DRMAA_SESSION.initialize()
        except RuntimeError as e:
            print(e)
            exit(1)

    job_options = get_stage_options(options, stage, 'options')
    job_pre_script = get_stage_options(options, stage, 'pre_script')
    job_post_script = get_stage_options(options, stage, 'post_script')

    if GLOBAL_DRMAA_SESSION is None:
        exit("drmaa_session not correctly intialised")

    command_script = ''
    if job_pre_script:
        command_script += job_pre_script + '\n'
    command_script += command + '\n'
    if job_post_script:
        command_script += job_post_script + '\n'

    try:
        stdout_res = ''
        stderr_res = ''
        global_logger = get_logger()
        stdout_res, stderr_res = \
            run_job(command_script,
                job_name = stage,
                logger = global_logger['proxy'],
                drmaa_session = GLOBAL_DRMAA_SESSION,
                run_locally = False,
                retain_job_scripts = True,
                job_script_directory = options.pipeline['script_dir'],
                job_other_options = job_options)

    except error_drmaa_job as err:
        raise Exception("\n".join(map(str, ["Failed to run:", 
            command, err, stdout_res, stderr_res])))

def shell_command(command):
    '''Run a shell command and capture its stdout, stderr and exit status.'''
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=True)
    stdoutStr, stderrStr = process.communicate()
    return(stdoutStr, stderrStr, process.returncode)
