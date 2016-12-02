#!/usr/bin/python
from dispatchers import *

if __name__ == "__main__":
    import time
    dispatcher = GPIODispatcher()
    zero_pattern = [0 for x in xrange(8)]
    pattern = [0 for x in xrange(8)]
    i = 0
    try:
        print "Starting"
        while True:
            idx = i % 8
            pattern[idx] = 1
            print pattern
            dispatcher.write_pattern_to_register(pattern)
            pattern[idx] = 0
            i += 1
            time.sleep(2)
    except KeyboardInterrupt:
        print ""
        print "Stop"
        dispatcher.write_pattern_to_register(pattern)

