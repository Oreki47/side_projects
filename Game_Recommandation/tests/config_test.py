#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' a test module for config data module'

__author__ = 'Oreki47'

import unittest, os, sys
sys.path.insert(0, os.path.abspath('.'))

from core.utilities import ConfigData

class ConfigTest(unittest.TestCase):

    def test_init(self):
        config = ConfigData('./config.ini')
        self.assertEqual(config.test_string, 'Hello World!')

if __name__ == '__main__':
    unittest.main(exit=False)