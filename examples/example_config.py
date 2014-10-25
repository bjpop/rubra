pipeline = {
    "logDir": "log",
    "logFile": "pipeline.log",
    "procs": 2,
    "end": ["total"],
}

stageDefaults = {
    "distributed": True,
    "walltime": "00:10:00",
    "memInGB": 1,
    "queue": "batch",
    "modules": ["python-gcc"],
    #"jobscript": "# put jobscript stuff here",
}
stages = {
    "countLines": {
        "command": "wc -l %file > %out",
    },
    "total": {
        "command": "./test/total.py %files > %out",
    },
}
