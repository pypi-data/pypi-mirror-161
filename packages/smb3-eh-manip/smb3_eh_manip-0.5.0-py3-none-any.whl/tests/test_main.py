import unittest
from smb3_eh_manip import main


class TestMain(unittest.TestCase):
    def test_initialize_logging(self):
        main.initialize_logging()  # :\ i know
