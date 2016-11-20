
from collections import OrderedDict
from core_config import interval_types
from settings_keys import *
import cerberus

even_odd_intervals = [EVEN_INTERVAL_TYPE,
                      ODD_INTERVAL_TYPE]
                                 
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
                 end_time=0):
        self.station_id = station_id
        self.duration = duration
        self.start_time = start_time
        self.end_time = end_time
        self.in_station = False
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
                 station_blocks = None):
        self.program_id  = program_id
        self.time_of_day = time_of_day
        self.running = False
        self.interval = interval
        self.dow = dow
        self.is_one_shot = is_one_shot
        self.station_blocks = station_blocks
        self.is_dirty = False
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
