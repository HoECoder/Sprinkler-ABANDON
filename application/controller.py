from copy import deepcopy
from singleton import *
from core_config import *
from settings_keys import *
from clock import *
from dispatchers import *
from settings import *
from program_manager import *
from programs import *

@singleton
class Controller(object):
    def __init__(self, dispatch_class = DefaultDispatcher):
        self.program_manager = ProgramManager()
        self.settings = Settings()
        self.settings.load()
        self.program_manager.load_programs()
        self.dispatcher = DefaultDispatcher()
        self.__prepare_state()
    def __prepare_state(self):
        station_count = self.settings['stations available']
        self.state = [0 for x in xrange(station_count)]
        self.full_stop_state = [0 for x in xrange(station_count)]
    def on_tick(self):
        # This is our main function. Should be called from some sort of loop
        # 1. We build now (year,month,day,day_of_week,hour,minute,second,seconds_from_midnight)
        # 2. Loop over programs and mark as running those programs that should run
        # 3. Loop over running programs
        # 3.a. Stop any expired programs
        # 3.b. Advance any running program
        
        # 1. Build now
        now = make_now()
        
        # 2. Loop over all programs for today and find those that need to start
        programs_that_should_run = self.program_manager.programs_that_should_run(now)
        
        # 3. Loop over these running programs
        for program in self.program_manager.running_programs():
            value = program.evaluate(now)
            # 3.a. Stop expired programs
            if value in [TOO_EARLY, STOP]: # If we are running and we get either, full stop
                # Stop the program
                program.running = False
                # Dispatch a Stop
                stations = program.program_stations
                for station in stations:
                    self.state[station - 1] = 0
                self.dispatcher.write_pattern_to_register(self.state)
            else:
                # 3.b We are in a running program (or a program that needs to run)
                changed_stations = dict()
                # Loop through the stations and look for stations that fall within our times
                for station in program.station_blocks:
                    if station.within(now):
                        #Inside a station, turn it on
                        bit = 1
                        station.in_station = True
                    else:
                        #Not in a station, turn it off
                        bit = 0
                        station.in_station = False
                    if station.changed:
                        station.changed = False
                        changed_stations[station.station_id] = bit
                if len(changed_stations) > 0:
                    for station_id, state in changed_stations.items():
                        self.state[station_id - 1] = state
                    self.dispatcher.write_pattern_to_register(self.state)
                
        
