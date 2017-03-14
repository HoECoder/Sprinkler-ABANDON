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

short_day_dst_tester_program = {u'enabled': True,
                                u'interval': {u'type': u'odd'},
                                u'name': u'DST Day Program',
                                u'pid': -1,
                                u'station_duration': [{u'duration': 5, u'stid': 1},
                                                      {u'duration': 5, u'stid': 2},
                                                      {u'duration': 5, u'stid': 3},
                                                      {u'duration': 5, u'stid': 4},
                                                      {u'duration': 5, u'stid': 5},
                                                      {u'duration': 5, u'stid': 6},
                                                      {u'duration': 5, u'stid': 7},
                                                      {u'duration': 5, u'stid': 8}],
                                u'time_of_day': u'01:59:50'}

dst_program = short_day_dst_tester_program