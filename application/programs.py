import logging
from clock import clock_parse, pretty_now, make_now, format_time_of_day
from collections import OrderedDict
from core_config import interval_types, END_OF_DAY, TIME_DUMP_FORMAT, STATION_ON_OFF
from settings_keys import *
import cerberus
from program_log import sqlite_program_log

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
                  TIME_OF_DAY_KEY : {"type" : "string"},
                  INTERVAL_KEY : {"type":"dict",
                                  "validator":validate_interval},
                  PROGRAM_NAME_KEY: {"type" : "string"},
                  STATION_DURATION_KEY : {"type" : "list",
                                          "schema" : {"type" : "dict",
                                                      "schema" : station_block_schema}}}

program_validator = cerberus.Validator(program_schema,allow_unknown = True)

def unpack_station_block(d, logger = sqlite_program_log):
    s = StationBlock(d[STATION_ID_KEY], d[DURATION_KEY], logger = logger)
    return s

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

class StationBlock(object):
    def __init__(self,
                 station_id,
                 duration,
                 start_time=0,
                 end_time=0,
                 parent = None,
                 logger = sqlite_program_log):
        self.station_id = station_id
        self.__duration = duration
        self.start_time = start_time
        self.end_time = end_time
        self.__in_station = False
        self.__dirty = False
        self.__changed = False
        self.parent = parent
        self.bound_station = None
        self.logger = logger
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
    @property
    def in_station(self):
        return self.__in_station
    @in_station.setter
    def in_station(self, value):
        if self.__in_station != value:
            self.__in_station = value
            self.__changed = True
            if self.__in_station and self.wired:
                self.logger.log_station_start(self.parent, self.station_id)
            elif (not self.__in_station) and self.wired:
                self.logger.log_station_stop(self.parent, self.station_id)
    @property
    def bit(self):
        in_station = self.__in_station
        if in_station and self.wired:
            return 1
        else:
            return 0
    @property
    def wired(self):
        bound_station_wired = False
        # We have to respect if the station is wired up or not
        if not self.bound_station is None:
            bound_station_wired = self.bound_station.wired
        #print self.station_id, bound_station_wired
        return bound_station_wired
    @property
    def changed(self):
        return self.__changed
    @changed.setter
    def changed(self, value):
        self.__changed = value
    def serialize(self):
        d = OrderedDict()
        d[STATION_ID_KEY] = self.station_id
        d[DURATION_KEY] = self.duration
        return d
    def within(self, now):
        seconds = now["seconds_from_midnight"]
        return self.start_time <= seconds and seconds < self.end_time

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
        return self.__running
    @running.setter
    def running(self, value):
        if self.__running != value:
            self.__running = value
            self.manager.move_program(self, value)
            # self.logger.debug("%s: Program %d %s", 
                              # pretty_now(make_now()), 
                              # self.program_id, 
                              # STATION_ON_OFF[value])
            #print "Program %s" % (STATION_ON_OFF[value])
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
        for sb in self.station_blocks:
            if start >= END_OF_DAY: # We force a 24 hour day
                start = END_OF_DAY
            sb.start_time = start
            sb.end_time = start + sb.duration
            start = sb.end_time
            if sb.end_time >= END_OF_DAY: # We force a 24 hour day
                self.end_time = END_OF_DAY
        self.min_start_time = min([sb.start_time for sb in self.station_blocks])
        self.max_end_time = max([sb.end_time for sb in self.station_blocks]) 
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
            if seconds < self.min_start_time:
                evaluation = TOO_EARLY
            elif seconds > self.max_end_time:
                evaluation =  STOP
            else:
                evaluation =  START
        else:
            evaluation =  TOO_EARLY
        return evaluation
