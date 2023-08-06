# This file is placed in the Public Domain.


"event"


import threading


from .bus import Bus
from .obj import Default, Object


def __dir__():
    return (
        "Command",
        "Event",
        "Parsed"
    )



class Parsed(Object):

    def __init__(self):
        Object.__init__(self)
        self.args = []
        self.cmd = ""
        self.gets = Default()
        self.index = 0
        self.opts = ""
        self.rest = ""
        self.sets = Default()
        self.toskip = Default()
        self.otxt = ""
        self.txt = ""

    def parse(self, txt=None):
        self.otxt = txt or self.txt
        spl = self.otxt.split()
        args = []
        _nr = -1
        for w in spl:
            if w.startswith("-"):
                try:
                    self.index = int(w[1:])
                except ValueError:
                    self.opts += w[1:2]
                continue
            _nr += 1
            if _nr == 0:
                self.cmd = w
                continue
            try:
                k, v = w.split("==")
                if v.endswith("-"):
                    v = v[:-1]
                    self.toskip[v] = ""
                self.gets[k] = v
                continue
            except ValueError:
                pass
            try:
                k, v = w.split("=")
                self.sets[k] = v
                continue
            except ValueError:
                args.append(w)
        if args:
            self.args = args
            self.rest = " ".join(args)
            self.txt = self.cmd + " " + self.rest
        else:
            self.txt = self.cmd


class Event(Parsed):

    def __init__(self):
        Parsed.__init__(self)
        self._exc = None
        self._ready = threading.Event()
        self._result = []
        self._thrs = []
        self.cmd = ""
        self.channel = ""
        self.orig = None
        self.type = "event"

    def bot(self):
        return Bus.byorig(self.orig)

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self._result.append(txt)

    def show(self):
        assert self.orig
        for txt in self._result:
            Bus.say(self.orig, self.channel, txt)

    def wait(self):
        self._ready.wait()
        for thr in self._thrs:
            thr.join()
        return self._result


class Command(Event):

    def __init__(self):
        Event.__init__(self)
        self.type = "command"
