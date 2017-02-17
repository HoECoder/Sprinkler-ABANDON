import unittest

#Python stdlib imports
import os
import os.path
import json
import pprint
import time
import hashlib

#Sprinkler imports
from test_program_manager_sample_programs import *
from core_config import program_name_glob, program_name_template
from program_manager import program_manager

new_path = r"D:\controller\config\test_programs"

def make_program_full_path(pid):
    program_name = program_name_template % (pid)
    program_path = os.path.join(new_path, program_name)
    return program_path

def masterSetup():
    program_manager.change_program_path(new_path)
    i = 0
    while i < len(simple_programs):
        program_path = make_program_full_path(i + 1)
        if os.path.exists(program_path):
            os.remove(program_path)
        f = open(program_path, "wb")
        f.write(simple_programs[i])
        f.flush()
        f.close()
        del f
        i += 1
    program_manager.load_programs()
    
def masterTearDown():
    i = 0
    while i < len(simple_programs):
        program_path = make_program_full_path(i + 1)
        if os.path.exists(program_path):
            os.remove(program_path)
        i += 1

def setUpModule():
    masterSetup()
    
def tearDownModule():
    masterTearDown()
        
class TestProgramManagerDictionaryInterface(unittest.TestCase):

    def test_len(self):
        self.assertEqual(len(simple_programs), 
                         len(program_manager),
                         "Incorrect length, expecting %d" % len(simple_programs))
    def test_items(self):
        items = program_manager.items()
        self.assertEqual(len(simple_programs),
                         len(items),
                         "Incorrect number of item, expecting %d" % len(simple_programs))
    def test_has_key(self):
        self.assertTrue(program_manager.has_key(1))
        self.assertTrue(program_manager.has_key(2))
    
    def test_has_no_key(self):
        key = len(simple_programs) + 1
        self.assertFalse(program_manager.has_key(key))
        
    def test_keys(self):
        keys = program_manager.keys()
        self.assertEquals(len(simple_programs),
                          len(keys),
                          "Not enough keys back")
        x = [x + 1 for x in xrange(len(simple_programs))]
        self.assertSequenceEqual(x, keys, "Incorrect key ids")
    def test_roundtrip_items(self):
        i = 0
        while i < len(simple_programs):
            program = program_manager[i+1]
            od = program.serialize()
            serialized_program = json.dumps(od , indent = 4)
            # print len(serialized_program), len(simple_programs[i])
            # pprint.pprint(serialized_program)
            # print '------'
            # pprint.pprint(simple_programs[i])
            self.assertEquals(serialized_program,
                              simple_programs[i])
            i += 1
    def test_raise_key_error(self):
        with self.assertRaises(KeyError):
            program = program_manager[4]
        
