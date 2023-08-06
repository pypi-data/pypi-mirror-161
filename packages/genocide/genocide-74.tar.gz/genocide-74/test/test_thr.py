# This file is placed in the Public Domain.


"threads tests"


import unittest


from genocide.thr import Thread


class Test_Threads(unittest.TestCase):

    func = None

    def setUp(self):
        def test(event):
            pass
        self.func = test
        

    def test_thread(self):
        t = Thread(self.func, "test")
        self.assertEqual(type(t), Thread)
