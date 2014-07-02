#!/usr/bin/env python

import unittest
from mock import Mock, MagicMock
from test_encode import EncodeTestCase
from test_query import QueryTestCase


if __name__ == '__main__':
  suite1 = unittest.TestLoader().loadTestsFromTestCase(EncodeTestCase)
  suite2 = unittest.TestLoader().loadTestsFromTestCase(QueryTestCase)
  allTests = unittest.TestSuite([suite1, suite2])
  unittest.TextTestRunner(verbosity=2).run(allTests)
