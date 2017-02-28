import unittest

import time
import datetime
import pytz

from clock import *

central = None

short_days = list()
long_days = list()

td = datetime.timedelta(0, 2)

def setUpModule():
    sim_clock.tick_unit = 1
    # Make Central Time
    #TODO: Make this locale generic
    #I know this is a bit of a kludge
    central = pytz.timezone('US/Central')
    for day in central._utc_transition_times: # Short day is in 'spring'
        #Remove really old times as well
        if day.year >= 1970 and day.month < 6:
            short_days.append(day - td)
        elif day.year >= 1970 and day.month >= 6:
            long_days.append(day - td)

class TestClockShortDaySimple(unittest.TestCase):

    def test_one_short_transition(self):
        last = short_days[-1]
        last_tuple = last.timetuple()
        sim_clock.set_arbitrary_time(last_tuple)
        now = make_now()
        print now
        print pretty_now(now)

    def test_short_transition(self):
        for short_day in short_days:
            short_tuple = short_day.timetuple()
            sim_clock.set_arbitrary_time(short_tuple)
            now = make_now()
            print pretty_now(now)

def load_tests(loader, tests, pattern):
    
    dict_suite = unittest.TestSuite()
    dict_suite.addTest(TestClockShortDaySimple('test_one_short_transition'))
    
    return unittest.TestSuite([dict_suite])