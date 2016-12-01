from settings_keys import EVEN_INTERVAL_TYPE, ODD_INTERVAL_TYPE, DOW_INTERVAL_TYPE

program_log_sql = """create table if not exists interval_types (id integer not null,
                                           type_name text not null unique on conflict ignore,
                                           primary key (id,type_name) on conflict ignore);

create table if not exists events (event_id integer not null,
                                   event_text text not null,
                                   primary key (event_id, event_text) on conflict ignore);

create table if not exists programs (program_id integer primary key on conflict ignore,
                                     name text,
                                     interval_type integer not null,
                                     time_of_day text not null);

create table if not exists stations (station_id integer not null,
                                     station_name text not null unique,
                                     primary key (station_id, station_name) on conflict ignore);

create table if not exists program_stations (program_id integer not null,
                                             station_id integer not null,
                                             duration integer not null,
                                             primary key (program_id, station_id) on conflict ignore);

create table if not exists program_log (time_index real not null,
                                        program_id integer not null,
                                        event_id integer not null,
                                        primary key (time_index, program_id, event_id) on conflict ignore);

create table if not exists station_log (time_index real not null,
                                        station_id integer not null,
                                        event_id integer not null,
                                        primary key (time_index, station_id, event_id) on conflict ignore);

create view if not exists program_view as
select p.program_id, p.name,i.type_name as interval_type, p.time_of_day, sum(r.duration) as duration
from programs as p, interval_types as i, program_stations as r
where p.interval_type = i.id and r.program_id = p.program_id group by p.program_id;

create view if not exists program_log_view as
select p.name, l.time_index, datetime(l.time_index,'unixepoch') as unix_time, e.event_text as event
from programs as p, program_log as l, events as e
where l.program_id = p.program_id and l.event_id = e.event_id;

create view if not exists station_log_view as
select s.station_name, l.time_index, datetime(l.time_index,'unixepoch') as unix_time, e.event_text as event
from stations as s, station_log as l, events as e
where l.station_id = s.station_id and l.event_id = e.event_id;

create view if not exists program_stations_view as
select p.name, s.station_name, l.duration
from programs as p, stations as s, program_stations as l
where p.program_id = l.program_id and s.station_id = l.station_id;
"""

event_type_insert = "insert into events (event_id, event_text) values (?, ?)"
interval_type_insert = "insert into interval_types (id, type_name) values (?, ?)"

program_insert_string = "insert into programs (program_id, name, interval_type, time_of_day) values (?, ?, ?, ?)"
station_insert_string = "insert into stations (station_id, station_name) values (?, ?)"
program_stations_insert = "insert into program_stations (program_id, station_id, duration) values (?, ?, ?)"
program_event_insert = "insert into program_log (time_index, program_id, event_id) values (?, ?, ?)"
station_event_insert = "insert into station_log (time_index, station_id, event_id) values (?, ?, ?)"

sql_interval_map = {EVEN_INTERVAL_TYPE : 1,
                    ODD_INTERVAL_TYPE : 2,
                    DOW_INTERVAL_TYPE : 3}
sql_event_start = "start"
sql_event_stop = "stop"
sql_event_map = {sql_event_start : 1,
                 sql_event_stop : 2}