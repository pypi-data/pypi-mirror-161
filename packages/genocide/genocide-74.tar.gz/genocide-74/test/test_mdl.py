# This file is placed in the Public Domain.


"model tests"


import unittest


from genocide.mdl import oorzaak
from genocide.obj import Object


class Test_Composite(unittest.TestCase):

    def test_composite(self):
        self.assertEqual(type(oorzaak), Object)
