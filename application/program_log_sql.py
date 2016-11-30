program_log_sql = """create table if not exists interval_types (id integer not null,
                                           type_name text not null unique on conflict ignore,
                                           primary key (id,type_name) on conflict ignore);

create table if not exists events (event_id integer not null,
                                   event_text text not null,
                                   primary key (event_id, event_text) on conflict ignore);

create table if not exists programs (program_id integer primary key,
                                     name text,
                                     interval_type integer not null,
                                     time_of_day text not null);

create table if not exists stations (station_id integer not null,
                                     station_name text not null unique,
                                     primary key (station_id, station_name));

create table if not exists program_stations (program_id integer not null,
                                             station_id integer not null,
                                             duration integer not null,
                                             primary key (program_id, station_id) on conflict ignore);

create table if not exists program_log (time_index real not null,
                                        program_id integer not null,
                                        event_id integer not null,
                                        primary key (time_index, program_id, event_id));

create table if not exists station_log (time_index real not null,
                                        station_id integer not null,
                                        event_id integer not null,
                                        primary key (time_index, station_id, event_id));

insert into events (event_id, event_text) values (1,"start"),(2,"stop");
insert into interval_types (id, type_name) values (1, "even"), (2, "odd"), (3, "dow");
"""
sql_interval_map = {EVEN_INTERVAL_TYPE : 1,
                    ODD_INTERVAL_TYPE : 2,
                    DOW_INTERVAL_TYPE : 3}

sql_event_map = {"start" : 1,
                 "stop" : 2}