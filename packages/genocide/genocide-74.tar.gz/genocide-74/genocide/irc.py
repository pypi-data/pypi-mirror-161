# This file is placed in the Public Domain.


"internet relay chat"


import base64
import os
import queue
import socket
import ssl
import textwrap
import threading
import time
import _thread


from .bus import Bus
from .com import Commands
from .dbs import Class, find, last, locked, save
from .evt import Event
from .obj import Config, Object
from .obj import edit, format, update
from .hdl import Handler
from .thr import launch


def __dir__():
    return (
        "Config",
        "Event",
        "IRC",
        "DCC",
    )


def init():
    i = IRC()
    i.start()
    return i


def reg():
    Commands.add(cfg)
    Commands.add(dlt)
    Commands.add(met)
    Commands.add(mre)
    Commands.add(pwd)


def rem():
    Commands.remove(cfg)
    Commands.remove(dlt)
    Commands.remove(met)
    Commands.remove(mre)
    Commands.remove(pwd)


saylock = _thread.allocate_lock()


class NoUser(Exception):

    pass



name = Config.name


class Config(Config):

    cc = "!"
    channel = "#%s" % name
    nick = name
    password = ""
    port = 6667
    realname = name
    sasl = False
    server = "localhost"
    servermodes = ""
    sleep = 60
    username = name
    users = False

    def __init__(self):
        super().__init__()
        self.cc = Config.cc
        self.channel = Config.channel
        self.nick = Config.nick or name
        self.password = Config.password
        self.port = Config.port
        self.realname = Config.realname
        self.sasl = Config.sasl
        self.server = Config.server
        self.servermodes = Config.servermodes
        self.sleep = Config.sleep
        self.username = Config.username
        self.users = Config.users


Class.add(Config)


class IEvent(Event):

    def __init__(self):
        Event.__init__(self)
        self.args = []
        self.arguments = []
        self.channel = ""
        self.command = ""
        self.nick = ""
        self.origin = ""
        self.rawstr = ""
        self.sock = None
        self.type = "event"
        self.txt = ""


class TextWrap(textwrap.TextWrapper):

    def __init__(self):
        super().__init__()
        self.break_long_words = False
        self.drop_whitespace = True
        self.fix_sentence_endings = True
        self.replace_whitespace = True
        self.tabsize = 4
        self.width = 450


class Output(Object):

    cache = Object()

    def __init__(self):
        Object.__init__(self)
        self.oqueue = queue.Queue()
        self.dostop = threading.Event()

    def dosay(self, channel, txt):
        raise NotImplementedError

    def extend(self, channel, txtlist):
        if channel not in self.cache:
            self.cache[channel] = []
        self.cache[channel].extend(txtlist)

    def get(self, channel):
        try:
            return self.cache[channel].pop(0)
        except IndexError:
            pass

    def oput(self, channel, txt):
        self.oqueue.put_nowait((channel, txt))

    def output(self):
        while not self.dostop.isSet():
            (channel, txt) = self.oqueue.get()
            if self.dostop.isSet():
                break
            wrapper = TextWrap()
            txtlist = wrapper.wrap(txt)
            c = -1
            if len(txtlist) > 3:
                self.extend(channel, txtlist)
                self.dosay(channel, "%s put in cache, use !mre to show more" % len(txtlist))
                continue
            for t in txtlist:
                c += 1
                self.dosay(channel, t)

    def size(self, n):
        if n in self.cache:
            return len(self.cache[n])
        return 0

    def start(self):
        self.dostop.clear()
        launch(self.output)
        return self

    def stop(self):
        self.dostop.set()
        self.oqueue.put_nowait((None, None))


