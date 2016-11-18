
from singleton import singleton
from core_config import SIMULATE_TIME
import time

@singleton
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

def __build_make_now(timef=time.time):
    
    def make_now():
        # We build now (year,month,day,day_of_week,hour,minute,second,seconds_from_midnight)
        seconds = timef()
        #print seconds
        current_time = time.localtime(seconds)
        n = dict()
        n["year"] = current_time.tm_year
        n["month"] = current_time.tm_mon
        n["day"] = current_time.tm_mday
        n["day_of_week"] = current_time.tm_wday
        n["hour"] = current_time.tm_hour
        n["minute"] = current_time.tm_min
        n["second"] = current_time.tm_sec

        hrs = n["hour"] * 3600
        mins = n["minute"] * 60
        secs = n["second"]

        seconds = hrs + mins + secs

        n["seconds_from_midnight"] = seconds

        return n
    return make_now

def pretty_now(now):
    s = "%d/%d/%d %2d:%2d:%2d %d"
    r = s %(now['year'],
                now['month'],
                now['day'],
                now['hour'],
                now['minute'],
                now['second'],
                now['seconds_from_midnight'])
    return r

# Setup for simulation mode
if SIMULATE_TIME:
    __sim_clock = SimulationClock()
    time_function=__sim_clock.time
else:
    time_function=time.time

# return the critical timing function
make_now = __build_make_now(timef=time_function)