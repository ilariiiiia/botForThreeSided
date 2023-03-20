import os
import pathlib
import time
from datetime import datetime
import json
from json import JSONDecodeError

import discord
from discord.ext.commands.context import Context


class Log:
    def __init__(self, content, props):
        self.unix = time.time()
        self.prettyTime = datetime.utcfromtimestamp(self.unix).strftime('%Y-%m-%d %H:%M:%S')
        self.content = str(content)
        self.props = props

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

        if not self.filePath.exists():
            try:
                self.rewriteLogs()
            except FileNotFoundError:  # Directory does not exist
                os.mkdir(self.folderPath)
                self.rewriteLogs()

    def rewriteLogs(self):
        with open(self.filePath, "w") as file:
            file.write('{"logs":[]}')

    def log(self, message, props=None):
        log = Log(message, props=props)
        with open(self.filePath, "r") as file:
            try:
                oldData = json.load(file)
            except JSONDecodeError:
                self.rewriteLogs()
                oldData = json.load(file)
        with open(self.filePath, "w") as file:
            newLogs = oldData["logs"]
            newLogs.append(log.__dict__)
            newData = {"logs": newLogs}
            file.write(json.dumps(newData, indent=4))

    @staticmethod
    def contextToObject(ctx: Context):
        return {
            "type": "context",
            "message": Logger.messageToObject(ctx.message)
        }

    @staticmethod
    def memberToObject(member: discord.Member):
        return {
            "avatar": member.avatar.url if not member.bot else None,
            "name": member.name,
            "roles": [str(x) for x in member.roles]
        }

    @staticmethod
    def messageToObject(message: discord.Message):
        return {
            "author": Logger.memberToObject(message.author),
            "id": message.id,
            "content": message.content,
            "channelID": message.channel.id,
            "channelName": message.channel.name
        }