class IRC(Handler, Output):


    def __init__(self):
        Handler.__init__(self)
        Output.__init__(self)
        self.buffer = []
        self.cfg = Config()
        self.connected = threading.Event()
        self.channels = []
        self.errors = []
        self.joined = threading.Event()
        self.keeprunning = False
        self.outqueue = queue.Queue()
        self.sock = None
        self.speed = "slow"
        self.state = Object()
        self.state.needconnect = False
        self.state.error = ""
        self.state.last = 0
        self.state.lastline = ""
        self.state.nrconnect = 0
        self.state.nrerror = 0
        self.state.nrsend = 0
        self.state.pongcheck = False
        self.threaded = False
        self.users = Users()
        self.zelf = ""
        self.register("903", h903)
        self.register("904", h903)
        self.register("AUTHENTICATE", AUTH)
        self.register("CAP", CAP)
        self.register("ERROR", ERROR)
        self.register("LOG", LOG)
        self.register("NOTICE", NOTICE)
        self.register("PRIVMSG", PRIVMSG)
        self.register("QUIT", QUIT)
        Bus.add(self)

    def announce(self, txt):
        for channel in self.channels:
            self.say(channel, txt)

    @locked(saylock)
    def command(self, cmd, *args):
        if not args:
            self.raw(cmd)
        elif len(args) == 1:
            self.raw("%s %s" % (cmd.upper(), args[0]))
        elif len(args) == 2:
            self.raw("%s %s :%s" % (cmd.upper(), args[0], " ".join(args[1:])))
        elif len(args) >= 3:
            self.raw(
                "%s %s %s :%s" % (cmd.upper(),
                                  args[0],
                                  args[1],
                                  " ".join(args[2:]))
            )
        if (time.time() - self.state.last) < 4.0:
            time.sleep(4.0)
        self.state.last = time.time()

    def connect(self, server, port=6667):
        self.connected.clear()
        if self.cfg.password:
            self.cfg.sasl = True
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
            ctx.check_hostname = False
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock = ctx.wrap_socket(sock)
            self.sock.connect((server, port))
            self.raw("CAP LS 302")
        else:
            addr = socket.getaddrinfo(server, port, socket.AF_INET)[-1][-1]
            self.sock = socket.create_connection(addr)
        if self.sock:
            os.set_inheritable(self.fileno(), os.O_RDWR)
            self.sock.setblocking(True)
            self.sock.settimeout(180.0)
            self.connected.set()
            return True
        return False

    def disconnect(self):
        self.sock.shutdown(2)

    def doconnect(self, server, nck, port=6667):
        self.state.nrconnect = 0
        while 1:
            self.state.nrconnect += 1
            try:
                if self.connect(server, port):
                    break
            except Exception as ex:
                self.errors.append(ex)
            time.sleep(self.cfg.sleep)
        self.logon(server, nck)

    def dosay(self, channel, txt):
        txt = str(txt).replace("\n", "")
        txt = txt.replace("  ", " ")
        self.command("PRIVMSG", channel, txt)

    def event(self, txt, origin=None):
        if not txt:
            return
        e = self.parsing(txt)
        cmd = e.command
        if cmd == "PING":
            self.state.pongcheck = True
            self.command("PONG", e.txt or "")
        elif cmd == "PONG":
            self.state.pongcheck = False
        if cmd == "001":
            self.state.needconnect = False
            if self.cfg.servermodes:
                self.raw("MODE %s %s" % (self.cfg.nick, self.cfg.servermodes))
            self.zelf = e.args[-1]
            self.joinall()
        elif cmd == "002":
            self.state.host = e.args[2][:-1]
        elif cmd == "366":
            self.joined.set()
        elif cmd == "433":
            nck = self.cfg.nick + "_"
            self.raw("NICK %s" % nck)
        return e

    def fileno(self):
        return self.sock.fileno()

    def joinall(self):
        for channel in self.channels:
            self.command("JOIN", channel)

    def keep(self):
        while 1:
            self.connected.wait()
            self.keeprunning = True
            time.sleep(self.cfg.sleep)
            self.state.pongcheck = True
            self.command("PING", self.cfg.server)
            time.sleep(10.0)
            if self.state.pongcheck:
                #self.keeprunning = False
                self.restart()

    def logon(self, server, nck):
        self.raw("NICK %s" % nck)
        self.raw(
            "USER %s %s %s :%s"
            % (self.cfg.username,
               server,
               server,
               self.cfg.realname or "bot")
        )

    def parsing(self, txt):
        rawstr = str(txt)
        rawstr = rawstr.replace("\u0001", "")
        rawstr = rawstr.replace("\001", "")
        o = IEvent()
        o.rawstr = rawstr
        o.command = ""
        o.arguments = []
        arguments = rawstr.split()
        if arguments:
            o.origin = arguments[0]
        else:
            o.origin = self.cfg.server
        if o.origin.startswith(":"):
            o.origin = o.origin[1:]
            if len(arguments) > 1:
                o.command = arguments[1]
                o.type = o.command
            if len(arguments) > 2:
                txtlist = []
                adding = False
                for arg in arguments[2:]:
                    if arg.count(":") <= 1 and arg.startswith(":"):
                        adding = True
                        txtlist.append(arg[1:])
                        continue
                    if adding:
                        txtlist.append(arg)
                    else:
                        o.arguments.append(arg)
                o.txt = " ".join(txtlist)
        else:
            o.command = o.origin
            o.origin = self.cfg.server
        try:
            o.nick, o.origin = o.origin.split("!")
        except ValueError:
            o.nick = ""
        target = ""
        if o.arguments:
            target = o.arguments[0]
        if target.startswith("#"):
            o.channel = target
        else:
            o.channel = o.nick
        if not o.txt:
            o.txt = rawstr.split(":", 2)[-1]
        if not o.txt and len(arguments) == 1:
            o.txt = arguments[1]
        spl = o.txt.split()
        if len(spl) > 1:
            o.args = spl[1:]
        o.type = o.command
        o.orig = repr(self)
        o.txt = o.txt.strip()
        return o

    def poll(self):
        self.connected.wait()
        if not self.buffer:
            try:
                self.some()
            except ConnectionResetError as ex:
                e = IEvent()
                e.txt = ex.args[0]
                self.stop()
                return e
        if self.buffer:
            return self.event(self.buffer.pop(0))

    def raw(self, txt):
        txt = txt.rstrip()
        if not txt.endswith("\r\n"):
            txt += "\r\n"
        txt = txt[:512]
        txt += "\n"
        txt = bytes(txt, "utf-8")
        if self.sock:
            try:
                self.sock.send(txt)
            except BrokenPipeError:
                self.stop()
        self.state.last = time.time()
        self.state.nrsend += 1

    def reconnect(self):
        self.disconnect()
        self.connected.clear()
        self.joined.clear()
        self.doconnect(self.cfg.server, self.cfg.nick, int(self.cfg.port))

    def say(self, channel, txt):
        self.oput(channel, txt)

    def some(self):
        self.connected.wait()
        if not self.sock:
            return
        inbytes = self.sock.recv(512)
        txt = str(inbytes, "utf-8")
        if txt == "":
            raise ConnectionResetError
        self.state.lastline += txt
        splitted = self.state.lastline.split("\r\n")
        for s in splitted[:-1]:
            self.buffer.append(s)
        self.state.lastline = splitted[-1]

    def start(self):
        last(self.cfg)
        if self.cfg.channel not in self.channels:
            self.channels.append(self.cfg.channel)
        self.connected.clear()
        self.joined.clear()
        Output.start(self)
        Handler.start(self)
        launch(self.doconnect, self.cfg.server or "localhost", self.cfg.nick or "hx", int(self.cfg.port or "6667"))
        if not self.keeprunning:
            launch(self.keep)

    def stop(self):
        try:
            self.sock.shutdown(2)
        except OSError:
            pass
        Handler.stop(self)

    def wait(self):
        self.joined.wait()


