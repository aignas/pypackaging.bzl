"""Tests that the Starlark code does not get slower without us noticing."""

import unittest

import starlark_shim
from workloads import workloads

# The number of steps that each workload takes, see the README.md. Update the
# numbers with the output of `bazel run //:benchmark`.
_STEPS = {
    # keep sorted
    "evaluate_long": 2588,
    "evaluate_long_parsed": 817,
    "evaluate_string": 191,
    "evaluate_two_strings": 380,
    "evaluate_version": 292,
    "evaluate_version_parsed": 152,
    "parse_long": 1772,
    "requirement_parse": 591,
    "specifier_set_contains": 64,
    "specifier_set_parse": 155,
    "tags_get_supported": 2602,
    "version_is_compatible": 30,
    "version_is_eq_prefix": 24,
    "version_is_ge": 22,
    "version_is_lt": 24,
    "version_normalize": 48,
    "version_parse_all_segments": 173,
    "version_parse_invalid": 16,
    "version_parse_pre_release": 124,
    "version_parse_release": 35,
    "wheel_filename_parse": 197,
}

# The number of the steps slightly depends on the Python version.
_TOLERANCE = 0.05


class StepsTest(unittest.TestCase):
    def test_all_workloads_are_measured(self):
        self.assertEqual(sorted(_STEPS), sorted(workloads()))

    def test_steps(self):
        for name, fn in workloads().items():
            with self.subTest(name):
                want = _STEPS[name]
                self.assertAlmostEqual(
                    starlark_shim.count_steps(fn),
                    want,
                    delta=want * _TOLERANCE,
                    msg="The number of steps has changed, see perf/README.md",
                )


if __name__ == "__main__":
    unittest.main()
