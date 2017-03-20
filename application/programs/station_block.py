from collections import OrderedDict

from settings_keys import *
from program_log import sqlite_program_log

class StationBlock(object):
    def __init__(self,
                 station_id,
                 duration,
                 start_time = 0,
                 end_time = 0,
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
        seconds = now[TIME_FROM_MIDNIGHT]
        return self.start_time <= seconds and seconds < self.end_time

def unpack_station_block(d, logger = sqlite_program_log):
    s = StationBlock(d[STATION_ID_KEY], d[DURATION_KEY], logger = logger)
    return s