class TestDirtyBit(unittest.TestCase):
    def test_station_block_dirty(self):
        for program in program_manager.values():
            for sb in program.values():
                sb.dirty = True
                self.assertTrue(sb.dirty,
                                "Station Block Dirty Bit Not Set: %d" % sb.station_id)
                self.assertTrue(program.dirty,
                                "Program Dirty Bit Not Set:  %d" % program.program_id)
                self.assertTrue(program_manager.dirty,
                                "ProgramManager Dirty Bit Not Set")
                sb.dirty = False
                self.assertFalse(sb.dirty,
                                "Station Block Dirty Bit Not UnSet: %d" % sb.station_id)
                self.assertFalse(program.dirty,
                                "Program Dirty Bit Not UnSet:  %d" % program.program_id)
                self.assertFalse(program_manager.dirty,
                                "ProgramManager Dirty Bit Not UnSet")
    def test_station_block_dirty2(self):
        for program in program_manager.values():
            for sb in program.values():
                sb.duration = sb.duration
                self.assertFalse(sb.dirty, "Duration Unchanged, Station Should Not be Dirty: %d" % sb.station_id)
            self.assertFalse(program.dirty, "Durations Unchanged, Program Should Not Be Dirty: %d" % program.program_id)
        self.assertFalse(program_manager.dirty, "Durations Unchanged, ProgramManager Should Not Be Dirty")
        for program in program_manager.values():
            for sb in program.values():
                sb.duration = sb.duration * 2
                self.assertTrue(sb.dirty, "Duration Changed, Station Should Be Dirty: %d" % sb.station_id)
            self.assertTrue(program.dirty, "Durations Changed, Program Should Be Dirty: %d" % program.program_id)
        self.assertTrue(program_manager.dirty, "Durations Changed, ProgramManager Should Be Dirty")
        
    def test_program_dirty(self):
        for program in program_manager.values():
            program.dirty = True
            for sb in program.values():
                self.assertFalse(sb.dirty,
                                 "Station Block Should Not Be Dirty: %d, %d" % (sb.station_id, program.program_id))
            self.assertTrue(program.dirty,
                            "Program Dirty Bit Not Set:  %d" % program.program_id)
            self.assertTrue(program_manager.dirty,
                            "ProgramManager Dirty Bit Not Set")
            program.dirty = False
            for sb in program.values():
                self.assertFalse(sb.dirty,
                                 "Station Block Should Not Be Dirty: %d, %d" % (sb.station_id, program.program_id))
            self.assertFalse(program.dirty,
                            "Program Dirty Bit Not UnSet:  %d" % program.program_id)
            self.assertFalse(program_manager.dirty,
                            "ProgramManager Dirty Bit Not UnSet")
    def test_program_disabled_dirty(self):
        for program in program_manager.values():
            program.enabled = False
            for sb in program.values():
                self.assertFalse(sb.dirty,
                                 "Station Block Should Not Be Dirty: %d, %d" % (sb.station_id, program.program_id))
            self.assertTrue(program.dirty,
                            "Program Disabled, Dirty Bit Not Set:  %d" % program.program_id)
            self.assertTrue(program_manager.dirty,
                            "ProgramManager Dirty Bit Not Set. Program is Dirty: %d" % program.program_id)
            program.enabled = True
            for sb in program.values():
                self.assertFalse(sb.dirty,
                                 "Station Block Should Not Be Dirty: %d, %d" % (sb.station_id, program.program_id))
            self.assertTrue(program.dirty,
                            "Program Enabled, Dirty Bit Not Set:  %d" % program.program_id)
            self.assertTrue(program_manager.dirty,
                            "ProgramManager Dirty Bit Not Set. Program is Dirty: %d" % program.program_id)
            program.dirty = False
            for sb in program.values():
                self.assertFalse(sb.dirty,
                                 "Station Block Should Not Be Dirty: %d, %d" % (sb.station_id, program.program_id))
            self.assertFalse(program.dirty,
                            "Program Enabled, Dirty Bit Not UnSet:  %d" % program.program_id)
            self.assertFalse(program_manager.dirty,
                            "ProgramManager Dirty Bit Not UnSet. Program is Not Dirty: %d" % program.program_id)


