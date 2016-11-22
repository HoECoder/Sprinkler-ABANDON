import os
import os.path
import glob
import ConfigParser
import json
from copy import deepcopy
from collections import OrderedDict
from core_config import master_file_name,master_path,programs_path,program_name_template
from settings_keys import *
from programs import *
from singleton import *

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
        if not exist:
            os.makedirs(application_base_dir)
        self.__settings = None
        self.dirty = False
    def __getitem__(self, key):
        if self.__settings is None:
            raise KeyError("Settings Not Initialized")
        return self.__settings[key]
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
        sections = conifg.sections()
        # Load the main options
        main_opts = config.options(MAIN_SECTION)
        for opt in main_opts:
            master[opt] = config.get(MAIN_SECTION, opt)
        # Load the station info
        station_list = OrderedDict()
        master[STATION_LIST_KEY] = station_list
        # The Station configurations are in an unbounded list by section
        # So we need to loop through all of them
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
    def __init__(self, programs_path = program_logs_path):
        self.programs_path = programs_path
        exists = os.path.exists(self.programs_path)
        if not exist:
            os.makedirs(self.programs_path)
        self.__programs = OrderedDict()
        self.program_glob = os.path.join(self.programs_path, program_name_glob)
        self.dirty = False
    def __getitem__(self,key):
        return self.__programs[key]
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
    def add_program(self, program, write_through = False):
        pass
    def delete_program(self, program):
        pass
    def write_programs(self):
        for pid, program in self.__programs.items():
            if program.is_dirty: # Effeciency, less disk access
                # Force the program to serialize, then turn the resultant into a JSON string
                # This makes a nice, user friendly format
                s = program.serialize()
                file_name = os.path.join(self.programs_path, program_name_template % program.program_id)
                try:
                    program_file = open(filename,"wb")
                    json.dump(s, program_file, indent = 4)
                    program_file.flush()
                    program_file.close()
                    del program_file
                    program.dirty = False
                except IOError, e:
                    pass
                except ValueError, e:
                    pass
                except TypeError, e:
                    pass
    def load_programs(self):
        program_paths = glob.glob(self.program_glob)
        programs = OrderedDict()
        for pp in program_paths:
            try:
                program_file = open(pp,"rb")
                program_d = json.load(program_file)
                program = unpack_program(program_d)
                programs[program.program_id] = program
                program_file.close()
                del program_file
            except IOError, e:
                pass #TODO : Figure out a better thing to do here
        if len(programs) > 0:
            self.__programs = programs
            self.dirty = False
            return True
        else:
            return False

