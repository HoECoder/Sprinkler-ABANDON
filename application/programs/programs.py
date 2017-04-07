import logging
from clock import clock_parse, format_time_of_day
from collections import OrderedDict
from core_config import END_OF_DAY, STATION_ON_OFF
from settings_keys import *

from validation import program_validator, even_odd_intervals
from station_block import StationBlock, unpack_station_block

from program_log import sqlite_program_log

TOO_EARLY = -1
STOP = 0
START = 1

def unpack_program(d, manager, logger = sqlite_program_log):
    if not program_validator.validate(d):
        return None #TODO : raise an error
    program_id = d[PROGRAM_ID_KEY]
    time_of_day = clock_parse(d[TIME_OF_DAY_KEY])
    int_d = d[INTERVAL_KEY]
    stations = [unpack_station_block(s, logger) for s in d[STATION_DURATION_KEY]]
    interval = int_d["type"]
    enabled = d.get(ENABLED_DISABLED_KEY, True)
    program_name = d.get(PROGRAM_NAME_KEY,"Program %d" % program_id)
    if not interval in even_odd_intervals:
        days = int_d[RUN_DAYS_KEY]
    else:
        days = None
    return Program(manager,
                   program_id,
                   program_name,
                   time_of_day,
                   interval,
                   enabled,
                   dow = days,
                   station_blocks = stations)

class Program(object):
    def __init__(self,
                 manager,
                 program_id,
                 program_name,
                 time_of_day,
                 interval,
                 enabled = True,
                 dow = None,
                 is_one_shot = False,
                 station_blocks = list()):
        self.manager = manager
        self.program_name = program_name
        self.logger = logging.getLogger(self.__class__.__name__)
        self.program_id  = program_id
        self.__time_of_day = time_of_day
        self.__running = False
        self.__enabled = enabled
        self.interval = interval
        self.dow = dow
        self.is_one_shot = is_one_shot
        self.station_blocks = station_blocks
        self.__sb_dict = OrderedDict()
        if not(self.station_blocks is None):
            for sb in self.station_blocks:
                sb.parent = self
                self.__sb_dict[sb.station_id] = sb
        self.__dirty = False
        if not(self.station_blocks is None) and len(self.station_blocks) > 0:
            self.fix_start_end()
    def __getitem__(self, key):
        return self.__sb_dict[key]
    def has_key(self, key):
        return self.__sb_dict.has_key(key)
    def get(self, key, default = None):
        return self.__sb_dict.get(key, default)
    def keys(self):
        return self.__sb_dict.keys()
    def values(self):
        return self.__sb_dict.values()
    def items(self):
        return self.__sb_dict.items()
    def __len__(self):
        return len(self.__sb_dict)
    @property
    def program_stations(self):
        stids = set()
        for sb in self.station_blocks:
            stids.add(sb.station_id)
        return list(stids)
    @property
    def dirty(self):
        return self.__dirty or reduce(lambda x,y: x or y.dirty, self.station_blocks,False)
    @dirty.setter
    def dirty(self, value):
        self.__dirty = value
        if not value:
            for sb in self.station_blocks:
                sb.dirty = False
    @property
    def time_of_day(self):
        return self.__time_of_day
    @time_of_day.setter
    def time_of_day(self, value):
        if not(isinstance(value, int) or isinstance(value, float)):
            raise TypeError(value)
        if self.__time_of_day != value:
            self.dirty = True
            self.__time_of_day = value
            self.fix_start_end()
    @property
    def running(self):
        running = False
        for sb in self.station_blocks:
            running = running or sb.in_station
        self.__running = running
        return self.__running
    @running.setter
    def running(self, value):
        if self.__running != value:
            self.__running = value
            self.manager.move_program(self, value)
            if not self.__running:
                for sb in self.station_blocks:
                    sb.in_station = False
    @property
    def enabled(self):
        return self.__enabled
    @enabled.setter
    def enabled(self, value):
        if self.__enabled != value:
            self.__enabled = value
            self.__dirty = True
            if not self.__enabled:
                for station in self.station_blocks:
                    station.in_station = False
    def fix_start_end(self):
        start = self.__time_of_day
        end = start
        for sb in self.station_blocks:
            adder = 0
            if sb.bound_station is None:
                adder = sb.duration
            else:
                if sb.bound_station.wired:
                    adder = sb.duration
                else:
                    adder = 0
            end += adder
        if end >= END_OF_DAY: # Force the end at the midnight boundary
            end = END_OF_DAY
        
        self.start_time = start
        self.end_time = end
        
    def serialize(self):
        int_d = {INTERVAL_TYPE_KEY : self.interval}
        if not self.interval in even_odd_intervals:
            int_d[RUN_DAYS_KEY]=self.dow
        d = OrderedDict()
        
        d[PROGRAM_ID_KEY] = self.program_id
        d[PROGRAM_NAME_KEY] = self.program_name
        d[ENABLED_DISABLED_KEY] = self.__enabled
        d[TIME_OF_DAY_KEY] = format_time_of_day(self.time_of_day)
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
        in_day = False
        if self.interval in even_odd_intervals and self.interval == even_odd:
            in_day = True
        elif self.interval == DOW_INTERVAL_TYPE:
            in_day = now["day"] in self.dow
        evaluation = TOO_EARLY
        if in_day:
            seconds = now["seconds_from_midnight"]
            if seconds < self.start_time:
                evaluation = TOO_EARLY
            elif seconds >= self.end_time:
                evaluation =  STOP
            else:
                evaluation =  START
        else:
            evaluation =  TOO_EARLY
        return evaluation
