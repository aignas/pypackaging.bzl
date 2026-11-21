# Performance of the Starlark code

The versions, the specifiers and the markers are usually handled for every
requirement, for every target platform and for every Python version of a
project, so this code is executed many times in the loading and analysis
phases. This directory has the tools to ensure that it stays fast.

It is a separate Bazel module, because the tools need Python and the library
itself does not. Run the commands below in this directory.

The measured workloads are in `workloads.bzl`. The marker and version
workloads have the same names and inputs as the ones in `tests/perf` of
[rules_python](https://github.com/bazel-contrib/rules_python), where these
tools come from, so that the results can be compared.

## Counting the steps

Bazel cannot count how many steps the Starlark interpreter executes. However,
the `.bzl` files that only have pure functions are almost valid Python, so
`starlark_shim.py` executes them with CPython and counts the executed lines of
the `.bzl` files, which we call _steps_.

The number of steps does not depend on the machine and it changes when the
amount of work that the code does changes. It only slightly depends on the
Python version, hence the test below has a tolerance of 5%.

The shim is not a Starlark interpreter, it only supports what the measured
files need. If you start using something that is not supported, extend the
shim.

Print the number of steps that the workloads take:

```shell
bazel run //:benchmark
```

Only run the workloads that have `version` in the name:

```shell
bazel run //:benchmark -- version
```

The same works without Bazel, which is handy when iterating on the code:

```shell
python3 benchmark.py version
```

`//:steps_test` fails if the number of steps of a workload changes by more
than the tolerance. If the code got slower, then either fix the code or, if
the extra work is necessary, update the numbers in `steps_test.py`. If the
code got faster, then update the numbers, so that it stays that way. In both
cases update the results below.

## Measuring with Bazel

The steps are a proxy, so there is also a benchmark that measures the
workloads with Bazel itself:

```shell
bazel run //:bazel_benchmark
```

It builds `//:bazel_benchmark_analysis`, which executes the workload that is
selected with `--//:workload` for `--//:iterations` times during the analysis.
Starlark does not have a clock, so the time of a single iteration is the
difference of the wall time of 2 builds divided by the difference of the
iterations. This takes a long time and the results depend on the machine,
hence it is not a test.

If you run Bazel with startup options, pass the same ones to the benchmark,
otherwise the Bazel server restarts for every build:

```shell
bazel --host_jvm_args=-Xmx2g run //:bazel_benchmark -- \
    --bazel="bazel --host_jvm_args=-Xmx2g"
```

The same target can be used to profile the code with `--starlark_cpu_profile`,
see https://bazel.build/rules/performance#performance-profiling:

```shell
bazel build //:bazel_benchmark_analysis \
    --//:workload=evaluate_long \
    --//:iterations=10000 \
    --starlark_cpu_profile=/tmp/profile.gz
```

## Results

The time is of Bazel 8.5.0 on a laptop, only the ratios are meaningful.

| Workload                     | Steps | Bazel, µs |
| ---------------------------- | ----: | --------: |
| `evaluate_long`              |  2175 |     354.2 |
| `evaluate_long_parsed`       |   780 |     109.0 |
| `evaluate_string`            |   127 |      19.0 |
| `evaluate_two_strings`       |   262 |      39.7 |
| `evaluate_version`           |   239 |      40.8 |
| `evaluate_version_parsed`    |   128 |      20.3 |
| `parse_long`                 |  1396 |     205.9 |
| `requirement_parse`          |   401 |      63.6 |
| `specifier_set_contains`     |    66 |      10.3 |
| `specifier_set_parse`        |   146 |      23.6 |
| `tags_get_supported`         |  1227 |     160.9 |
| `version_is_compatible`      |    29 |       5.9 |
| `version_is_eq_prefix`       |    24 |       5.1 |
| `version_is_ge`              |    21 |       4.1 |
| `version_is_lt`              |    24 |       3.6 |
| `version_normalize`          |    46 |       8.4 |
| `version_parse_all_segments` |   201 |      38.7 |
| `version_parse_invalid`      |    20 |       4.2 |
| `version_parse_pre_release`  |    96 |      18.0 |
| `version_parse_release`      |    30 |       5.3 |
| `wheel_filename_parse`       |   190 |      36.8 |
