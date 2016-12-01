import logging
import logging.handlers
from controller import *
from clock import sim_clock
import time
from program_manager import program_manager
from settings import settings
from program_log import sqlite_program_log

if os.name == "nt":
    log_filename = "D:\\toys\\controller\\controller.log"
    program_log = application_log_path
else:
    log_filename = os.path.expanduser("~/.controller/controller.log")
    program_log = application_log_path

fmt = logging.Formatter('%(name)s:%(levelname)s: %(message)s')
program_handler = logging.handlers.RotatingFileHandler(program_log,
                                                       maxBytes=1024*1024,
                                                       backupCount=100)
program_handler.setFormatter(fmt)
logging.getLogger('Program').addHandler(program_handler)

if __name__ == "__main__":
    s = sim_clock
    s.reset_to_today()
    total_start = time.time()
    d2d_start = 0
    d2d_end = 0
    try:
        settings.load()
        program_manager.load_programs()
        controller = Controller()
        sqlite_program_log.load(r"D:\controller\t.db3")
        sqlite_program_log.register_stations(settings.stations.values())
        sqlite_program_log.register_programs(program_manager.values())
        
        i = 0
        day = 24*3600
        run_time = day * 30
        while i < run_time:
            if i % day == 0:
                print "Day %d" % ((i/day) + 1)
            controller.on_tick()
            if i > 1 and i % 10 == 0:
                sqlite_program_log.persist()
            i += 1
            s.tick()
    except KeyboardInterrupt:
        print "\nCTRL-C caught, Shutdown"
    total_end = time.time()
    print "Run time : %f" % (total_end-total_start)