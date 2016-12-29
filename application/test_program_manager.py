import unittest

import os
import os.path

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

masterSetup()
        
class TestDictionaryInterface(unittest.TestCase):

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
        self.assertFalse(program_manager.has_key(3))
        
    def test_keys(self):
        keys = program_manager.keys()
        self.assertEquals(len(simple_programs),
                          len(keys),
                          "Not enough keys back")
        x = [x+1 for x in xrange(len(simple_programs))]
        self.assertSequenceEqual(x, keys, "Incorrect key ids")
        
    
dictionary_suite = unittest.TestLoader().loadTestsFromTestCase(TestDictionaryInterface)
