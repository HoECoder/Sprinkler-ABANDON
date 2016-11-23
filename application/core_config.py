#
# core_config.py
# Home of core variables/constants for the aaplication.
#
# Import os to check version and set paths:
import os
import os.path
from settings_keys import EVEN_INTERVAL_TYPE,ODD_INTERVAL_TYPE,DOW_INTERVAL_TYPE

if os.name == "nt":
    application_base_dir = "D:\\controller\\config"
else:
    application_base_dir = os.path.expanduser("~/.controller")
#
# Master config file:
master_file_name = "master.cfg"
master_path = os.path.join(application_base_dir,master_file_name)
#
# Program locations
programs_path_part = "programs"
programs_path = os.path.join(application_base_dir,programs_path_part)
program_name_glob = "program.*.json"
program_name_template = "program.%d.json"
#
# Log files:
#
# Programs
program_logs = "logs"
program_logs_path = os.path.join(application_base_dir,program_logs)
program_log_name_template = "program.%s.log"
# Application
application_log = "controller.runtime.log"
application_log_path = os.path.join(application_base_dir,application_log)
#
# GPIO Configurations
#
# I'm assuming a RPi A+/B+ or RPi 2
# Swiped the definition from OpenSprinkler Unified Firmware
# OpenSprinkler-Firmware/defines.h
# https://github.com/OpenSprinkler/OpenSprinkler-Firmware/blob/a62856969722f8185b1168737b67d8497ffb95b2/defines.h#L307
pin_sr_dat = 27 # Shift Register Data Pin
pin_sr_clk = 4  # Shift Register Clock Pin
pin_sr_oe = 17  # Shift Register Output Enable Pin
pin_sr_lat = 22 # Shift Register Latch Pin

# Collection of GPIO pins
gpio_pins = [pin_sr_dat,
             pin_sr_clk,
             pin_sr_oe,
             pin_sr_lat]

#Map GPIO pins to human text             
gpio_pin_names = {pin_sr_dat : "pin_sr_dat",
                  pin_sr_clk : "pin_sr_clk",
                  pin_sr_oe : "pin_sr_oe",
                  pin_sr_lat : "pin_sr_lat"}

# Map GPIO pins to more friendly text
gpio_pin_help = {pin_sr_dat : "SR Data",
                 pin_sr_clk : "SR Clock",
                 pin_sr_oe : "SR Output Enable",
                 pin_sr_lat : "SR Latch"}

interval_types = [EVEN_INTERVAL_TYPE,
                  ODD_INTERVAL_TYPE,
                  DOW_INTERVAL_TYPE]

# End of Day
END_OF_DAY = 86400
# Format for parsing times in programs
TIME_PARSE_FORMAT = "%H:%M:%S"
TIME_DUMP_FORMAT = "%02d:%02d:%02d"
#
STATION_ON_TEXT = "On"
STATION_OFF_TEXT = "Off"
STATION_ON_OFF = {True: STATION_ON_TEXT,
                  False: STATION_OFF_TEXT}
# Simulation parameters
SIMULATE_GPIO = True
# Fake a clock for testing purposes, goes as quickly as possible
# If set, will force SIMULATE_GPIO to True, for safety reasons
SIMULATE_TIME = True
if SIMULATE_TIME:
    SIMULATE_GPIO = True
