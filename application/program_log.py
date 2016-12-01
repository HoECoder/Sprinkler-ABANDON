from singleton import *
from core_config import *
from settings_keys import *
from clock import *
from settings import *
from program_log_sql import *

import sqlite3
class SQLiteProgramLog(object):
    def __init__(self):
        self.sqlite3_filename = None
        self.conn = None

    def load(self, sqlite3_filename):
        self.sqlite3_filename = sqlite3_filename
        self.conn = sqlite3.connect(sqlite3_filename)
        self.__prepare_tables()
    
    def __prepare_tables(self):
        self.conn.executescript(program_log_sql)
        event_types = list()
        for event, id in sql_event_map.items():
            event_types.append((id, event))
        interval_types = list()
        for interval, id in sql_interval_map.items():
            interval_types.append((id, interval))
        self.conn.executemany(event_type_insert, event_types)
        self.conn.executemany(interval_type_insert, interval_types)
        self.conn.commit()
        
    def __enter_programs(self, programs):
        inserts = list()
        for program in programs:
            tod = format_time_of_day(program.time_of_day)
            insert = (program.program_id, program.program_name, sql_interval_map[program.interval], tod)
            inserts.append(insert)
        self.conn.executemany(program_insert_string, inserts)
        self.conn.commit()
        
    def __enter_stations(self, stations):
        inserts = list()
        for station in stations:
            insert = (station.station_id, station.name)
            inserts.append(insert)
        self.conn.executemany(station_insert_string, inserts)
        self.conn.commit()
        
    def persist(self):
        self.conn.commit()
    
    def register_programs(self, programs):
        self.__enter_programs(programs)
        
    def register_stations(self, stations):
        self.__enter_stations(stations)
        
    def __log_program_event(self, program, event, now = None):
        if now == None:
            now = make_now()
        event_id = sql_event_map[event]
        self.conn.execute(program_event_insert, (now['epoch'], program.program_id, event_id))
        #self.conn.commit()
        
    def log_program_start(self, program, now = None):
        self.__log_program_event(program, sql_event_start, now)
        
    def log_program_stop(self, program, now = None):
        self.__log_program_event(program, sql_event_stop, now)
        
    def __log_station_event(self, program, station_id, event, now = None):
        if now == None:
            now = make_now()
        event_id = sql_event_map[event]
        self.conn.execute(station_event_insert, (now['epoch'], station_id, event_id))
        #self.conn.commit()
        
    def log_station_start(self, program, station_id, now = None):
        self.__log_station_event(program, station_id, sql_event_start, now)
        
    def log_station_stop(self, program, station_id, now = None):
        self.__log_station_event(program, station_id, sql_event_stop, now)

sqlite_program_log = SQLiteProgramLog()