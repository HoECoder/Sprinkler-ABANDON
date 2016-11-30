from collections import OrderedDict
from core_config import *
from settings_keys import *
from programs import *
from singleton import *
from program_log_sql import *
from program_manager import ProgramManager
from settings import Settings

class ProgramLog(object):
    def register_programs(self, programs):
        pass
    def register_stations(self, stations):
        pass
    def log_start(self, program, now):
        pass
    def log_stop(self, program, now):
        pass
    def log_station_start(self, program, station, now):
        pass
    def log_station_stop(self, program, station, now):
        pass

import sqlite3
@singleton
class SQLiteProgramLog(ProgramLog):
    def __init__(self,
                 sqlite3_filename = ""):
        self.sqlite3_filename = sqlite3_filename
        self.conn = sqlite3.connect(sqlite3_filename)
        self.__prepare_tables()
        self.settings = Settings()
        self.program_manager = ProgramManager()
        
        self.settings.load()
        self.program_manager.load()
    def __prepare_tables(self):
        self.conn.executescript(program_log_sql)
        self.conn.commit()
    def __enter_programs(self, programs):
        program_insert_string = "insert into programs (program_id, name, interval_type, time_of_day) values (?)"
        inserts = list()
        for program in programs:
            insert = (program.program_id, program.program_name, sql_interval_map[program.interval], program.time_of_day)
            inserts.append(insert)
        self.conn.executemany(program_insert_string, inserts)
        self.conn.commit()
    def __enter_stations(self, stations):
        station_insert_string = "insert into stations (station_id, station_name) values (?)"
        inserts = list()
        for station in stations:
            insert = (station.station_id, station.name)
            inserts.append(insert)
        self.conn.executemany(station_insert_string, inserts)
        self.conn.commit()
