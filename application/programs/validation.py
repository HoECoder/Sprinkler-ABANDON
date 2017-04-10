import cerberus

from settings_keys import *

even_odd_intervals = [EVEN_INTERVAL_TYPE,
                      ODD_INTERVAL_TYPE]

DOW_INTERVAL_ERROR_NO_LIST_STR = "Day of Week Interval must contain a list of days"
DOW_INTERVAL_ERROR_BAD_LIST_STR = "Day of Week Interval must have a list of days Sun - Sat"
INTERVAL_TYPE_ERROR_STR = "Interval type must be 'even','odd','day_of_week'"

def validate_interval(field, value, error):
    typ = value[INTERVAL_TYPE_KEY]
    if typ == DOW_INTERVAL_TYPE:
        days = value.get(RUN_DAYS_KEY, None)
        if days is None:
            error(field, DOW_INTERVAL_ERROR_NO_LIST_STR)
        ma = max(days)
        mi = min(days)
        if mi < 0 or ma > 6:
            error(field, DOW_INTERVAL_ERROR_BAD_LIST_STR)
    elif not typ in even_odd_intervals:
        error(field, INTERVAL_TYPE_ERROR_STR)


station_block_schema = {STATION_ID_KEY : {"type" : "integer",
                                          "min" : 0},
                        DURATION_KEY : {"type" : "integer",
                                        "min" : 0}}
program_schema = {PROGRAM_ID_KEY : {"type" : "integer",
                                    "min" : 0},
                  TIME_OF_DAY_KEY : {"type" : "string"},
                  INTERVAL_KEY : {"type":"dict",
                                  "validator":validate_interval},
                  PROGRAM_NAME_KEY: {"type" : "string"},
                  STATION_DURATION_KEY : {"type" : "list",
                                          "schema" : {"type" : "dict",
                                                      "schema" : station_block_schema}}}

program_validator = cerberus.Validator(program_schema,allow_unknown = True)