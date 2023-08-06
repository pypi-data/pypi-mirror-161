# This file is placed in the Public Domain.


"handler"


import queue
import threading
import time


from .bus import Bus
from .obj import Object, get, register
from .thr import launch


def __dir__():
    return (
        'Callbacks',
        'Handler',
    )



class Callbacks(Object):

    cbs = Object()

    @staticmethod
    def add(name, cb):
        register(Callbacks.cbs, name, cb)

    @staticmethod
    def callback(e):
        f = Callbacks.get(e.type)
        if not f:
            e.ready()
            return
        f(e)

    @staticmethod
    def get(cmd):
        return get(Callbacks.cbs, cmd)

    @staticmethod
    def dispatch(e):
        Callbacks.callback(e)


class Handler(Object):

    def __init__(self):
        Object.__init__(self)
        self.cache = Object()
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        self.threaded = False
        Bus.add(self)

    def announce(self, txt):
        self.raw(txt)

    def forever(self):
        while 1:
            time.sleep(1.0)

    def handle(self, e):
        Callbacks.dispatch(e)

    def loop(self):
        while not self.stopped.isSet():
            self.handle(self.poll())

    def poll(self):
        return self.queue.get()

    def put(self, e):
        self.queue.put_nowait(e)

    def raw(self, txt):
        pass

    def register(self, typ, cb):
        Callbacks.add(typ, cb)

    def restart(self):
        self.stop()
        self.start()

    def say(self, channel, txt):
        self.raw(txt)

    def start(self):
        self.stopped.clear()
        launch(self.loop)

    def stop(self):
        self.stopped.set()


def dispatch(e):
    pass


Callbacks.add("event", dispatch)
