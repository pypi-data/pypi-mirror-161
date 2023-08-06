# This file is placed in the Public Domain.


"console tests"


import unittest


from genocide.run import CLI, Console


class Test_Console(unittest.TestCase):

    def test_console(self):
        c = Console()
        self.assertEqual(type(c), Console)
