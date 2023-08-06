# This file is placed in the Public Domain.


"basic commands"


import threading
import time


from obj import Class, Config, Db, Object
from obj import find, fntime, format, get, save, update
from obh import Bus, Commands, getname, starttime


def reg():
    Commands.add(cmd)
    Commands.add(dlt)
    Commands.add(dne)
    Commands.add(flt)
    Commands.add(fnd)
    Commands.add(log)
    Commands.add(tdo)
    Commands.add(thr)
    Commands.add(upt)
    Commands.add(ver)


class Todo(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


Class.add(Todo)


class Log(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


Class.add(Log)


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


def cmd(event):
    event.reply(",".join(sorted(Commands.cmd)))


def dlt(event):
    if not event.args:
        event.reply("dlt <username>")
        return
    selector = {"user": event.args[0]}
    for _fn, o in find("user", selector):
        o._deleted = True
        save(o)
        event.reply("ok")
        break

def dne(event):
    if not event.args:
        return
    selector = {"txt": event.args[0]}
    for _fn, o in find("todo", selector):
        o._deleted = True
        save(o)
        event.reply("ok")
        break


def flt(event):
    try:
        index = int(event.args[0])
        event.reply(Bus.objs[index])
        return
    except (KeyError, TypeError, IndexError, ValueError):
        pass
    event.reply(" | ".join([getname(o) for o in Bus.objs]))


def fnd(event):
    if not event.args:
        db = Db()
        res = ",".join(
            sorted({x.split(".")[-1].lower() for x in db.types()}))
        if res:
            event.reply(res)
        else:
            event.reply("no types yet.")
        return
    bot = event.bot()
    otype = event.args[0]
    res = list(find(otype))
    if bot.cache:
        if len(res) > 3:
            bot.extend(event.channel, [x[1].txt for x in res])
            bot.say(event.channel, "%s left in cache, use !mre to show more" % bot.cache.size())
            return
    nr = 0
    for _fn, o in res:
        txt = "%s %s %s" % (str(nr), format(o), elapsed(time.time()-fntime(_fn)))
        nr += 1
        event.reply(txt)
    if not nr:
        event.reply("no result")


def log(event):
    if not event.rest:
        event.reply("log <txt>")
        return
    o = Log()
    o.txt = event.rest
    save(o)
    event.reply("ok")


def tdo(event):
    if not event.rest:
        nr = 0
        for _fn, o in find("todo"):
            event.reply("%s %s %s" % (nr, o.txt, elapsed(time.time() - fntime(_fn))))
            nr += 1
        if nr == 0:
            event.reply("no todo items yet.")
        return
    o = Todo()
    o.txt = event.rest
    save(o)
    event.reply("ok")


def thr(event):
    result = []
    for t in sorted(threading.enumerate(), key=lambda x: x.getName()):
        if str(t).startswith("<_"):
            continue
        o = Object()
        update(o, vars(t))
        if get(o, "sleep", None):
            up = o.sleep - int(time.time() - o.state.latest)
        else:
            up = int(time.time() - starttime)
        result.append((up, t.getName()))
    res = []
    for up, txt in sorted(result, key=lambda x: x[0]):
        res.append("%s/%s" % (txt, elapsed(up)))
    if res:
        event.reply(" ".join(res))


def upt(event):
    event.reply(elapsed(time.time()-starttime))


def ver(event):
    event.reply("%s %s" % (Config.name.upper(), Config.version or "1"))
