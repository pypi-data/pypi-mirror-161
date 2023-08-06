# This file is placed in the Public Domain.


"object"


import copy as copying
import datetime
import json
import os
import pathlib
import uuid


def __dir__():
    return (
        'Class',
        'Config',
        'Db',
        'Object',
        'ObjectDecoder',
        'ObjectEncoder',
        'all',
        'clear',
        'copy',
        'diff',
        'dump',
        'dumps',
        'edit',
        'find',
        'format',
        'fromkeys',
        'get',
        'items',
        'key',
        'keys',
        'last',
        'load',
        'loads',
        'pop',
        'popitem',
        'read',
        "register",
        'save',
        'search',
        'setdefault',
        'update',
        'values'
    )


class ENOPATH(Exception):

    pass


class Object:

    "object"


    __slots__ = (
        "__dict__",
        "__otype__",
        "__stp__",
    )


    def __init__(self):
        object.__init__(self)
        self.__otype__ = str(type(self)).split()[-1][1:-2]
        self.__stp__ = os.path.join(
            self.__otype__,
            str(uuid.uuid4()),
            os.sep.join(str(datetime.datetime.now()).split()),
        )

    def __class_getitem__(cls):
        return cls.__dict__.__class_geitem__(cls)

    def __contains__(self, k):
        if k in self.__dict__.keys():
            return True
        return False

    def __delitem__(self, k):
        if k in self:
            del self.__dict__[k]

    def __eq__(self, o):
        return len(self.__dict__) == len(o.__dict__)

    def __getitem__(self, k):
        return self.__dict__[k]

    def __ior__(self, o):
        return self.__dict__.__ior__(o)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __le__(self, o):
        return len(self) <= len(o)

    def __lt__(self, o):
        return len(self) < len(o)

    def __ge__(self, o):
        return len(self) >= len(o)

    def __gt__(self, o):
        return len(self) > len(o)

    def __hash__(self):
        return id(self)

    def __ne__(self, o):
        return len(self.__dict__) != len(o.__dict__)

    def __reduce__(self):
        pass

    def __reduce_ex__(self, k):
        pass

    def __reversed__(self):
        return self.__dict__.__reversed__()

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __oqn__(self):
        return "<%s.%s object at %s>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self)),
        )

    def __ror__(self, o):
        return self.__dict__.__ror__(o)

    def __str__(self):
        return str(self.__dict__)


class Default(Object):


    _default = ""


    def __getattr__(self, k):
        return self.__dict__.get(k, self._default)


class Config(Default):

    console = False
    daemon = False
    debug = False
    name = ""
    threaded = False
    verbose = False
    version = ""
    workdir = ""


def clear(o):
    o.__dict__ = {}


def copy(o):
    return copying.copy(o)


def fromkeys(iterable, value=None):
    o = Object()
    for i in iterable:
        o[i] = value
    return o


def get(o, k, default=None):
    return o.__dict__.get(k, default)


def items(o):
    try:
        return o.__dict__.items()
    except AttributeError:
        return o.items()


def key(o, k, default=None):
    for kk in keys(o):
        if k.lower() in kk.lower():
            return kk


def keys(o):
    try:
        return o.__dict__.keys()
    except (AttributeError, TypeError):
        return o.keys()


def pop(o, k, d=None):
    try:
        return o[k]
    except KeyError as ex:
        if d:
            return d
        raise KeyError from ex


def popitem(o):
    k = keys(o)
    if k:
        v = o[k]
        del o[k]
        return (k, v)
    raise KeyError


def setdefault(o, k, default=None):
    if k not in o:
        o[k] = default
    return o[k]


def update(o, data):
    try:
        o.__dict__.update(vars(data))
    except TypeError:
        o.__dict__.update(data)
    return o


def values(o):
    try:
        return o.__dict__.values()
    except TypeError:
        return o.values()


class ObjectDecoder(json.JSONDecoder):

    def decode(self, s, _w=None):
        v = json.loads(s)
        o = Object()
        update(o, v)
        return o


class ObjectEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, Object):
            return vars(o)
        if isinstance(o, list):
            return iter(o)
        if isinstance(o,
                      (type(str), type(True), type(False),
                       type(int), type(float))):
            return o
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            return str(o)

def cdir(path):
    if os.path.exists(path):
        return
    if path.split(os.sep)[-1].count(":") == 2:
        path = os.path.dirname(path)
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def dump(o, opath):
    cdir(opath)
    with open(opath, "w", encoding="utf-8") as ofile:
        json.dump(
            o.__dict__, ofile, cls=ObjectEncoder, indent=4, sort_keys=True
        )
    return o.__stp__


def dumps(o):
    return json.dumps(o, cls=ObjectEncoder)


def load(o, opath):
    if opath.count(os.sep) != 3:
        raise ENOPATH(opath)
    assert Config.workdir
    splitted = opath.split(os.sep)
    stp = os.sep.join(splitted[-4:])
    lpath = os.path.join(Config.workdir, "store", stp)
    if os.path.exists(lpath):
        with open(lpath, "r", encoding="utf-8") as ofile:
            d = json.load(ofile, cls=ObjectDecoder)
            update(o, d)
    o.__stp__ = stp
    return o.__stp__


def loads(s):
    return json.loads(s, cls=ObjectDecoder)


def save(o, stime=None):
    assert Config.workdir
    prv = os.sep.join(o.__stp__.split(os.sep)[:2])
    if stime:
        o.__stp__ = os.path.join(prv, stime)
    else:
        o.__stp__ = os.path.join(prv,
                             os.sep.join(str(datetime.datetime.now()).split()))
    opath = os.path.join(Config.workdir, "store", o.__stp__)
    dump(o, opath)
    os.chmod(opath, 0o444)
    return o.__stp__


def spl(txt):
    try:
        l = txt.split(",")
    except (TypeError, ValueError):
        l = txt
    return [x for x in l if x]


def diff(o1, o2):
    d = Object()
    for k in keys(o2):
        if k in keys(o1) and o1[k] != o2[k]:
            d[k] = o2[k]
    return d


def edit(o, setter):
    for k, v in items(setter):
        register(o, k, v)


def format(o, args="", skip="_", empty=False, plain=False, **kwargs):
    if not o:
        return ""
    res = []
    if args:
        ks = spl(args)
    else:
        ks = keys(o)
    for k in ks:
        if k in spl(skip) or k.startswith("_"):
            continue
        v = getattr(o, k, None)
        if not v and not empty:
            continue
        txt = ""
        if plain:
            txt = str(v)
        elif isinstance(v, str) and len(v.split()) >= 2:
            txt = '%s="%s"' % (k, v)
        else:
            txt = '%s=%s' % (k, v)
        res.append(txt)
    return " ".join(res)


def register(o, k, v):
    setattr(o, k, v)


def search(o, s):
    ok = False
    for k, v in items(s):
        vv = getattr(o, k, None)
        if v not in str(vv):
            ok = False
            break
        ok = True
    return ok
