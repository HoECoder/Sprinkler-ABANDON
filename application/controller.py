from copy import deepcopy
from singleton import *
from core_config import *
from settings_keys import *
from clock import *
from dispatchers import *
from settings import *
from programs import *

@singleton
class Controller(object):
    def __init__(self, dispatch_class = DefaultDispatcher):
        self.program_manager = ProgramManager()
        self.settings = Settings()
        self.settings.load()
        self.program_manager.load()
        self.dispatcher = DefaultDispatcher()
    def on_tick(self):
        # This is our main function. Should be called from some sort of loop
        # 1. We build now (year,month,day,day_of_week,hour,minute,second,seconds_from_midnight)
        # 2. We find any running programs
        # 3. Loop over the programs (including the one_shot_program)
        # 3.a If the program is expired, stop it
        # 3.b If a program is live, possibly advance its stations
        # 3.c If a new program is up, start it
        # 4. Periodically persist settings and programs
        
        #1. Build now
        now = make_now()
        
        #2. Loop over all programs for today and find those that need to start
        programs_that_should_run = self.program_manager.programs_that_should_run()
        for program in programs_that_should_run:
            program.running = True #These will now show in the running programs list
        
        #3. Get the running programs
        running = self.program_manager.running_programs()
        
        #4. Loop over these running programs
        for program in running:
            value = program.evaluate(now)
            if value in [TOO_EARLY, STOP]: # If we are running and we get either, full stop
                # Stop the program
                program.running = False
                # Dispatch a Full Stop
            else:
                # Program may need to advance a station
                pass
        
