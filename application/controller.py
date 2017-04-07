from copy import deepcopy
from collections import deque
from singleton import *
from core_config import *
from settings_keys import *
from clock import *
from dispatchers import *
from settings import *
from program_manager import *
from programs import *
from program_log import sqlite_program_log

class StationStates(object):
    def __init__(self, controller, program_station_block):
        self.__controller = controller
        self.__program_station_block = program_station_block
        self.__expired = False
        self.__running = False
        self.__run_time = 0
        self.__max_run_time = 0
        
        self.__station = program_station_block.bound_station
        self.__program_id = program_station_block.parent.program_id
        
        self.__max_run_time = self.__station.duration
    
    @property
    def expired(self):
        return self.__expired
    @property
    def running(self):
        return self.__running
    @running.setter
    def running(self, value):
        if not value == self.__running:
            self.__running = value
            self.__program_station_block.in_station = value
            self.__controller.update_state(self.__station, value)
    def is_part_of_program(self, program_id):
        if program_id == self.__program_id:
            return True
        else:
            return False
    def increase_time(self, value):
        self.__run_time += value
        if self.__run_time > self.__max_run_time:
            self.__expired = True
            self.running = False
        

class Controller(object):
    def __init__(self, dispatch_class = DefaultDispatcher, logger = sqlite_program_log):
        # self.program_manager = ProgramManager()
        # self.settings = Settings()
        # self.settings.load()
        # self.program_manager.load_programs()
        self.logger = logger
        self.__stations = None
        self.dispatcher = dispatch_class()
        self.__station_queue = deque()
        self.__running_program = None
        self.__last_time_check = None
        
        # Prepare internal states
        station_count = settings[STATIONS_AVAIL_KEY]
        self.state = [0 for x in xrange(station_count)]
        self.new_state = [0 for x in xrange(station_count)]
        self.full_stop_state = [0 for x in xrange(station_count)]
        self.__stations = settings[STATION_LIST_KEY]
        self.__state_changed = False
        
    def __time_check_and_update(self, now):
        now_s = now[TIME_EPOCH]
        if self.__last_time_check is None:
            self.__last_time_check = now_s
            return 0
        else:
            diff = now_s - self.__last_time_check
            self.__last_time_check = now_s
            return diff
    @property
    def stations(self):
        return self.__stations
    
    def __add_stations_to_queue(self, station_blocks):
        for sb in station_blocks:
            self.__station_queue.append(StationState(self, sb))
    
    def __purge_stations(self, program = None):
        if program is None:
            while len(self.__station_queue) > 0:
                ss = self.__station_queue.popleft()
                ss.running = False
        else:
            remove_list = list()
            program_id = program.program_id
            for ss in self.__station_queue:
                if ss.is_part_of_program(program_id):
                    remove_list.append(ss)
            for ss in remove_list:
                ss.running = False
                self.__station_queue.remove(ss)
    
    def update_state(self, station, value):
        bit = 0
        if self.station.wired: # Other checks can go in here (lockouts, etc)
            if value:
                bit = 1
            else:
                bit = 0
        self.new_state[station.station_id - 1] = bit
    
    def __manage_running_programs(self, now):
        program_to_run = program_manager.get_program_to_run(now)
        if not program_to_run is None:
            #If we have no running program
            if self.__running_program is None:
                # Make the time StationStates
                self.__add_stations_to_queue(program_to_run.station_blocks)
                
            # Check if we have an already running program, if so, kill it if it is not the same
            elif program_to_run.program_id != self.__running_program.program_id:
                # Kill already running program
                self.__purge_stations(program_to_run)
                program_to_run.running = False
                # Add in new program
                self.__running_program = program_to_run
                self.__add_stations_to_queue(program_to_run.station_blocks)
            else:
                pass
    
    def __service_queue(self, now):
        seconds_elapsed_since_last_tick = self.__time_check_and_update(now)
        # The left-most element of the queue is the most immediate station, and the only item to be serviced.
        # It is popped permanently when it has expired (whether by time or by force)
        station = self.__station.queue.popleft()
        
        station.increase_time(seconds_elapsed_since_last_tick)
        if not station.expired:
            self.__station_queue.appendleft(station)
    
    def __dispatch_io(self):
        if not self.state == self.new_state:
            self.dispatcher.write_pattern_to_register(self.state)
        self.state = deepcopy(self.new_state)
    
    def on_tick(self):
        # This is our main function. Should be called from some sort of loop
        # 1. We build now (year,month,day,day_of_week,hour,minute,second,seconds_from_midnight)
        # 2. Check if programs should run
        # 3. Service the queue and run list
        # 4. Dispatch IO
        
        # 1. Build now
        now = make_now()
        
        # 2. Check for programs:
        self.__manage_running_programs(now)
       
        #3. Service the queue
        self.__service_queue(now)
        
        # 4. Dispatch IO
        self.__dispatch_io()
                
        
