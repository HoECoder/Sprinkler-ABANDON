simple_program_1 = """{
    "pid": 1, 
    "name": "Program 1", 
    "enabled": true, 
    "time_of_day": "12:05:00", 
    "interval": {
        "type": "even"
    }, 
    "station_duration": [
        {
            "stid": 1, 
            "duration": 5
        }, 
        {
            "stid": 2, 
            "duration": 5
        }, 
        {
            "stid": 3, 
            "duration": 5
        }, 
        {
            "stid": 4, 
            "duration": 5
        }, 
        {
            "stid": 5, 
            "duration": 5
        }, 
        {
            "stid": 6, 
            "duration": 5
        }, 
        {
            "stid": 7, 
            "duration": 5
        }, 
        {
            "stid": 8, 
            "duration": 5
        }
    ]
}"""

simple_program_2 = """{
    "pid": 2, 
    "name": "Program 2", 
    "enabled": true, 
    "time_of_day": "12:05:00", 
    "interval": {
        "type": "odd"
    }, 
    "station_duration": [
        {
            "stid": 1, 
            "duration": 5
        }, 
        {
            "stid": 2, 
            "duration": 5
        }, 
        {
            "stid": 3, 
            "duration": 5
        }, 
        {
            "stid": 4, 
            "duration": 5
        }, 
        {
            "stid": 5, 
            "duration": 5
        }, 
        {
            "stid": 6, 
            "duration": 5
        }, 
        {
            "stid": 7, 
            "duration": 5
        }, 
        {
            "stid": 8, 
            "duration": 5
        }
    ]
}"""

simple_programs = [simple_program_1, simple_program_2]

short_day_dst_tester_program = """{
    "pid": 1, 
    "name": "Short Day Program", 
    "enabled": true, 
    "time_of_day": "01:59:50", 
    "interval": {
        "type": "odd"
    }, 
    "station_duration": [
        {
            "stid": 1, 
            "duration": 5
        }, 
        {
            "stid": 2, 
            "duration": 5
        }, 
        {
            "stid": 3, 
            "duration": 5
        }, 
        {
            "stid": 4, 
            "duration": 5
        }, 
        {
            "stid": 5, 
            "duration": 5
        }, 
        {
            "stid": 6, 
            "duration": 5
        }, 
        {
            "stid": 7, 
            "duration": 5
        }, 
        {
            "stid": 8, 
            "duration": 5
        }
    ]
}
"""
long_day_dst_tester_program = """{
    "pid": 2, 
    "name": "Long Day Program", 
    "enabled": true, 
    "time_of_day": "01:59:50", 
    "interval": {
        "type": "odd"
    }, 
    "station_duration": [
        {
            "stid": 1, 
            "duration": 5
        }, 
        {
            "stid": 2, 
            "duration": 5
        }, 
        {
            "stid": 3, 
            "duration": 5
        }, 
        {
            "stid": 4, 
            "duration": 5
        }, 
        {
            "stid": 5, 
            "duration": 5
        }, 
        {
            "stid": 6, 
            "duration": 5
        }, 
        {
            "stid": 7, 
            "duration": 5
        }, 
        {
            "stid": 8, 
            "duration": 5
        }
    ]
}
"""

dst_programs = [short_day_dst_tester_program, long_day_dst_tester_program]