def AUTH(event):
    time.sleep(1.0)
    bot = event.bot()
    bot.raw("AUTHENTICATE %s" % bot.cfg.password)


def CAP(event):
    time.sleep(1.0)
    bot = event.bot()
    if bot.cfg.password and "ACK" in event.arguments:
        bot.raw("AUTHENTICATE PLAIN")
    else:
        bot.raw("CAP REQ :sasl")


def h903(event):
    time.sleep(1.0)
    bot = event.bot()
    bot.raw("CAP END")


def h904(event):
    time.sleep(1.0)
    bot = event.bot()
    bot.raw("CAP END")


def ERROR(event):
    bot = event.bot()
    bot.state.nrerror += 1
    bot.state.error = event.txt


def KILL(event):
    pass


def LOG(event):
    pass


def NOTICE(event):
    bot = event.bot()
    if event.txt.startswith("VERSION"):
        txt = "\001VERSION %s %s - %s\001" % (
            "op",
            bot.cfg.version,
            bot.cfg.username,
        )
        bot.command("NOTICE", event.channel, txt)


def PRIVMSG(event):
    if event.txt:
        bot = event.bot()
        if event.txt[0] in [bot.cfg.cc, "!",]:
            event.txt = event.txt[1:]
        elif event.txt.startswith("%s:" % bot.cfg.nick):
            event.txt = event.txt[len(bot.cfg.nick)+1:]
        else:
            return
        if bot.cfg.users and not bot.users.allowed(event.origin, "USER"):
            return
        splitted = event.txt.split()
        splitted[0] = splitted[0].lower()
        event.txt = " ".join(splitted)
        event.type = "command"
        bot.handle(event)


