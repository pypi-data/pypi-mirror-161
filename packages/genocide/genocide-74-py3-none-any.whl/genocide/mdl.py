# This file is placed in the Public Domain.


"model"


import time


from .bus import Bus
from .com import Commands
from .evt import Event
from .obj import Object, get, key, keys, update
from .thr import Repeater, launch
from .utl import elapsed


def __dir__():
    return (
        "init",
        "reg",
        "rem"
    )


def init():
    for k in keys(oorzaken):
        val = get(oorzaken, k, None)
        if val and int(val) > 10000:
            e = Event()
            e.txt = ""
            e.rest = k
            sec = seconds(val)
            repeater = Repeater(sec, cbstats, e, name=get(aliases, k))
            repeater.start()
    launch(daily, name="daily")
    #launch(hourly, name="hourly")


def reg():
    Commands.add(now)
    Commands.add(sts)
    Commands.add(tpc)


def rem():
    Commands.remove(now)
    Commands.remove(sts)
    Commands.remove(tpc)


oor = """"Totaal onderliggende doodsoorzaken (aantal)";"1 Infectieuze en parasitaire ziekten/Totaal infectieuze en parasitaire zktn (aantal)";"1 Infectieuze en parasitaire ziekten/1.1 Tuberculose (aantal)";"1 Infectieuze en parasitaire ziekten/1.2 Meningokokkeninfecties (aantal)";"1 Infectieuze en parasitaire ziekten/1.3 Virale hepatitis (aantal)";"1 Infectieuze en parasitaire ziekten/1.4 AIDS (aantal)";"1 Infectieuze en parasitaire ziekten/1.5 Ov. infectieuze en parasitaire zktn (aantal)";"2 Nieuwvormingen/Totaal nieuwvormingen (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/Totaal kwaadaardige nieuwvormingen (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.1 Kw. nv. van lip, mond en keel (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.2 Kw. nv. van slokdarm (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.3 Kw. nv. van maag (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.4 Kw. nv. van dikke darm (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.5 Kw. nv. van endeldarm en anus (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.6 Kw. nv. lever en intrah. galwegen (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.7 Kw. nv. van galblaas en galwegen (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.8 Kw. nv. van alvleesklier (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.9 Kw. nv. van strottenhoofd (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.10 Kw. nv. van luchtpijp en long (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.11 Melanoom van huid (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.12 Kw. nv. van borst (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.13 Kw. nv. van baarmoederhals (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.14 Kw. nv. van baarmoederlichaam (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.15 Kw. nv. van eierstok (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.16 Kw. nv. van prostaat (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.17 Kw. nv. nier, behalve nierbekken (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.18 Kw. nv. van urineblaas (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.19 Kw. nv. lymf. en bloedv. weefsel (aantal)";"2 Nieuwvormingen/2.1 Kwaadaardige nieuwvormingen/2.1.20 Ov. kwaadaardige nieuwvormingen (aantal)";"2 Nieuwvormingen/2.2 Overige nieuwvormingen (aantal)";"3 Zktn bloed, bloedvormende organen en.. (aantal)";"4 Endocriene, voedings-, stofwiss. zktn/Totaal endocriene, voedings-, stofwiss.. (aantal)";"4 Endocriene, voedings-, stofwiss. zktn/4.1 Suikerziekte (aantal)";"4 Endocriene, voedings-, stofwiss. zktn/4.2 Ov. endocriene, voedings-, stofwis.. (aantal)";"5 Psychische en gedragsstoornissen/Totaal psychische stoornissen (aantal)";"5 Psychische en gedragsstoornissen/5.1 Psychische stoornissen door alcohol (aantal)";"5 Psychische en gedragsstoornissen/5.2 Psychische stoornissen drugs en vl.. (aantal)";"5 Psychische en gedragsstoornissen/5.3 Overige psychische stoornissen (aantal)";"6 Ziekten van zenuwstelsel en zintuigen/Totaal ziekten zenuwstelsel en zintuigen (aantal)";"6 Ziekten van zenuwstelsel en zintuigen/6.1 Hersenvliesontsteking (aantal)";"6 Ziekten van zenuwstelsel en zintuigen/6.2 Ziekte van Parkinson (aantal)";"6 Ziekten van zenuwstelsel en zintuigen/6.3 Ov. zktn zenuwstelsel en zintuigen (aantal)";"7 Ziekten van hart en vaatstelsel/Totaal ziekten van hart en vaatstelsel (aantal)";"7 Ziekten van hart en vaatstelsel/7.1 Ziekten van de kransvaten/Totaal ziekten van de kransvaten (aantal)";"7 Ziekten van hart en vaatstelsel/7.1 Ziekten van de kransvaten/7.1.1 Acuut hartinfarct (aantal)";"7 Ziekten van hart en vaatstelsel/7.1 Ziekten van de kransvaten/7.1.2 Overige ziekten van de kransvaten (aantal)";"7 Ziekten van hart en vaatstelsel/7.2 Overige hartziekten (aantal)";"7 Ziekten van hart en vaatstelsel/7.3 Hersenvaatletsels (aantal)";"7 Ziekten van hart en vaatstelsel/7.4 Overige ziekten hart en vaatstelsel (aantal)";"8 Ziekten van de ademhalingsorganen/Totaal ziekten van de ademhalingsorganen (aantal)";"8 Ziekten van de ademhalingsorganen/8.1 Griep (aantal)";"8 Ziekten van de ademhalingsorganen/8.2 Longontsteking (aantal)";"8 Ziekten van de ademhalingsorganen/8.3 Chron. aand. onderste luchtwegen/Totaal chronische aand. onderste lucht.. (aantal)";"8 Ziekten van de ademhalingsorganen/8.3 Chron. aand. onderste luchtwegen/8.3.1 Astma (aantal)";"8 Ziekten van de ademhalingsorganen/8.3 Chron. aand. onderste luchtwegen/8.3.2 Ov. chron. aand. onderste luchtw.. (aantal)";"8 Ziekten van de ademhalingsorganen/8.4 Overige ziekten ademhalingsorganen (aantal)";"9 Ziekten van de spijsverteringsorganen/Totaal ziekten spijsverteringsorganen (aantal)";"9 Ziekten van de spijsverteringsorganen/9.1 Maagzweer en zweer aan twaalfvinge.. (aantal)";"9 Ziekten van de spijsverteringsorganen/9.2 Chronische leveraandoeningen/Totaal chronische leveraandoeningen (aantal)";"9 Ziekten van de spijsverteringsorganen/9.2 Chronische leveraandoeningen/9.2.1 Chronische leveraand. alcohol (aantal)";"9 Ziekten van de spijsverteringsorganen/9.2 Chronische leveraandoeningen/9.2.2 Ov. chronische leveraandoeningen (aantal)";"9 Ziekten van de spijsverteringsorganen/9.3 Ov. ziekten spijsverteringsorganen (aantal)";"10 Ziekten van huid en subcutis (aantal)";"11 Ziekten botspierstelsel en bindweef../Totaal ziekten spieren, beend., bindwfsl (aantal)";"11 Ziekten botspierstelsel en bindweef../11.1 Reumatoïde artritis en artrose (aantal)";"11 Ziekten botspierstelsel en bindweef../11.2 Ov. zktn spieren, beend., bindwfsl (aantal)";"12 Ziekten van urogenitaal stelsel/Totaal zktn urinewegen en gesl. organen (aantal)";"12 Ziekten van urogenitaal stelsel/12.1 Ziekten van nier en urineleider (aantal)";"12 Ziekten van urogenitaal stelsel/12.2 Ov. zktn urinewegen en gesl.organen (aantal)";"13 Zwangerschap, bevalling en kraambed. (aantal)";"14 Aandoeningen v.d. perinatale periode (aantal)";"15 Aangeboren afwijkingen/Totaal aangeboren afwijkingen (aantal)";"15 Aangeboren afwijkingen/15.1 Aangeboren afw. zenuwstelsel (aantal)";"15 Aangeboren afwijkingen/15.2 Aangeboren afw. hart en bloedvaten (aantal)";"15 Aangeboren afwijkingen/15.3 Overige aangeboren afwijkingen (aantal)";"16 Sympt., afwijkende klinische bevind../Totaal symp. en onvoll. omschr. ziekte.. (aantal)";"16 Sympt., afwijkende klinische bevind../16.1 Wiegendood (aantal)";"16 Sympt., afwijkende klinische bevind../16.2 Onvoll. omschr. en onbek. oorzaken (aantal)";"16 Sympt., afwijkende klinische bevind../16.3 Ov. symptomen en onvolledig omsch.. (aantal)";"17 Uitwendige doodsoorzaken/Totaal uitwendige doodsoorzaken (aantal)";"17 Uitwendige doodsoorzaken/17.1 Ongevallen/Totaal ongevallen (aantal)";"17 Uitwendige doodsoorzaken/17.1 Ongevallen/17.1.1 Vervoersongevallen/Totaal vervoersongevallen (aantal)";"17 Uitwendige doodsoorzaken/17.1 Ongevallen/17.1.1 Vervoersongevallen/17.1.1.1 Wegverkeersongevallen (aantal)";"17 Uitwendige doodsoorzaken/17.1 Ongevallen/17.1.1 Vervoersongevallen/17.1.1.2 Overige vervoersongevallen (aantal)";"17 Uitwendige doodsoorzaken/17.1 Ongevallen/17.1.2 Accidentele val (aantal)";"17 Uitwendige doodsoorzaken/17.1 Ongevallen/17.1.3 Accidentele verdrinking (aantal)";"17 Uitwendige doodsoorzaken/17.1 Ongevallen/17.1.4 Accidentele vergiftiging (aantal)";"17 Uitwendige doodsoorzaken/17.1 Ongevallen/17.1.5 Overige ongevallen (aantal)";"17 Uitwendige doodsoorzaken/17.2 Zelfdoding (aantal)";"17 Uitwendige doodsoorzaken/17.3 Moord en doodslag (aantal)";"17 Uitwendige doodsoorzaken/17.4 Gebeurtenissen opzet onbekend (aantal)";"17 Uitwendige doodsoorzaken/17.5 Overige uitwendige doodsoorzaken (aantal)";"18 COVID-19 (Coronavirus ziekte 19)/18 Totaal COVID-19 (Coronavirus 19) (aantal)";"18 COVID-19 (Coronavirus ziekte 19)/18.1 Vastgestelde COVID-19 (aantal)";"18 COVID-19 (Coronavirus ziekte 19)/18.2 Vermoedelijke COVID-19 (aantal)""".split(";")
aantal = "168678;2974;32;1;34;23;2884;47089;45103;690;2013;1150;3395;1235;956;452;2942;205;10080;811;3083;230;560;1032;3006;923;1359;3636;7345;1986;560;3646;2799;847;11682;531;61;11090;8387;50;1792;6545;36622;8037;4718;3319;12682;8850;7053;10503;295;2726;5776;146;5630;1706;4882;138;948;433;515;3796;323;1067;333;734;3248;1958;1290;2;390;436;42;87;307;7664;11;4436;3217;9030;6433;633;590;43;5234;107;238;221;1823;107;28;639;20173;17495;2678".split(";")

