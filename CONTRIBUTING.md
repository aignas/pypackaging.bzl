# Contributing

## Development

- Bazel is pinned in `.bazelversion` (also in `conformance/`, `docs/`,
  `e2e/smoke/`, `e2e/workspace/` and `perf/`);
  use [Bazelisk](https://github.com/bazelbuild/bazelisk).
- Unit tests: `bazel test //...` in the repository root.
- Smoke test of the public API (also run by BCR presubmit):
  `cd e2e/smoke && bazel test //...`.
- The same smoke test with a `WORKSPACE.bazel` file instead of Bzlmod:
  `cd e2e/workspace && bazel test //...`. It cannot run with Bazel 9,
  which removed WORKSPACE.
- Conformance: the test cases in `pypackaging/tests/packaging_cases` are
  generated from the test-suite of `packaging`, with `packaging` computing the
  expected values. Regenerate them with `cd conformance && bazel run //:update`
  and verify with `cd conformance && bazel test //...`, see
  [conformance/README.md](conformance/README.md).
- Performance: `cd perf && bazel test //...` fails if the amount of work that
  the Starlark code does for the measured workloads changes, see
  [perf/README.md](perf/README.md) for how to measure and update the numbers.
- API docs: `docs/pypackaging.md` is generated from docstrings. After
  changing a public docstring, run `cd docs && bazel run //:update` and
  verify with `cd docs && bazel test //...`.
- Formatting and lint: run `pre-commit run --all-files` before sending a
  change (or install the git hook with `pre-commit install`).
- To test against another Bazel version, set `USE_BAZEL_VERSION` (e.g.
  `USE_BAZEL_VERSION=9.x`) and pass `--lockfile_mode=off`. On Bazel 7, pass
  `--ignore_all_rc_files` (`bazel --ignore_all_rc_files test //...`) because
  `tools/preset.bazelrc` targets Bazel 8+.
