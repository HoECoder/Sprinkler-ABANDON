import logging
import logging.handlers
from controller import *
from clock import sim_clock
import time
from program_manager import program_manager
from settings import settings
from program_log import sqlite_program_log, console_log
import argparse

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

def get_default_sqlite_file_name():
    t = time.localtime()
    s = r"D:\controller\t_%04d%02d%02d_%02d%02d%02d.db3" % (t.tm_year,
                                                            t.tm_mon,
                                                            t.tm_mday,
                                                            t.tm_hour,
                                                            t.tm_min,
                                                            t.tm_sec)
    return s

fmt_1 = "%x"
fmt_2 = "%Y-%m-%d"
fmt_3 = "%Y/%m/%d"
fmt_4 = "%y-%m-%d"
fmt_5 = "%y/%m/%d"
fmts = [fmt_1, 
        fmt_2, 
        fmt_3, 
        fmt_4, 
        fmt_5]
def parse_a_time(str):
    i = 0
    l = len(fmts)
    t = None
    while i < l:
        try:
            fmt = fmts[i]
            t = time.strptime(str, fmt)
            i = l
        except ValueError:
            i += 1
    return t
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test a controller in a tight time-loop')
    log_group = parser.add_mutually_exclusive_group()
    parser.add_argument("-s", 
                        "--set_date",
                        metavar = "StartDate",
                        type = parse_a_time,
                        default = None,
                        help = "Change the start of the sim-clock, defaults to today")
    log_group.add_argument("-f", 
                           "--file",
                           metavar = "SQLiteFile",
                           default = get_default_sqlite_file_name(),
                           help = "Test database for logging")
    log_group.add_argument("-c",
                           "--console",
                           action='store_true',
                           default = False,
                           help = "Log to the console")
    parser.add_argument("-d", 
                        "--days",
                        metavar = "Days",
                        help = "Number of days to simulate; default is 30",
                        default = 30,
                        type=int)
    parser.add_argument("-m", 
                        "--months",
                        metavar = "Months",
                        help = "Number of months (30 d) to simulate",
                        default = 0,
                        type=int)
    parser.add_argument("-y", 
                        "--years",
                        metavar = "Years",
                        help = "Number of years (365 d) to simulate",
                        default = 0,
                        type=int)
    args = parser.parse_args()
    print args
    s = sim_clock
    if args.set_date is None:
        s.reset_to_today()
    else:
        s.set_arbitrary_time(args.set_date)
    total_start = time.time()
    d2d_start = 0
    d2d_end = 0
    changes = 0
    new_changes = 0
    try:
        if args.console:
            program_manager.logger = console_log
            logger = console_log
        else:
            program_manager.logger = sqlite_program_log
            sqlite_program_log.load(args.file)
            logger = sqlite_program_log
        settings.load()
        program_manager.load_programs()
        controller = Controller()
        # print controller.stations
        program_manager.bind_stations(controller.stations)
        logger.register_stations(settings.stations.values())
        logger.register_programs(program_manager.values())
        
        changes = logger.total_changes
        i = 0
        day = 24*3600
        run_time = day * (args.days + 30 * args.months + 365 * args.years)
        while i < run_time:
            if i % day == 0:
                print "Day %d" % ((i/day) + 1)
            controller.on_tick()
            
            new_changes = logger.total_changes
            if new_changes != changes:
                
                #print "\t%d new changes" % (new_changes-changes)
                changes = new_changes
            i += 1
            s.tick()
        logger.persist()
    except KeyboardInterrupt:
        print "\nCTRL-C caught, Shutdown"
        logger.persist()
    total_end = time.time()
    print "Run time : %f" % (total_end-total_start)