oorzaak = Object()
update(oorzaak, zip(oor,aantal))
#oorzaak.Suicide = 1859

aliases = Object()
aliases["Nieuwvormingen"] = "cancer"
aliases["Hart en vaatstelsel"] = "hart disease"
aliases["Psychische en gedragsstoornissen"] = "mental illness"
aliases["Ademhalingsorganen"] = "breathing"
aliases["Uitwendige doodsoorzaken"] = "externals"
aliases["Zenuwstelsel en zintuigen"] = "nerves"
aliases["Afwijkende klinische bevindingen"] = "other diseases NOS"
aliases["Spijsverteringsorganen"] = "stomach disease"
aliases["Endocriene, voedings-, stofwisseling"] = "metabolism disease"
aliases["Urogenitaal stelsel"] = "kidney disease"
aliases["Infectieuze en parasitaire ziekten"] = "infectious disease"
aliases["Botspierstelsel en bindweefsel"] = "muscle disease"
aliases["Bloed, bloedvormende organen"] = "blood disease"
aliases["Aangeboren afwijkingen"] = "birth defect"
aliases["Huid en subcutis"] = "skin disease"
aliases["Zwangerschap"] = "pregnancy"
aliases["Suicide"] = "suicide"


demo = Object()
demo.gehandicapten = 2000000
demo.ggz = 800000
demo.population = 17440000
demo.part = 7000000000 / demo.population


