import re
import numpy
import pandas
from tests import TestCase
from file_validator.helper.utils import (
    FLOAT_RE, FIRST_CAP_RE, ALL_CAP_RE, clean_value, is_empty, to_snake, to_int, to_str, to_float, dollar_str_to_float,
)


class TestUtils(TestCase):
    def test_should_match_float_re(self):
        self.assertEqual(True, True if re.match(FLOAT_RE, '2.0') else False)
        self.assertEqual(True, True if re.match(FLOAT_RE, '2.00') else False)
        self.assertEqual(True, True if re.match(FLOAT_RE, '02.00') else False)
        self.assertEqual(True, True if re.match(FLOAT_RE, '02') else False)
        self.assertEqual(True, True if re.match(FLOAT_RE, '2') else False)
        self.assertEqual(False, True if re.match(FLOAT_RE, 'True') else False)
        self.assertEqual(False, True if re.match(FLOAT_RE, '[1,2]') else False)

    def test_should_verify_first_cap_re(self):
        self.assertEqual(False, True if re.match(FIRST_CAP_RE, '. Some text') else False)  # True?
        self.assertEqual(True, True if re.match(FIRST_CAP_RE, '.Some text') else False)  # True?
        self.assertEqual(False, True if re.match(FIRST_CAP_RE, '. another text') else False)
        self.assertEqual(False, True if re.match(FIRST_CAP_RE, '.another text') else False)
        self.assertEqual(False, True if re.match(FIRST_CAP_RE, 'More text') else False)
        self.assertEqual(True, True if re.match(FIRST_CAP_RE, ' More text') else False)
        self.assertEqual(True, True if re.match(FIRST_CAP_RE, ' EvenMoreText') else False)  # True?
        self.assertEqual(False, True if re.match(FIRST_CAP_RE, ' evenMore') else False)  # True?
        self.assertEqual(True, True if re.match(FIRST_CAP_RE, '.EvenMoreText') else False)  # True?
        self.assertEqual(True, True if re.match(FIRST_CAP_RE, ' Even more text...   ') else False)  # True

    def test_should_verify_all_cap_re(self):
        self.assertEqual(True, True if re.match(ALL_CAP_RE, '1W') else False)
        self.assertEqual(True, True if re.match(ALL_CAP_RE, '1West') else False)
        self.assertEqual(True, True if re.match(ALL_CAP_RE, '1West north') else False)
        self.assertEqual(True, True if re.match(ALL_CAP_RE, '1West north') else False)

        self.assertEqual(False, True if re.match(ALL_CAP_RE, 'oneWest north') else False)
        self.assertEqual(False, True if re.match(ALL_CAP_RE, 'oneWest') else False)
        self.assertEqual(True, True if re.match(ALL_CAP_RE, 'eW') else False)
        self.assertEqual(False, True if re.match(ALL_CAP_RE, ' eW') else False)
        self.assertEqual(False, True if re.match(ALL_CAP_RE, '.eW') else False)
        self.assertEqual(False, True if re.match(ALL_CAP_RE, '. eW') else False)
        self.assertEqual(False, True if re.match(ALL_CAP_RE, ' eW ') else False)

    def test_should_clean_value(self):
        self.assertEqual(' some text ', clean_value(' some text '))  # No change
        self.assertEqual(dict(), clean_value(dict()))  # No change
        self.assertEqual(1, clean_value(pandas.Series([1, 2])))
        self.assertEqual({"key1": 1, "key2": 2}, clean_value(pandas.Series([{"key1": 1, "key2": 2}, {"key3": 3, "key4": 4}])))
        self.assertEqual(('key1', 1), clean_value(pandas.Series([('key1', 1), ('key2', 2)])))

    def test_should_verify_is_empty(self):
        self.assertEqual(False, is_empty(' some text '))
        self.assertEqual(False, is_empty(dict()))
        self.assertEqual(False, is_empty(list()))
        self.assertEqual(False, is_empty(tuple()))
        self.assertEqual(False, is_empty(set()))
        self.assertEqual(False, is_empty(0))
        self.assertEqual(False, is_empty(0.0))
        self.assertEqual(False, is_empty("  "))
        self.assertEqual(True, is_empty(str()))
        self.assertEqual(True, is_empty(u''))
        self.assertEqual(True, is_empty(""))
        self.assertEqual(True, is_empty(None))
        self.assertEqual(True, is_empty(numpy.nan))

    def test_should_verify_to_snake(self):
        self.assertEqual(' some text ', to_snake(' some text '))  # no change
        self.assertEqual('some text', to_snake('some text'))  # no change
        self.assertEqual('sometext', to_snake('sometext'))  # no change
        self.assertEqual('some_text', to_snake('SomeText'))
        self.assertEqual('._some_text', to_snake('.SomeText'))
        self.assertEqual('some_text', to_snake('someText'))
        self.assertEqual(' some_text', to_snake(' someText'))
        self.assertEqual(' _some _text', to_snake(' Some Text'))

    def test_should_verify_to_int(self):
        self.assertEqual(1, to_int(1))  # no change
        self.assertEqual(1, to_int(1.0))
        self.assertEqual(1, to_int('1'))
        self.assertEqual(1, to_int('1.0'))
        self.assertEqual(None, to_int('(1.0,)'))
        self.assertEqual(None, to_int('test'))
        self.assertEqual(None, to_int(dict()))
        self.assertEqual(None, to_int(list()))
        self.assertEqual(None, to_int(set()))
        self.assertEqual(None, to_int(tuple()))
        self.assertEqual(None, to_int(pandas.Series([])))

    def test_should_verify_to_str(self):
        self.assertEqual('1', to_str(1))
        self.assertEqual('1.0', to_str(1.0))
        self.assertEqual('1', to_str('1'))  # no change
        self.assertEqual('1.0', to_str('1.0'))  # no change
        self.assertEqual('(1.0,)', to_str('(1.0,)'))  # no change
        self.assertEqual('test', to_str('test'))  # no change
        self.assertEqual('{}', to_str(dict()))
        self.assertEqual('[]', to_str(list()))
        self.assertEqual('set()', to_str(set()))
        self.assertEqual('()', to_str(tuple()))
        self.assertEqual('Series([], dtype: float64)', to_str(pandas.Series([])))
        self.assertEqual(None, to_str(str()))
        self.assertEqual(None, to_str(None))
        self.assertEqual(None, to_str(None))

    def test_should_verify_to_float(self):
        self.assertEqual(1.0, to_float(1))
        self.assertEqual(1.0, to_float(1.0))  # no change
        self.assertEqual(1.0, to_float('1'))
        self.assertEqual(1.0, to_float('1.0'))
        self.assertEqual(None, to_float('(1.0,)'))
        self.assertEqual(None, to_float('test'))
        self.assertEqual(None, to_float(dict()))
        self.assertEqual(None, to_float(list()))
        self.assertEqual(None, to_float(set()))
        self.assertEqual(None, to_float(tuple()))
        self.assertEqual(None, to_float(pandas.Series([])))
        self.assertEqual(None, to_float(str()))
        self.assertEqual(None, to_float(None))
        self.assertEqual(None, to_float(None))

    def test_should_verify_dollar_str_to_float(self):
        self.assertEqual(None, dollar_str_to_float(1))
        self.assertEqual(None, dollar_str_to_float(1.0))
        self.assertEqual(1.0,  dollar_str_to_float('1'))
        self.assertEqual(1.0,  dollar_str_to_float('1.0'))  # no change
        self.assertEqual(-1.0, dollar_str_to_float('(1.0,)'))
        self.assertEqual(None, dollar_str_to_float('test'))
        self.assertEqual(None, dollar_str_to_float(dict()))
        self.assertEqual(None, dollar_str_to_float(list()))
        self.assertEqual(None, dollar_str_to_float(set()))
        self.assertEqual(None, dollar_str_to_float(tuple()))
        self.assertEqual(None, dollar_str_to_float(pandas.Series([])))
        self.assertEqual(None, dollar_str_to_float(str()))
        self.assertEqual(None, dollar_str_to_float(None))
        self.assertEqual(None, dollar_str_to_float(None))

        self.assertEqual(1.0,  dollar_str_to_float('$1.0'))
        self.assertEqual(1.0,  dollar_str_to_float('$$1.0'))
        self.assertEqual(None, dollar_str_to_float('$1. 0'))
        self.assertEqual(None, dollar_str_to_float('$1 .0'))
        self.assertEqual(None, dollar_str_to_float('$1 . 0'))
        self.assertEqual(1.0,  dollar_str_to_float('$  1.0'))
        self.assertEqual(None, dollar_str_to_float('&1.0'))
        self.assertEqual(None, dollar_str_to_float('&100,000.0'))
        self.assertEqual(100000.0, dollar_str_to_float('$100,000.0'))
        self.assertEqual(1000000.0, dollar_str_to_float('$$1,000,000.0'))
