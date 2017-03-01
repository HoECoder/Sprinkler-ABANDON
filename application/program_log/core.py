from singleton import *
from core_config import *
from settings_keys import *
from clock import *
from settings import *
import json

class ConsoleProgramLog(object):
    def __init__(self):
        self.__stations = dict()
        self.__programs = dict()
        
    def load(self, filename):
        pass

    def log_program_start(self, program, now=None):
        pass

    def log_program_stop(self, program, now=None):
        pass

    def log_station_start(self, program, station_id, now=None):
        pass

    def log_station_stop(self, program, station_id, now=None):
        pass

    def persist(self):
        pass

    def register_programs(self, programs):
        for program in programs:
            serialized = program.serialize()
            s = json.dumps(serialized)
            print s
            self.__programs[program.program_id] = program

    def register_stations(self, stations):
        for station in stations:
            fmt = "SID: %d, Name: %d, Wired: %s, Ignore Rain: %s, Need Master: %s"
            s = fmt % (station.station_id,
                       station.name,
                       str(station.wired),
                       str(station.ignore_rain_sensor),
                       str(station.need_master))
            print s
            self.__stations[station.station_id] = station


