#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_iris_validator
----------------------------------

Tests for `test_iris_validator` module.
"""

import glob
import os
import sys
import unittest

import iris_validator
from iris_validator import installation_dir
from iris_validator.cmdline import process_cmd_line
from iris_validator.iris_validate import stationxml_passes_rule, stationxml_validator
from iris_validator.iris_rules import error_codes, restrictions, test_xmls

import logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

class TestIris_validator(unittest.TestCase):

    def setUp(self):

        self.install_dir = installation_dir()
        self.assertEqual(os.path.isdir(self.install_dir), 1)
        self.resource_dir = os.path.join(self.install_dir, 'iris_resources')
        self.assertEqual(os.path.isdir(self.resource_dir), 1)

    def test_version(self):
        assert(iris_validator.__version__)

    def test_process_command_line(self):
        ex = os.path.join('/Users/mth/mth/miniconda3/envs/yas/bin/', 'iris-validator')
        xmlfile = os.path.join(self.resource_dir, 'F1_110.xml')
        sys.argv = [ex, '--infile=%s' % xmlfile]
        args = process_cmd_line('iris-validator')
        self.assertEqual(args.infile, xmlfile)
        pass

    def test_validate_rule(self):
        xmlfile = os.path.join(self.resource_dir, 'F1_110.xml')
        code = '110'
        xmlfile = os.path.join(self.resource_dir, 'F1_423.xml')
        code = '423'
        passed, errors = stationxml_passes_rule(xmlfile, code)
        self.assertEqual(passed, False)
        pass

    def test_validate_iris_stationxml_examples_vs_rules(self):
        '''
        Loop through IRIS validation stationxmlfile examples (e.g., 'F1_304.xml')
            Test to see that file F?_XXX.xml correctly FAILS rule_code=XXX
            -or-
            Test to see that file P?_XXX.xml correctly PASSES rule_code=XXX
        '''
        for rule in error_codes.keys():
            files = test_xmls[rule]

            for fname in files:
                xmlfile = os.path.join(self.resource_dir, fname)
                #code = fname[3:6]
                code = rule

                #print("Check file:%s against Rule:%s xmlfile=%s" % (fname, code, xmlfile))
                if not os.path.isfile(xmlfile):
                    print("******* Error: Can't find file:%s" % fname)
                    continue

                passed, errors = stationxml_passes_rule(xmlfile, code)

                if fname[0:1] == 'P':
                    self.assertEqual(passed, True)
                    if not passed:
                        print("Error fname=%s should have failed" % fname)
                elif fname[0:1] == 'F':
                    if passed:
                        print("Error fname=%s should have failed" % fname)
                    self.assertEqual(passed, False)
        pass

    def test_validate_Validator_Pass(self):
        xmlfile = os.path.join(self.resource_dir, 'Validator_Pass.xml')
        validator = stationxml_validator(xmlfile)
        validator.validate_inventory()
        self.assertEqual(len(validator.errors), 0)
        pass


    '''
    def tearDown(self):
        files = glob.glob('?.xml')
        for f in files:
            os.remove(f)
    '''

if __name__ == "__main__":
    unittest.main()