def QUIT(event):
    bot = event.bot()
    if event.orig and event.orig in bot.zelf:
        bot.reconnect()


class User(Object):

    def __init__(self, val=None):
        super().__init__()
        self.user = ""
        self.perms = []
        if val:
            update(self, val)


Class.add(User)


class Users(Object):

    userhosts = Object()

    def allowed(self, origin, perm):
        perm = perm.upper()
        origin = getattr(self.userhosts, origin, origin)
        user = self.get_user(origin)
        if user:
            if perm in user.perms:
                return True
        return False

    def delete(self, origin, perm):
        for user in self.get_users(origin):
            try:
                user.perms.remove(perm)
                save(user)
                return True
            except ValueError:
                pass

    def get_users(self, origin=""):
        s = {"user": origin}
        return find("user", s)

    def get_user(self, origin):
        u = list(self.get_users(origin))
        if u:
            return u[-1][-1]

    def perm(self, origin, permission):
        user = self.get_user(origin)
        if not user:
            raise NoUser(origin)
        if permission.upper() not in user.perms:
            user.perms.append(permission.upper())
            save(user)
        return user


Class.add(Users)


def cfg(event):
    c = Config()
    last(c)
    if not event.sets:
        event.reply(format(c, skip="realname,sleep,username"))
        return
    edit(c, event.sets)
    save(c)
    event.reply("ok")


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

def met(event):
    if not event.args:
        event.reply("met <userhost>")
        return
    user = User()
    user.user = event.rest
    user.perms = ["USER"]
    save(user)
    event.reply("ok")


def mre(event):
    if not event.channel:
        event.reply("channel is not set.")
        return
    bot = event.bot()
    if "cache" not in dir(bot):
        event.reply("bot is missing cache")
        return
    if event.channel not in bot.cache:
        event.reply("no output in %s cache." % event.channel)
        return
    for _x in range(3):
        txt = bot.get(event.channel)
        if txt:
            bot.say(event.channel, txt)
    sz = bot.size(event.channel)
    event.reply("%s more in cache" % sz)


def pwd(event):
    if len(event.args) != 2:
        event.reply("pwd <nick> <password>")
        return
    m = "\x00%s\x00%s" % (event.args[0], event.args[1])
    mb = m.encode("ascii")
    bb = base64.b64encode(mb)
    bm = bb.decode("ascii")
    event.reply(bm)
