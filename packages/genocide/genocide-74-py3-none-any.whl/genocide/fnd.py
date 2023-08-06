# This file is placed in the Public Domain.


"find"


import time


from .com import Commands
from .dbs import Db, find, fntime
from .obj import format
from .utl import elapsed


def reg():
    Commands.add(fnd)


def rem():
    Commands.remove(fnd)


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
    res = list(find(otype, event.gets))
    if bot.cache:
        if len(res) > 3:
            bot.extend(event.channel, [x[1].txt for x in res])
            bot.say(event.channel, "%s left in cache, use !mre to show more" % bot.cache.size())
            return
    nr = 0
    for _fn, o in res:
        txt = "%s %s %s" % (str(nr), format(o, event.sets.keys, event.toskip), elapsed(time.time()-fntime(_fn)))
        nr += 1
        event.reply(txt)
    if not nr:
        event.reply("no result")
