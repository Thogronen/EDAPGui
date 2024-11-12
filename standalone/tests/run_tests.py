import unittest
import time
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

# Add tests directory to path
tests_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, tests_dir)

# Import test classes from their respective modules
from tests.test_gui import TestKeyboardGUI
from tests.test_logging import TestConsoleLogging
from tests.test_plugins import TestPluginSystem
# import any other tests you want here :)

# Ensure we're using the parent directory's plugins folder
os.environ['PLUGIN_DIR'] = os.path.join(parent_dir, 'plugins')


def run_tests():
    """Run all tests with detailed output"""
    # Create test suite
    suite = unittest.TestSuite()

    test_classes = [TestKeyboardGUI, TestConsoleLogging, TestPluginSystem]

    print("\nStarting Test Suite:")
    print("=" * 70)
    print(f"Using plugin directory: {os.environ['PLUGIN_DIR']}")

    total_start = time.time()

    for test_class in test_classes:
        class_start = time.time()
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        print(f"\n{test_class.__name__}:")
        print("-" * 50)
        print(f"Description: {test_class.__doc__}")
        print(f"Number of tests: {tests.countTestCases()}")
        print("Tests:")

        for test in tests:
            test_start = time.time()
            test_name = test._testMethodName
            test_doc = getattr(test, test_name).__doc__ or "No description"
            print(f"\n  • {test_name}")
            print(f"    {test_doc}")
            suite.addTest(test)
            test_time = time.time() - test_start
            print(f"    Time: {test_time:.3f}s")

        class_time = time.time() - class_start
        print(f"\nClass total time: {class_time:.3f}s")

    # Run tests
    print("\nRunning all tests:")
    print("=" * 70)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    total_time = time.time() - total_start
    print("\nTest Summary:")
    print("=" * 70)
    print(f"Total tests run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Total time: {total_time:.3f}s")

    if result.failures:
        print("\nFailures:")
        print("=" * 70)
        for i, failure in enumerate(result.failures, 1):
            print(f"\nFailure {i}:")
            print(f"Test: {failure[0]}")
            print(f"Error: {failure[1]}")

    if result.errors:
        print("\nErrors:")
        print("=" * 70)
        for i, error in enumerate(result.errors, 1):
            print(f"\nError {i}:")
            print(f"Test: {error[0]}")
            print(f"Error: {error[1]}")

    return result.wasSuccessful()


if __name__ == '__main__':
    run_tests()