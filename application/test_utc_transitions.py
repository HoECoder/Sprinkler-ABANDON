import unittest

import time
import datetime
from calendar import timegm
import pytz

from clock import *

central = None

short_days = list()
long_days = list()

short_sample_times = [3600 * 2 - 2,
                      3600 * 2 - 1,
                      3600 * 3,
                      3600 * 3 + 1]
                      
long_sample_times = [3600 * 2 - 2,
                      3600 * 2 - 1,
                      3600,
                      3600 + 1]
                      
short_tick_count = len(short_sample_times)
long_tick_count = len(long_sample_times)

fmt = '%Y-%m-%d %H:%M:%S %Z'

def setUpModule():
    sim_clock.tick_unit = 1
    # Make Central Time
    #TODO: Make this locale generic
    #I know this is a bit of a kludge
    central = pytz.timezone('US/Central')
    minimum_year = time.localtime().tm_year
    for day in central._utc_transition_times: # Short day is in 'spring'
        #Remove really old times as well
        if day.year >= minimum_year: 
            day_tuple = day.timetuple()
            fday = timegm(day_tuple)
            if day.month < 6:
                short_days.append(fday - 2)
            elif day.month >= 6:
                long_days.append(fday - 2)
    
    #print short_days[-1]
    #print long_days[-1]

class TestClockShortDaySimple(unittest.TestCase):
    def __test_single_transition(self, transition, check_list):
        sim_clock.set_arbitrary_time_float(transition)
        #print '====='
        seconds_from_midnight = list()
        for x in xrange(len(check_list)):
            now = make_now()
            #s = ("%s, %s" % (time.strftime(fmt,time.localtime(now['epoch'])), pretty_now(now)))
            #print s
            seconds_from_midnight.append(now['seconds_from_midnight'])
            sim_clock.tick()
        msg = "Bad Transition: %0.1f" % transition
        self.assertEqual(check_list, seconds_from_midnight, msg)
    
    def test_one_short_transition(self):
        last = short_days[-1]
        self.__test_single_transition(last, short_sample_times)

    def test_one_long_transition(self):
        last = long_days[-1]
        self.__test_single_transition(last, long_sample_times)

    def test_short_transitions(self):
        for day in short_days:
            self.__test_single_transition(day, short_sample_times)
            
    def test_long_transitions(self):
        for day in long_days:
            self.__test_single_transition(day, long_sample_times)
            

def load_tests(loader, tests, pattern):
    
    dict_suite = unittest.TestSuite()
    dict_suite.addTest(TestClockShortDaySimple('test_one_short_transition'))
    dict_suite.addTest(TestClockShortDaySimple('test_one_long_transition'))
    dict_suite.addTest(TestClockShortDaySimple('test_short_transitions'))
    dict_suite.addTest(TestClockShortDaySimple('test_long_transitions'))
    
    return unittest.TestSuite([dict_suite])