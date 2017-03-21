from copy import deepcopy
from singleton import *
from core_config import *
from settings_keys import *
from clock import *
from dispatchers import *
from settings import *
from program_manager import *
from programs import *
from program_log import sqlite_program_log

class Controller(object):
    def __init__(self, dispatch_class = DefaultDispatcher, logger = sqlite_program_log):
        # self.program_manager = ProgramManager()
        # self.settings = Settings()
        # self.settings.load()
        # self.program_manager.load_programs()
        self.logger = logger
        self.__stations = None
        self.dispatcher = dispatch_class()
        self.__prepare_state()
        self.__station_queue = None
    def __prepare_state(self):
        station_count = settings[STATIONS_AVAIL_KEY]
        self.state = [0 for x in xrange(station_count)]
        self.full_stop_state = [0 for x in xrange(station_count)]
        self.__stations = settings[STATION_LIST_KEY]
    @property
    def stations(self):
        return self.__stations
    def on_tick(self):
        # This is our main function. Should be called from some sort of loop
        # 1. We build now (year,month,day,day_of_week,hour,minute,second,seconds_from_midnight).
        # 2. Check if programs should run, add their stations to the queue. Queue is time-ordered.
        # 3. Service the queue and run list
        # 3.a. If the station in the run list has expired, prepare a stop, remove it from the run list.
        # 3.b. If the station in the run list still needs to run, increment its counter.
        # 3.c. If the run list is empty, pop the next item out of the queue and start it.
        # 3.d. If we've received a request to stop the currently executing station, prepare a stop, 
        #      remove it from the run list. Pop the next item out of the queue.
        # 4. Dispatch IO
        
        # 1. Build now
        now = make_now()
        
        # 2. Get programs that should run now.
        running_programs = program_manager.programs_that_should_run(now)
        
        
        # 4. Dispatch IO
        if len(changed_stations) > 0:
            for station_id, state in changed_stations.items():
                self.state[station_id - 1] = state
            self.dispatcher.write_pattern_to_register(self.state)
        
        #sqlite_program_log.persist()
                
        
