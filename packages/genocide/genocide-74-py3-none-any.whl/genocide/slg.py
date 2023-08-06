# This file is placed in the Public Domain


from .com import Commands


def reg():
    Commands.add(slg)


def rem():
    Commands.remove(slg)


txt = """GENOCIDE 73 released - http://pypi.org/project/genocide

basis to prosecute are:

1) not medicine but poison
2) law and poison
3) special law for special people


@KarimKhanQC  @IntlCrimCourt
 

reconsider OTP-CR-117/19

http://genocide.rtfd.io 
"""


def slg(event):
    event.reply(txt)
