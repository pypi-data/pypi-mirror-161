# This file is placed in the Public Domain.


"time tests"


import unittest


from genocide.thr import Timer



class Test_Time(unittest.TestCase):

    def setUp(self):
        def test(event):
            pass
        self.func = test

    def test_timer(self):
        t = Timer(60, self.func)
        self.assertEqual(type(t), Timer)
