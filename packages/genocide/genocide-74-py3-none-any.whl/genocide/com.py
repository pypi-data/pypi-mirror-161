# This file is placed in the Public Domain.


"command"


from .obj import Object, get, register
from .hdl import Callbacks


def __dir__():
    return (
        "Commands",
        "dispatch"
    )


class Commands(Object):

    cmd = Object()

    @staticmethod
    def add(cmd):
        register(Commands.cmd, cmd.__name__, cmd)

    @staticmethod
    def get(cmd):
        return get(Commands.cmd, cmd)


    @staticmethod
    def remove(cmd):
        del Commands.cmd[cmd]


def dispatch(e):
    e.parse()
    f = Commands.get(e.cmd)
    if f:
        f(e)
        e.show()
    e.ready()


Callbacks.add("command", dispatch)
