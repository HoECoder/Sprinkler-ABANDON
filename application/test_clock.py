import unittest

from core_config import END_OF_DAY, TIME_PARSE_FORMAT, TIME_DUMP_FORMAT
from clock import *

invalid_times = ["24:00:00",
                 "-1",
                 "13:61:00",
                 "13:60:00",
                 "00:00:70",
                 "00:00:-01",
                 "23:60:00"]
invalid_time_f = [END_OF_DAY,
                  -1,
                  -1 * END_OF_DAY,
                  END_OF_DAY * 2]

class TestClockParse(unittest.TestCase):
    def test_valid_times(self):
        for sec in xrange(END_OF_DAY):
            h = sec / 3600
            m = (sec - (h * 3600)) / 60
            s = (sec - (h * 3600) - (m * 60))
            ts = TIME_DUMP_FORMAT % (h, m, s)
            r = clock_parse(ts)
            self.assertEqual(sec, r)
    def test_invalid_times(self):
        for inv in invalid_times:
            r = clock_parse(inv)
            self.assertEqual(-1, r)
            
class TestFormatToD(unittest.TestCase):
    def test_valid_times(self):
        for sec in xrange(END_OF_DAY):
            r = clock_parse(format_time_of_day(sec))
            self.assertNotEqual(-1, r)
    def test_invalid_times(self):
        for inv in invalid_time_f:
            r = clock_parse(format_time_of_day(inv))
            self.assertEqual(-1, r)

def load_tests(loader, tests, pattern):
    
    dict_suite = unittest.TestSuite()
    dict_suite.addTest(TestClockParse('test_valid_times'))
    dict_suite.addTest(TestClockParse('test_invalid_times'))
    dict_suite.addTest(TestFormatToD('test_valid_times'))
    dict_suite.addTest(TestFormatToD('test_invalid_times'))

    return unittest.TestSuite([dict_suite])