jaar = Object()
jaar["WvGGZ"] = 14206
jaar["Pvp"] = 20088
jaar["Wzd"] = 25000
jaar["Wfz"] = 23820
jaar["totaal"] = 168678


oorzaken = Object()


nr = -1
for kk in keys(oorzaak):
    nr += 1
    if nr == 0:
        continue
    if kk.startswith('"'):
        kk = kk[1:]
    l = kk.split("/")
    if len(l) > 1 and not l[1].startswith("Totaal"):
        continue
    a = l[0].replace('(aantal)"', "")
    a = a.replace("Ziekten van de", "")
    a = a.replace("Ziekten van", "")
    a = a.replace("Ziekten", "")
    a = a.replace("Zktn", "")
    a = a.replace("zktn", "")
    a = a.replace("en..", "")
    a = a.replace("..", "")
    a = a.replace("bindweef", "bindweefsel")
    a = a.replace("bevind", "bevindingen")
    a = a.replace("stofwiss.", "stofwisseling")
    a = a.replace("Sympt.,", "")
    a = a.replace(", bevalling en kraambed. ", "")
    a = a.replace("Aandoeningen v.d. ", "")
    n = " ".join(a.split()[1:]).capitalize()
    n = n.strip()
    oorzaken[n] = aantal[nr]


