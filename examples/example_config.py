pipeline = {
    "log_dir": "log",
    "script_dir": "scripts",
    "log_file": "pipeline.log",
    "procs": 2,
    "end": ["total"],
}

"""
SLURM options:

--account=name          Charge job to specified accounts
--exclusive             Allocate nodenumber of tasks to invoke on each nodes 
                        in exclusive mode when cpu consumable resource is enabled
--mem=MB                Minimum amount of real memory
--mem-per-cpu=MB        Maximum amount of real memory per allocated cpu required by a job
--mincpus=n             Minimum number of logical processors (threads) per node
--nodes=N               Number of nodes on which to run (N = min[-max])
--ntasks-per-node=n     Number of tasks to invoke on each node
--partition=partition   Partition requested
--reservation=name      Allocate resources from named reservation
--time=hours:minutes    Set a maximum job wallclock time
--ntasks=n              Number of tasks
--mail-type             Notify user by email when certain event types occur. Valid 
                        type values are BEGIN, END, FAIL, REQUEUE, and ALL 
                        (any state change)
"""

stageDefaults = {
    "distributed": True,
    "options": "--time=0:10 --mem=1024 --partition=main",
    "pre_script": "",
    "post_script": "",
}
stages = {
    "count_lines": {
        "command": "wc -l %file > %out",
    },
    "total": {
        "pre_script": "module load python-gcc",
        "command": "./test/total.py %files > %out",
    },
}
