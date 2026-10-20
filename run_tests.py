#!/usr/bin/env python3
"""
Unified test runner for udi-yolink unittest suite.
Discovers and executes all test suites (test_*.py) with detailed reporting.
"""

import os
import sys
import unittest
import time

def main():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(repo_dir)

    print("=" * 70)
    print("UDI-YOLINK UNITTEST SUITE")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=repo_dir, pattern='test_*.py')

    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print(f"Tests run:     {result.testsRun}")
    print(f"Failures:      {len(result.failures)}")
    print(f"Errors:        {len(result.errors)}")
    print(f"Skipped:       {len(result.skipped)}")
    print(f"Time elapsed:  {elapsed:.3f}s")
    print("=" * 70)

    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        return 0
    else:
        print("❌ TESTS FAILED!")
        return 1

if __name__ == '__main__':
    sys.exit(main())

