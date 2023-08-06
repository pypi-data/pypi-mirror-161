# This file is placed in the Public Domain.


"log"


from .com import Commands
from .dbs import Class
from .obj import Object, save


def reg():
    Class.add(Log)
    Commands.add(log)


def rem():
    Class.remove(Log)
    Commands.remove(log)


class Log(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


def log(event):
    if not event.rest:
        event.reply("log <txt>")
        return
    o = Log()
    o.txt = event.rest
    save(o)
    event.reply("ok")
