# -*- coding: utf-8 -*-
import sys
import unittest

class Runner:
    def __init__(self,test_cases):
        self.suite = unittest.TestSuite()
        for case in test_cases:
            tests = unittest.TestLoader().loadTestsFromTestCase(case)
            self.suite.addTests(tests)

    def add_tests(self, case):
        tests = unittest.TestLoader().loadTestsFromTestCase(case)
        self.suite.addTest(tests)
        
    def run(self):
        res = unittest.TextTestRunner(verbosity=3).run(self.suite)
        if len(res.errors) >= 1 or len(res.failures) >= 1:
            sys.exit(-1)
        else:
            sys.exit(0)