class TestProgramManagerWrites(unittest.TestCase):
    def setUp(self):
        pre_stats, path_names, digests = self.gather_stats()
        self.pre_stats = pre_stats
        self.path_names = path_names
        self.pre_digests = digests
        #time.sleep(0.125)
    
    def gather_stats(self):
        stats = list()
        path_names = list()
        digests = list()
        i = 0
        while i < len(simple_programs):
            path_name = make_program_full_path(i + 1)
            path_names.append(path_name)
            stat = os.stat(path_name)
            stats.append(stat)
            digest = self.hash_file(path_name)
            digests.append(digest)
            i += 1
        return stats, path_names, digests
    def hash_file(self, path_name):
        h = hashlib.sha256()
        f = open(path_name)
        for line in f:
            h.update(line)
        f.close()
        return h.hexdigest()
        
    def __check_same_size_same_content(self):
        post_stats, path_names, digests = self.gather_stats()
        stats = zip(self.pre_stats, post_stats, self.path_names, self.pre_digests, digests)
        for pre_stat, post_stat, path_name, pre_digest, digest in stats:
            self.assertEqual(pre_stat.st_size,
                             post_stat.st_size,
                             "File Size Changed on Program: %s" % path_name)
            self.assertEqual(pre_digest, 
                             digest,
                             "Unequal Hash Digests %s" % path_name)
                             
    def __check_same_size_different_content(self):
        post_stats, path_names, digests = self.gather_stats()
        stats = zip(self.pre_stats, post_stats, self.path_names, self.pre_digests, digests)
        for pre_stat, post_stat, path_name, pre_digest, digest in stats:
            self.assertEqual(pre_stat.st_size,
                             post_stat.st_size,
                             "File Size Changed on Program: %s" % path_name)
            self.assertNotEqual(pre_digest, 
                                digest,
                                "Equal Hash Digests %s" % path_name)
    def __check_different_size_different_content(self):
        post_stats, path_names, digests = self.gather_stats()
        stats = zip(self.pre_stats, post_stats, self.path_names, self.pre_digests, digests)
        for pre_stat, post_stat, path_name, pre_digest, digest in stats:
            self.assertNotEqual(pre_stat.st_size,
                                post_stat.st_size,
                                "File Size Changed on Program: %s" % path_name)
            self.assertNotEqual(pre_digest, 
                                digest,
                                "Equal Hash Digests %s" % path_name)
    
    def __check_only_different_content(self):
        post_stats, path_names, digests = self.gather_stats()
        stats = zip(self.pre_stats, post_stats, self.path_names, self.pre_digests, digests)
        for pre_stat, post_stat, path_name, pre_digest, digest in stats:
            self.assertNotEqual(pre_digest, 
                                digest,
                                "Equal Hash Digests %s" % path_name)
    
    def test_write_with_no_dirty_programs(self):
        self.setUp()
        program_manager.write_programs()
        self.__check_same_size_same_content()
        
    def test_write_with_simple_dirty(self):
        self.setUp()
        for program in program_manager.values():
            program.dirty = True
        program_manager.write_programs()
        self.__check_same_size_same_content()

    def test_write_with_enable_change(self):
        self.setUp()
        for program in program_manager.values():
            program.enabled = False
        program_manager.write_programs()
        self.__check_different_size_different_content()
        
    def test_with_time_of_day_change(self):
        self.setUp()
        for program in program_manager.values():
            program.time_of_day = 500
        program_manager.write_programs()
        self.__check_same_size_different_content() # Time should always be formatted the same length
        
    def test_duration_changes(self):
        self.setUp()
        for program in program_manager.values():
            for sb in program.values():
                sb.duration = 10
                self.assertTrue(sb.dirty,
                                "Station Block Should Be Dirty: %d, %d" % (sb.station_id, program.program_id))
                self.assertTrue(program.dirty,
                                "Program Should Be Dirty: %d, %d" % (sb.station_id, program.program_id))
            self.assertTrue(program.dirty,
                            "Program Should Be Dirty: %d" % program.program_id)
        program_manager.write_programs()
        self.__check_only_different_content()

def load_tests(loader, tests, pattern):
    
    dict_suite = unittest.TestSuite()
    dict_suite.addTest(TestProgramManagerDictionaryInterface('test_len'))
    dict_suite.addTest(TestProgramManagerDictionaryInterface('test_items'))
    dict_suite.addTest(TestProgramManagerDictionaryInterface('test_has_key'))
    dict_suite.addTest(TestProgramManagerDictionaryInterface('test_has_no_key'))
    dict_suite.addTest(TestProgramManagerDictionaryInterface('test_keys'))
    dict_suite.addTest(TestProgramManagerDictionaryInterface('test_roundtrip_items'))
    dict_suite.addTest(TestProgramManagerDictionaryInterface('test_raise_key_error'))
    dict_suite.addTest(TestDirtyBit('test_station_block_dirty'))
    dict_suite.addTest(TestDirtyBit('test_program_dirty'))
    dict_suite.addTest(TestDirtyBit('test_program_disabled_dirty'))
    dict_suite.addTest(TestProgramManagerWrites('test_write_with_no_dirty_programs'))
    dict_suite.addTest(TestProgramManagerWrites('test_write_with_simple_dirty'))
    dict_suite.addTest(TestProgramManagerWrites('test_write_with_enable_change'))
    dict_suite.addTest(TestProgramManagerWrites('test_with_time_of_day_change'))
    dict_suite.addTest(TestProgramManagerWrites('test_duration_changes'))
    
    return unittest.TestSuite([dict_suite])
