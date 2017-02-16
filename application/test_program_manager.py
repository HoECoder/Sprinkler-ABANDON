import unittest

#Python stdlib imports
import os
import os.path
import json
import pprint

#Sprinkler imports
from test_program_manager_sample_programs import *
from core_config import program_name_glob, program_name_template
from program_manager import program_manager

new_path = r"D:\controller\config\test_programs"

def masterSetup():
    program_manager.change_program_path(new_path)
    i = 0
    while i < len(simple_programs):
        program_name = program_name_template % (i+1)
        program_path = os.path.join(new_path, program_name)
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
        program_name = program_name_template % (i+1)
        program_path = os.path.join(new_path, program_name)
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
    
    return unittest.TestSuite([dict_suite])
