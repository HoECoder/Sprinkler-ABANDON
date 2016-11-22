
from collections import OrderedDict
from core_config import interval_types
from settings_keys import *
import cerberus

even_odd_intervals = [EVEN_INTERVAL_TYPE,
                      ODD_INTERVAL_TYPE]
                      
TOO_EARLY = -1
STOP = 0
START = 1
                                 
def validate_interval(field, value, error):
    typ = value[INTERVAL_TYPE_KEY]
    if typ == DOW_INTERVAL_TYPE:
        days = value.get(RUN_DAYS_KEY, None)
        if days is None:
            error(field, "Day of Week Interval must contain a list of days")
        ma = max(days)
        mi = min(days)
        if mi < 0 or ma > 6:
            error(field, "Day of Week Interval must have a list of days Sun - Sat")
    elif not typ in even_odd_intervals:
        error(field, "Interval type must be 'even','odd','day_of_week'")


station_block_schema = {STATION_ID_KEY : {"type" : "integer",
                                          "min" : 0},
                        DURATION_KEY : {"type" : "integer",
                                        "min" : 0}}
program_schema = {PROGRAM_ID_KEY : {"type" : "integer",
                                    "min" : 0},
                  TIME_OF_DAY_KEY : {"type" : "integer",
                                     "min" : 0},
                  INTERVAL_KEY : {"type":"dict",
                                  "validator":validate_interval},
                  STATION_DURATION_KEY : {"type" : "list",
                                          "schema" : {"type" : "dict",
                                                      "schema" : station_block_schema}}}

program_validator = cerberus.Validator(program_schema,allow_unknown = True)

class StationBlock(object):
    def __init__(self,
                 station_id,
                 duration,
                 start_time=0,
                 end_time=0,
                 parent = None):
        self.station_id = station_id
        self.__duration = duration
        self.start_time = start_time
        self.end_time = end_time
        self.in_station = False
        self.__dirty=False
        self.parent = parent
    @property
    def dirty(self):
        return self.__dirty
    @dirty.setter
    def dirty(self, value):
        self.__dirty = value
    @property
    def duration(self):
        return self.__duration
    @duration.setter
    def duration(self, value):
        if not(isinstance(value, int) or isinstance(value, float)):
            raise TypeError(value)
        if self.__duration != value:
            self.__duration = value
            self.__dirty = True
            if not self.parent is None:
                self.parent.fix_start_end()
    def serialize(self):
        d = OrderedDict()
        d[STATION_ID_KEY] = self.station_id
        d[DURATION_KEY] = self.duration
        return d

def unpack_station_block(d):
    s = StationBlock(d[STATION_ID_KEY],d[DURATION_KEY])
    return s


class Program(object):
    def __init__(self,
                 program_id,
                 time_of_day,
                 interval,
                 dow = None,
                 is_one_shot = False,
                 station_blocks = list()):
        self.program_id  = program_id
        self.__time_of_day = time_of_day
        self.__running = False
        self.interval = interval
        self.dow = dow
        self.is_one_shot = is_one_shot
        self.station_blocks = station_blocks
        if not(self.station_blocks is None):
            for sb in self.station_blocks:
                sb.parent = self
        self.__dirty = False
        if not(self.station_blocks is None) and len(self.station_blocks) > 0:
            self.fix_start_end()
    @property
    def dirty(self):
        return self.__dirty or reduce(lambda x,y: x or y.dirty, self.station_blocks,False)
    @dirty.setter
    def dirty(self, value):
        self.__dirty = value
    @property
    def time_of_day(self):
        return self.__time_of_day
    @time_of_day.setter
    def time_of_day(self, value):
        if not(isinstance(value, int) or isinstance(value, float)):
            raise TypeError(value)
        if self.__time_of_day != value:
            self.__time_of_day = value
            self.fix_start_end()
    @property
    def running(self):
        return self.__running
    @running.setter
    def running(self, value):
        if self.__running != value:
            self.__running = value
            if not self.__running:
                for sb in self.station_blocks:
                    sb.in_station = False
    def fix_start_end(self):
        start = self.__time_of_day
        for sb in self.station_blocks:
            sb.start_time = start
            sb.end_time = start + sb.duration
            start = sb.end_time
    def serialize(self):
        int_d = {INTERVAL_TYPE_KEY : self.interval}
        if not self.interval in even_odd_intervals:
            int_d[RUN_DAYS_KEY]=self.dow
        d = OrderedDict()
        
        d[PROGRAM_ID_KEY] = self.program_id
        d[TIME_OF_DAY_KEY] = self.time_of_day
        d[INTERVAL_KEY] = int_d
        d[STATION_DURATION_KEY] = [s.serialize() for s in self.station_blocks]
        return d
    def evaluate(self, now):
        """returns -1, 0, 1 if the program should:
        -1 - Too early
         1 - Continue running
         0 - Stop running
        """
        if now["day"] % 2 == 0:
            even_odd = EVEN_INTERVAL_TYPE
        else:
            even_odd = ODD_INTERVAL_TYPE
        if self.interval in even_odd_intervals and self.interval == even_odd:
            in_day = True
        elif self.interval == DOW_INTERVAL_TYPE:
            in_day = now["day"] in self.dow
        if in_day:
            start_times = min([sb.start_time for sb in self.station_blocks])
            end_time = max([sb.end_time for sb in self.station_blocks])
            seconds = now["seconds_from_midnight"]
            if seconds < start_time:
                return TOO_EARLY
            if seconds > end_time:
                return STOP
            return START
        else:
            return TOO_EARLY

def unpack_program(d):
    if not program_validator.validate(d):
        return None #TODO : raise an error
    program_id = d[PROGRAM_ID_KEY]
    time_of_day = d[TIME_OF_DAY_KEY]
    int_d = d[INTERVAL_KEY]
    stations = [unpack_station_block(s) for s in d[STATION_DURATION_KEY]]
    interval = int_d["type"]
    if not interval in even_odd_intervals:
        days = int_d[RUN_DAYS_KEY]
    else:
        days = None
    return Program(program_id,time_of_day,interval,dow=days,station_blocks = stations)
