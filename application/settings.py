import os
import os.path
import ConfigParser
from copy import deepcopy
from collections import OrderedDict
from core_config import master_file_name,master_path
from settings_keys import *
from programs import *

boolean_conf_keys = [RAIN_SENSOR_KEY,
                     INVERT_RAIN_SENSOR_KEY,
                     WIRED_KEY,
                     IGNORE_RAIN_KEY,
                     NEED_MASTER_KEY]
int_conf_keys = [STATIONS_AVAIL_KEY]
float_conf_keys = []

class Settings(object):
    def __init__(self,config_file=master_path):
        self.settings_file_name = config_file
        exists = os.path.exists(application_base_dir)
        if not exist:
            os.makedirs(application_base_dir)
        self.__settings = None
        self.dirty = False
    def __getitem__(self,key):
        if self.__settings is None:
            raise KeyError("Settings Not Initialized")
        return self.__settings[key]
    def load(self):
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
        
class ProgramManager(object):
    def __init__(self):
        self.__programs = OrderedDict()
    def __getitem__(self,key):
        return self.__programs[key]
    def add_program(self,program):
        pass
    def delete_program(self,program):
        pass
    def write_programs(self):
        for pid, program in self.__programs.items():
            if program.is_dirty: # Effeciency, less disk access
                pass # TODO : Persist code here
    def load_programs(self):
        pass