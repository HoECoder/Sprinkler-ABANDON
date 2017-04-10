from core_config import *
from settings_keys import *
from clock import *
import json

start_key = "Start::"
stop_key =  "Stop:: "

class NullLog(object):
    def __init__(self):
        pass
        
    def load(self, filename):
        pass
    @property
    def total_changes(self):
        return 0
        
    def __booking(self, event, lookup_id, book, now = None):
        pass
        #Should have an else here with an error

    def __log_program_event(self, event, program, now = None):
        pass

    def log_program_start(self, program, now = None):
        pass
    def log_program_stop(self, program, now = None):
        pass

    def __log_station_event(self, event, program, station_id, now = None):
        pass

    def log_station_start(self, program, station_id, now = None):
        pass
    def log_station_stop(self, program, station_id, now = None):
        pass

    def persist(self):
        pass

    def register_programs(self, programs):
        pass

    def register_stations(self, stations):
        pass


