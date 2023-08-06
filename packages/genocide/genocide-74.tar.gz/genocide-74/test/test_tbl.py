# This file is placed in the Public Domain.


"composition tests"


import unittest


from genocide.run import Table



class Test_Table(unittest.TestCase):

    def test_table(self):
        t = Table()
        self.assertEqual(type(t), Table)
