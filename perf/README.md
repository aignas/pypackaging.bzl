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
| `evaluate_long`              |  2588 |     560.9 |
| `evaluate_long_parsed`       |   817 |     151.1 |
| `evaluate_string`            |   191 |      39.5 |
| `evaluate_two_strings`       |   380 |      74.6 |
| `evaluate_version`           |   292 |      67.9 |
| `evaluate_version_parsed`    |   152 |      34.0 |
| `parse_long`                 |  1772 |     351.9 |
| `requirement_parse`          |   591 |      95.3 |
| `specifier_set_contains`     |    64 |      24.1 |
| `specifier_set_parse`        |   155 |      82.8 |
| `tags_get_supported`         |  2602 |     680.3 |
| `version_is_compatible`      |    30 |       6.0 |
| `version_is_eq_prefix`       |    24 |       5.2 |
| `version_is_ge`              |    22 |       3.9 |
| `version_is_lt`              |    24 |       3.7 |
| `version_normalize`          |    48 |      10.2 |
| `version_parse_all_segments` |   173 |      38.8 |
| `version_parse_invalid`      |    16 |       4.0 |
| `version_parse_pre_release`  |   124 |      25.7 |
| `version_parse_release`      |    35 |       7.5 |
| `wheel_filename_parse`       |   197 |      41.2 |
