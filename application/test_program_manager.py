import unittest

from program_manager import program_manager

new_path = r"D:\controller\config\test_programs"

class TestDictionaryInterface(unittest.TestCase):
    def setUp(self):
        program_manager.change_program_path(new_path)
