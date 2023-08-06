# This file is placed in the Public Domain.


"event handler"


import datetime
import queue
import threading
import time
import types


from obj import Class, Config, Default, Object, get, register


def __dir__():
    return (
        'Bus',
        'CLI',
        'Callbacks',
        'Class',
        'Command',
        'Commands',
        'Config',
        'Console',
        'Event',
        'Handler',
        'Repeater',
        'Table',
        'Thread',
        'Timer',
        'dispatch',
        "elapsed",
        'getname',
        "get_day",
        "get_time"
        'launch',
        'starttime',
    )


year_formats = [
    "%b %H:%M",
    "%b %H:%M:%S",
    "%a %H:%M %Y",
    "%a %H:%M",
    "%a %H:%M:%S",
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d-%m",
    "%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    "%d-%m %H:%M:%S",
    "%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%d-%m-%Y %H:%M",
    "%d-%m %H:%M",
    "%m-%d %H:%M",
    "%H:%M:%S",
    "%H:%M"
]


starttime = time.time()



class Bus(Object):

    objs = []

    @staticmethod
    def add(o):
        if repr(o) not in [repr(x) for x in Bus.objs]:
            Bus.objs.append(o)

    @staticmethod
    def announce(txt):
        for o in Bus.objs:
            o.announce(txt)

    @staticmethod
    def byorig(orig):
        for o in Bus.objs:
            if repr(o) == orig:
                return o

    @staticmethod
    def say(orig, channel, txt):
        o = Bus.byorig(orig)
        if o:
            o.say(channel, txt)


class Callbacks(Object):

    cbs = Object()
    errors = []
    threaded = True

    @staticmethod
    def add(name, cb):
        register(Callbacks.cbs, name, cb)

    @staticmethod
    def callback(e):
        f = Callbacks.get(e.type)
        if not f:
            e.ready()
            return
        try:
            f(e)
        except Exception as ex:
            if Callbacks.threaded:
                Callbacks.errors.append(ex)
                e._exc = ex
                e.ready()
            else:
                raise

    @staticmethod
    def get(cmd):
        return get(Callbacks.cbs, cmd)

    @staticmethod
    def dispatch(e):
        if Callbacks.threaded:
            e._thrs.append(launch(Callbacks.callback, e, name=e.txt))
            return
        Callbacks.callback(e)


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


class Event(Object):

    def __init__(self):
        super().__init__()
        self._exc = None
        self._ready = threading.Event()
        self._result = []
        self._thrs = []
        self.args = []
        self.channel = ""
        self.cmd = ""
        self.gets = Default()
        self.index = 0
        self.opts = ""
        self.orig = ""
        self.rest = ""
        self.sets = Default()
        self.otxt = ""
        self.txt = ""
        self.type = "event"

    def bot(self):
        return Bus.byorig(self.orig)

    def parse(self, txt=None, orig=None):
        self.otxt = txt or self.txt
        self.orig = orig or self.orig
        spl = self.otxt.split()
        args = []
        _nr = -1
        for w in spl:
            _nr += 1
            if w.startswith("-"):
                try:
                    self.index = int(w[1:])
                except ValueError:
                    self.opts += w[1:2]
                continue
            if _nr == 0:
                self.cmd = w
                continue
            try:
                k, v = w.split("==")
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


class Handler(Object):

    def __init__(self):
        Object.__init__(self)
        self.cache = Object()
        self.cfg = Config()
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




class Table():

    mod = {}

    @staticmethod
    def add(o):
        Table.mod[o.__name__] = o

    @staticmethod
    def get(nm):
        return Table.mod.get(nm, None)


class Thread(threading.Thread):

    def __init__(self, func, name, *args, daemon=True):
        super().__init__(None, self.run, name, (), {}, daemon=daemon)
        self._exc = None
        self._evt = None
        self.name = name
        self.queue = queue.Queue()
        self.queue.put_nowait((func, args))
        self._result = None

    def __iter__(self):
        return self

    def __next__(self):
        for k in dir(self):
            yield k

    def join(self, timeout=None):
        super().join(timeout)
        return self._result

    def run(self):
        func, args = self.queue.get()
        if args:
            self._evt = args[0]
        self.setName(self.name)
        self._result = func(*args)
        return self._result


class Timer(Object):

    def __init__(self, sleep, func, *args, name=None):
        super().__init__()
        self.args = args
        self.func = func
        self.sleep = sleep
        self.name = name or ""
        self.state = Object()
        self.timer = None

    def run(self):
        self.state.latest = time.time()
        launch(self.func, *self.args)

    def start(self):
        if not self.name:
            self.name = getname(self.func)
        timer = threading.Timer(self.sleep, self.run)
        timer.setName(self.name)
        timer.setDaemon(True)
        timer.sleep = self.sleep
        timer.state = self.state
        timer.state.starttime = time.time()
        timer.state.latest = time.time()
        timer.func = self.func
        timer.start()
        self.timer = timer
        return timer

    def stop(self):
        if self.timer:
            self.timer.cancel()


class Repeater(Timer):

    def run(self):
        thr = launch(self.start)
        super().run()
        return thr


class CLI(Handler):

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

    def forever(self):
        while 1:
            time.sleep(1.0)


def dispatch(e):
    e.parse()
    f = Commands.get(e.cmd)
    if f:
        f(e)
        e.show()
    e.ready()


def day():
    return str(datetime.datetime.today()).split()[0]


def elapsed(seconds, short=True):
    txt = ""
    nsec = float(seconds)
    year = 365*24*60*60
    week = 7*24*60*60
    nday = 24*60*60
    hour = 60*60
    minute = 60
    years = int(nsec/year)
    nsec -= years*year
    weeks = int(nsec/week)
    nsec -= weeks*week
    nrdays = int(nsec/nday)
    nsec -= nrdays*nday
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    sec = nsec - minutes*minute
    if years:
        txt += "%sy" % years
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += "%sd" % nrdays
    if years and short and txt:
        return txt
    if hours:
        txt += "%sh" % hours
    if nrdays and short and txt:
        return txt
    if minutes:
        txt += "%sm" % minutes
    if hours and short and txt:
        return txt
    if sec == 0:
        txt += "0s"
    else:
        txt += "%ss" % int(sec)
    txt = txt.strip()
    return txt


def getname(o):
    t = type(o)
    if isinstance(t, types.ModuleType):
        return o.__name__
    if "__self__" in dir(o):
        return "%s.%s" % (o.__self__.__class__.__name__, o.__name__)
    if "__class__" in dir(o) and "__name__" in dir(o):
        return "%s.%s" % (o.__class__.__name__, o.__name__)
    if "__class__" in dir(o):
        return o.__class__.__name__
    if "__name__" in dir(o):
        return o.__name__
    return None


def get_time(daystr):
    for f in year_formats:
        try:
            t = time.mktime(time.strptime(daystr, f))
            return t
        except Exception:
            pass


def launch(func, *args, **kwargs):
    name = kwargs.get("name", getname(func))
    t = Thread(func, name, *args)
    t.start()
    return t


def today():
    return datetime.datetime.today().timestamp()


def to_day(daystring):
    line = ""
    daystr = str(daystring)
    for word in daystr.split():
        if "-" in word:
            line += word + " "
        elif ":" in word:
            line += word
    if "-" not in line:
        line = day() + " " + line
    try:
        return get_time(line.strip())
    except ValueError:
        pass


Callbacks.add("command", dispatch)
