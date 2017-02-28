
from singleton import singleton
from core_config import SIMULATE_TIME, TIME_PARSE_FORMAT, TIME_DUMP_FORMAT
import time

class SimulationClock(object):
    def __init__(self,start_time=None):
        self.tick_unit = 1
        if start_time is None:
            self.ticker = time.time()
        else:
            self.ticker = start_time
    def tick(self):
        #print "tick: %f" % self.ticker
        self.ticker += self.tick_unit
    def time(self):
        return self.ticker
    def set_arbitrary_time(self, time_tuple):
        t = time.mktime(time_tuple)
        self.ticker = t
    def reset_to_today(self):
        t = time.localtime()
        t = [x for x in t]
        t[3] = 0
        t[4] = 0
        t[5] = 0
        self.set_arbitrary_time(t)

def __build_make_now(timef=time.time):
    
    def make_now():
        # We build now (year,month,day,day_of_week,hour,minute,second,seconds_from_midnight)
        epoch_seconds = timef()
        #print seconds
        current_time = time.localtime(epoch_seconds)
        seconds_from_midnight = (current_time.tm_hour * 3600 +
                                 current_time.tm_min * 60 +
                                 current_time.tm_sec)
        n = dict()

        n["day"] = current_time.tm_mday
        n["day_of_week"] = current_time.tm_wday

        n["seconds_from_midnight"] = seconds_from_midnight
        n["epoch"] = epoch_seconds
        # n["year"] = current_time.tm_year
        # n["month"] = current_time.tm_mon
        # n["hour"] = current_time.tm_hour
        # n["minute"] = current_time.tm_min
        # n["second"] = current_time.tm_sec

        return n
    return make_now

def pretty_now(now):
    s = "Epoch: %0.1f, D: %d, DOW: %d, Sec: %d"
    r = s %(now['epoch'],
            now['day'],
            now['day_of_week'],
            now['seconds_from_midnight'])
    return r

def clock_parse(s):
    try:
        t = time.strptime(s, TIME_PARSE_FORMAT)
        hrs = t.tm_hour
        mins = t.tm_min
        secs = t.tm_sec
        seconds_from_midnight = hrs * 3600 + mins * 60 + secs
        return seconds_from_midnight
    except ValueError:
        return -1

def format_time_of_day(time_float):
    hours = time_float / 3600
    minutes = (time_float - (hours * 3600)) / 60
    seconds = (time_float - (hours * 3600) - (minutes * 60))
    
    return TIME_DUMP_FORMAT % (hours, minutes, seconds)

# Setup for simulation mode
sim_clock = SimulationClock()
if SIMULATE_TIME:
    time_function = sim_clock.time
else:
    time_function=time.time

# return the critical timing function
make_now = __build_make_now(timef=time_function)