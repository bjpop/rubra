pipeline = {
   "logDir": "log",
   "logFile": "pipeline.log",
   "style": "print",
   "procs": 2,
   "verbose": 1,
   "end": ["total"],
   "force": [],
   "rebuild" : "fromstart"
}
stageDefaults = {
   "distributed": True,
   "walltime": "00:10:00",
   "memInGB": 1,
   "queue": "batch",
   "modules": ["python-gcc"]
}
stages = {
   "countLines": {
      "command": "wc -l %file > %out",
   },
   "total": {
       "command": "./total.py %files > %out",
   },
}
