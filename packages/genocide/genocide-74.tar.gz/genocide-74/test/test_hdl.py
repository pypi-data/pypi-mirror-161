# This file is placed in the Public Domain.


"composition tests"


import unittest


from genocide.hdl import Handler



class Test_Handler(unittest.TestCase):

    def test_handler(self):
        h = Handler()
        self.assertEqual(type(h), Handler)
