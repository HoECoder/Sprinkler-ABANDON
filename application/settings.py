import os
import os.path
import glob
import ConfigParser
import json
from copy import deepcopy
from collections import OrderedDict
from core_config import *
from settings_keys import *
from programs import *
from singleton import *
from utility import find_key_gap
from clock import pretty_now

boolean_conf_keys = [RAIN_SENSOR_KEY,
                     INVERT_RAIN_SENSOR_KEY,
                     WIRED_KEY,
                     IGNORE_RAIN_KEY,
                     NEED_MASTER_KEY]
int_conf_keys = [STATIONS_AVAIL_KEY]
float_conf_keys = []

@singleton
class Settings(object):
    def __init__(self, config_file = master_path):
        self.settings_file_name = config_file
        exists = os.path.exists(application_base_dir)
        if not exists:
            os.makedirs(application_base_dir)
        self.__settings = None
        self.dirty = False
    def __getitem__(self, key):
        if self.__settings is None:
            raise KeyError("Settings Not Initialized")
        return self.__settings[key]
    def __setitem__(self, key, value):
        if self.__settings is None:
            raise KeyError("Settings Not Initialized")
        self.__settings[key] = value
        self.dirty = True
    def has_key(self, key):
        return self.__settings.has_key(key)
    def keys(self):
        return self.__settings.keys()
    def values(self):
        return self.__settings.values()
    def items(self):
        return self.__settings.items()
    def __len__(self):
        return len(self.__settings)
    def load(self):
        # The master settings file is in a INI-style format
        config = ConfigParser.ConfigParser()
        fs = config.read(self.settings_file_name)
        if len(fs) == 0:
            return False
        master = OrderedDict()
        sections = config.sections()
        # Load the main options
        main_opts = config.options(MAIN_SECTION)
        for opt in main_opts:
            master[opt] = config.get(MAIN_SECTION, opt)
        # Load the station info
        station_list = OrderedDict()
        master[STATION_LIST_KEY] = station_list
        # The Station configurations are in an unbounded list by section
        # So we need to loop through all of them
        sections.remove(MAIN_SECTION)
        for section in sections:
            station_id = int(section.split(' ')[1])
            options = config.options(section)
            __od = OrderedDict()
            for option in options:
                if option in boolean_conf_keys:
                    __od[option] = config.getboolean(section, option)
                elif option in int_conf_keys:
                    __od[option] = config.getint(section, option)
                elif option in float_conf_keys:
                    __od[option] = config.getfloat(section, option)
                else:
                    __od[option] = config.get(section, option)
            station_list[station_id] = __od
        master[STATIONS_AVAIL_KEY] = int(master[STATIONS_AVAIL_KEY])
        self.__settings = master
        return True
    def dump(self,force = False):
        if self.__settings is None:
            return False
        # For performance reasons, we will not touch the disk unless there is a change or we are forcing
        if not self.dirty and not force:
            return True
        # Make a deep copy, we don't want to accidentally muck the settings in memory
        conf = deepcopy(self.__settings)
        config = ConfigParser.ConfigParser()
        station_list = conf.pop(STATION_LIST_KEY, None)
        # Write main settings
        config.add_section(MAIN_SECTION)
        for key, val in conf.items():
            config.set(MAIN_SECTION, key, val)
        # Write out the individual station settings
        for key, val in station_list.items():
            header = STATION_SECTION_KEY % key
            config.add_section(header)
            for k2, v2 in val.items():
                config.set(header, k2, v2)
        fi = open(self.settings_file_name, "wb")
        config.write(fi)
        fi.flush()
        fi.close()
        del fi
        self.dirty = False

@singleton # ProgramManager is a Singleton  
class ProgramManager(object):
    def __init__(self, programs_path = programs_path):
        self.programs_path = programs_path
        exists = os.path.exists(self.programs_path)
        if not exists:
            os.makedirs(self.programs_path)
        self.__programs = OrderedDict()
        self.program_glob = os.path.join(self.programs_path, program_name_glob)
    def __getitem__(self, key):
        return self.__programs[key]
    def __setitem__(self, program_id, new_program):
        program = self.__programs.get(program_id, None)
        if program is None:
            self.add_program(new_program)
        else:
            self.__programs[program_id] = new_program
            new_program.dirty = True
    def has_key(self, key):
        return self.__programs.has_key(key)
    def keys(self):
        return self.__programs.keys()
    def values(self):
        return self.__programs.values()
    def items(self):
        return self.__programs.items()
    def __len__(self):
        return len(self.__programs)
    @property
    def dirty(self):
        return reduce(lambda a, b: a or b.dirty, self.__programs.values(), False)
    def add_program(self, program, write_through = False):
        program_key_set = self.__programs.keys()
        program_id = find_key_gap(program_key_set)
        program.program_id = program_id
        self.__programs[program_id] = program
        program.dirty = True
        if write_through:
            self.write_program(program)
        return program_id
    def delete_program(self, program_id):
        program = self.__programs.pop(program_id, None)
        program.dirty = False
        file_part = program_name_template % program.program_id
        full_path = os.path.join(program_logs_path, file_part)
        os.remove(full_path)
        program.program_id = 0
        return program
    def write_program(self, program):
        file_name = os.path.join(self.programs_path, program_name_template % program.program_id)
        program_file = open(file_name,"wb")
        s = program.serialize()
        json.dump(s, program_file, indent = 4)
        program_file.flush()
        program_file.close()
        del program_file
        program.dirty = False
    def write_programs(self):
        for pid, program in self.__programs.items():
            if program.dirty: # Effeciency, less disk access
                # Force the program to serialize, then turn the resultant into a JSON string
                # This makes a nice, user friendly format
                self.write_program(program)
    def load_programs(self):
        program_paths = glob.glob(self.program_glob)
        programs = OrderedDict()
        loaded = 0
        for pp in program_paths:
            try:
                program_file = open(pp,"rb")
                program_d = json.load(program_file)
                program = unpack_program(program_d)
                programs[program.program_id] = program
                program_file.close()
                del program_file
                loaded += 1
            except IOError, e:
                print str(e)
        if len(programs) > 0:
            self.__programs = programs
            return loaded
        else:
            return loaded
    def running_programs(self):
        return filter(lambda prog: prog.running, self.__programs.values())
    def non_running_programs(self):
        return filter(lambda prog: not prog.running, self.__programs.values())
    def programs_for_today(self, now):
        if now["day"] % 2 == 0:
            even_odd = EVEN_INTERVAL_TYPE
        else:
            even_odd = ODD_INTERVAL_TYPE
        dow = now["day_of_week"]
        even_odds = filter(lambda prog: prog.interval == even_odd, self.__programs.values())
        dows = filter(lambda prog: prog.interval == DOW_INTERVAL_TYPE and dow in prog.dow, self.__programs.values())
        todays_programs = list()
        todays_programs.extend(even_odds)
        todays_programs.extend(dows)
        return todays_programs
    def programs_that_should_run(self, now):
        return filter(lambda prog: prog.evaluate(now) == START, self.programs_for_today(now))
