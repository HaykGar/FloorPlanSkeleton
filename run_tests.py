"""Run every automated test and print the results.

    python run_tests.py

A test is any function in the tests folder whose name starts with "test_".
A test passes when it finishes without an AssertionError.
"""

import os
import sys
import traceback
from collections.abc import Callable
from types import ModuleType


PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
TESTS_FOLDER = os.path.join(PROJECT_FOLDER, "tests")

# Let the test files import room.py, rules.py, and so on.
sys.path.insert(0, PROJECT_FOLDER)
sys.path.insert(0, TESTS_FOLDER)

TEST_MODULE_NAMES = [
    "test_room",
    "test_floor_plan",
    "test_rules",
    "test_storage",
]


def collect_tests(module: ModuleType) -> list[tuple[str, Callable[[], None]]]:
    """Return every test function inside one test module, in file order."""
    functions = []
    for name in dir(module):
        if name.startswith("test_"):
            functions.append((name, getattr(module, name)))
    return functions


def run_module(module_name: str) -> tuple[int, int]:
    """Run one test module and return (passed, failed)."""
    module = __import__(module_name)
    print("\n" + module_name)

    passed = 0
    failed = 0
    for name, test_function in collect_tests(module):
        try:
            test_function()
        except AssertionError as error:
            failed += 1
            print("  FAIL  " + name)
            if str(error):
                print("        " + str(error))
        except Exception:
            failed += 1
            print("  ERROR " + name)
            for line in traceback.format_exc().splitlines()[-3:]:
                print("        " + line)
        else:
            passed += 1
            print("  pass  " + name)
    return passed, failed


def main() -> int:
    total_passed = 0
    total_failed = 0
    for module_name in TEST_MODULE_NAMES:
        passed, failed = run_module(module_name)
        total_passed += passed
        total_failed += failed

    print("\n" + "-" * 40)
    print("{} passed, {} failed".format(total_passed, total_failed))
    return 1 if total_failed else 0


if __name__ == "__main__":
    sys.exit(main())
