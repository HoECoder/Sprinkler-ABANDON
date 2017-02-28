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
            
class TestSimulationClock(unittest.TestCase):
    def test_monotonicity(self):
        start = sim_clock.time()
        for x in xrange(END_OF_DAY):
            pre_check = sim_clock.time()
            sim_clock.tick()
            post_check = sim_clock.time()
            self.assertTrue(post_check > pre_check)
        end = sim_clock.time()
        self.assertTrue(end > start)
    def test_small_ticks(self):
        sim_clock.reset_to_today()
        sim_clock.tick_unit = 0.1
        start = sim_clock.time()
        for x in xrange(10):
            pre_check = sim_clock.time()
            sim_clock.tick()
            post_check = sim_clock.time()
            self.assertTrue(post_check > pre_check)
            self.assertTrue(post_check - pre_check < 1)
        end = sim_clock.time()
        self.assertTrue(end > start)
        self.assertAlmostEqual(end - start , 1, places = 5) # This is a fiddly pain
        sim_clock.tick_unit = 1
    def tearDown(self):
        sim_clock.tick_unit = 1
        sim_clock.reset_to_today()
            
class TestPrettyNow(unittest.TestCase):
    def test_pretty_now(self):
        now = make_now()
        s = pretty_now(now)
        self.assertIsNotNone(s)

def load_tests(loader, tests, pattern):
    
    dict_suite = unittest.TestSuite()
    dict_suite.addTest(TestClockParse('test_valid_times'))
    dict_suite.addTest(TestClockParse('test_invalid_times'))
    dict_suite.addTest(TestFormatToD('test_valid_times'))
    dict_suite.addTest(TestFormatToD('test_invalid_times'))
    dict_suite.addTest(TestSimulationClock('test_monotonicity'))
    dict_suite.addTest(TestSimulationClock('test_small_ticks'))
    dict_suite.addTest(TestPrettyNow('test_pretty_now'))

    return unittest.TestSuite([dict_suite])