year = 365*24*60*60
source = "https://github.com/bthate/genocide"
startdate = "2020-01-01 00:00:00"
starttime = time.mktime(time.strptime(startdate, "%Y-%m-%d %H:%M:%S"))


def daily():
    time.sleep(10.0)
    while 1:
        event = Event()
        cbnow(event)
        time.sleep(24*60*60)


def hourly():
    while 1:
        time.sleep(60*60)
        event = Event()
        cbnow(event)


def seconds(nrs):
    if not nrs:
        return nrs
    return 60*60*24*365 / float(nrs)


def nr(name):
    for k in keys(oorzaken):
        if name.lower() in k.lower():
            return int(get(oorzaken, k))
    return 0


def iswanted(k, line):
    for w in line:
        if w in k:
            return True
    return False


def cbnow(e):
    delta = time.time() - starttime
    txt = elapsed(delta) + " "
    for name in sorted(oorzaken, key=lambda x: seconds(nr(x))):
        needed = seconds(nr(name))
        if needed > 60*60:
            continue
        nrtimes = int(delta/needed)
        txt += "%s: %s " % (get(aliases, name), nrtimes)
    txt += " http://genocide.rtfd.io"
    Bus.announce(txt)


def cbstats(e):
    name = e.rest or "psych"
    needed = seconds(nr(name))
    if needed:
        delta = time.time() - starttime
        nrtimes = int(delta/needed)
        nryear = int(year/needed)
        txt = "patient #%s died from %s (%s/year) every %s" % (nrtimes, get(aliases, name),  nryear, elapsed(needed))
        Bus.announce(txt)


def now(event):
    delta = time.time() - starttime
    txt = elapsed(delta) + " "
    for name in sorted(oorzaken, key=lambda x: seconds(nr(x))):
        needed = seconds(nr(name))
        if needed > 60*60:
            continue
        nrtimes = int(delta/needed)
        txt += "%s: %s " % (get(aliases, name), nrtimes)
    txt += " http://genocide.rtfd.io"
    Bus.announce(txt)


def sts(event):
    name = event.rest or "psych"
    needed = seconds(nr(name))
    if needed:
        delta = time.time() - starttime
        nrtimes = int(delta/needed)
        nryear = int(year/needed)
        txt = "patient #%s died from %s (%s/year) every %s" % (nrtimes, key(aliases, name, name).lower(),  nryear, elapsed(needed))
        Bus.announce(txt)


def tpc(event):
    txt = "%ss " % elapsed(time.time() - starttime)
    for name in sorted(oorzaken, key=lambda x: seconds(nr(x))):
        needed = seconds(nr(name))
        delta = time.time() - starttime
        nrtimes = int(delta/needed)
        if needed > 60*60:
            continue
        txt += "%s %s " % (get(aliases, name), nrtimes)
    for bot in Bus.objs:
        try:
            for channel in bot.channels:
                bot.topic(channel, txt)
        except AttributeError:
            pass
