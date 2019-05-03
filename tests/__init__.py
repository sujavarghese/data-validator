import unittest


class Base(unittest.TestCase):
    def fixtures(self, name):
        with open('fixtures/' + name, 'r') as input:
            input_file = input.read()
        return input_file
