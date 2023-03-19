import os
import pathlib
import time
from datetime import datetime
import json


class Log:
    def __init__(self, content):
        self.unix = time.time()
        self.prettyTime = datetime.utcfromtimestamp(self.unix).strftime('%Y-%m-%d %H:%M:%S')
        self.content = str(content)
        self.obj = {
            "unix": self.unix,
            "prettyTime": self.prettyTime,
            "content": self.content
        }

    def prettify(self):
        return f"""Log event @ {self.unix}, or {self.prettyTime}
log content: {self.content}"""

    def __str__(self):
        return self.prettify()


class Logger:
    def __init__(self, path):
        root = os.path.dirname(os.path.abspath(path))
        self.folderPath = pathlib.Path(f"{root}/logs")
        self.filePath = self.folderPath / "logs.json"

        def rewriteLogs():
            with open(self.filePath, "w") as file:
                file.write('{"logs":[]}')

        if not self.filePath.exists():
            try:
                rewriteLogs()
            except FileNotFoundError:  # Directory does not exist
                os.mkdir(self.folderPath)
                rewriteLogs()

    def log(self, log):
        if type(log) != Log:
            log = Log(log)
        with open(self.filePath, "r") as file:
            oldData = json.load(file)
        with open(self.filePath, "w") as file:
            newLogs = oldData["logs"]
            newLogs.append(log.obj)
            newData = {"logs": newLogs}
            file.write(json.dumps(newData, indent=4))
