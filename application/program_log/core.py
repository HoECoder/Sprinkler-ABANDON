from core_config import *
from settings_keys import *
from clock import *
import json

start_key = "Start::"
stop_key =  "Stop:: "

class ConsoleProgramLog(object):
    def __init__(self):
        self.__stations = dict()
        self.__programs = dict()
        self.__program_book = dict()
        self.__station_book = dict()
        
    def load(self, filename):
        pass
    @property
    def total_changes(self):
        return 0
        
    def __booking(self, event, lookup_id, book, now = None):
        if event == start_key:
            value = book.pop(lookup_id, None)
            book[lookup_id] = now
            if value is None:
                return 0
            else:
                diff = now[TIME_EPOCH] - value[TIME_EPOCH]
                return diff
        elif event == stop_key:
            value = book.pop(lookup_id, None)
            if value is None:
                return 0 # Should do something fancier here
            else:
                diff = now[TIME_EPOCH] - value[TIME_EPOCH]
                return diff
        #Should have an else here with an error

    def __log_program_event(self, event, program, now = None):
        fmt = "Program %s PID: %d, Name: %s, Time: %s"
        if now is None:
            now = make_now()
        d = self.__booking(event, program.program_id, self.__program_book, now)
        t = pretty_now(now)
        s = fmt % (event, 
                   program.program_id,
                   program.program_name,
                   t)
        print s
        if event == stop_key:
            print "Program Run Time: %0.1f" % d

    def log_program_start(self, program, now = None):
        self.__log_program_event(start_key, program, now)
    def log_program_stop(self, program, now = None):
        self.__log_program_event(stop_key, program, now)

    def __log_station_event(self, event, program, station_id, now = None):
        fmt = "Station %s PID: %d, PName: %s, SID: %d, SName: %s, Time: %s"
        
        if now is None:
            now = make_now()
        
        d = self.__booking(event, program.program_id, self.__station_book, now)
        t = pretty_now(now)
        station = self.__stations.get(station_id, None)
        if station is None:
            station_name = "BAD STATION"
        else:
            station_name = station.name
        s = fmt % (event, 
                   program.program_id,
                   program.program_name,
                   station_id,
                   station_name,
                   t)
        print s
        if event == stop_key:
            print "Station Run Time: %0.1f" % d

    def log_station_start(self, program, station_id, now = None):
        self.__log_station_event(start_key, program, station_id, now)
    def log_station_stop(self, program, station_id, now = None):
        self.__log_station_event(stop_key, program, station_id, now)

    def persist(self):
        pass

    def register_programs(self, programs):
        print "Register Programs"
        for program in programs:
            serialized = program.serialize()
            serialized["start_time"] = program.start_time
            serialized["end_time"] = program.end_time
            s = json.dumps(serialized)
            s= "\t" + s
            print s
            self.__programs[program.program_id] = program

    def register_stations(self, stations):
        print "Register Stations"
        for station in stations:
            fmt = "\tSID: %d, Name: %s, Wired: %s, Ignore Rain: %s, Need Master: %s"
            s = fmt % (station.station_id,
                       station.name,
                       str(station.wired),
                       str(station.ignore_rain_sensor),
                       str(station.need_master))
            print s
            self.__stations[station.station_id] = station


