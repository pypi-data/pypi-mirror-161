# This file is placed in the Public Domain.


"runtime"


import time


from .bus import Bus
from .dbs import cdir
from .evt import Command, Parsed
from .hdl import Handler
from .obj import Config, items, spl


def __dir__():
    return (
        "CLI",
        "Console",
        "boot",
        "init",
        "isopt",
        "starttime"
    )


starttime = time.time()


class Table():

    mod = {}

    @staticmethod
    def add(o):
        Table.mod[o.__name__] = o

    @staticmethod
    def get(nm):
        return Table.mod.get(nm, None)


class CLI(Handler):

    def __init__(self):
        Handler.__init__(self)
        Bus.add(self)

    def announce(self, txt):
        self.raw(txt)

    def cmd(self, txt):
        c = Command()
        c.channel = ""
        c.orig = repr(self)
        c.txt = txt
        self.handle(c)
        c.wait()

    def raw(self, txt):
        pass


class Console(CLI):

    def handle(self, e):
        Handler.handle(self, e)
        e.wait()

    def poll(self):
        e = Command()
        e.channel = ""
        e.cmd = ""
        e.txt = input("> ")
        e.orig = repr(self)
        if e.txt:
            e.cmd = e.txt.split()[0]
        return e


def boot(txt, mods="", doinit=True):
    cdir(Config.workdir)
    e = Parsed()
    e.parse(txt)
    for k, v in items(e):
        setattr(Config, k, v)
    for o in Config.opts:
        if o == "c":
            Config.console = True
        if o == "d":
            Config.daemon = True
        if o == "v":
            Config.verbose = True
    mns = mods or Config.sets.mod
    init(mns, "reg")
    if doinit:
        init(mns, "init")
    return e


def init(mns, cmds="init"):
    for mn in spl(mns):
        mod = Table.get(mn)
        if not mod:
            continue
        for cmd in spl(cmds):
            c = getattr(mod, cmd, None)
            if not c:
                continue
            c()

def isopt(opts):
    for o in opts:
        if o in Config.opts:
            return True
