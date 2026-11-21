# Conformance with pypa/packaging

The behaviour of this library is expected to be the same as of the
[packaging](https://github.com/pypa/packaging) release that is mentioned in the
`README.md` of the repository. To ensure that, the test cases in
`pypackaging/tests/packaging_cases` are generated with `generate.py`:

- The inputs are harvested from the test-suite of `packaging` and there are
  also tables that have all of the combinations of the interesting inputs,
  e.g. every version comparison operator for a list of versions.
- The expected values are computed by `packaging` itself. For
  `tags.get_supported` the `get_supported` function of `pip` is emulated on top
  of it and the manylinux and musllinux platforms are expanded like
  `packaging` does on a host that has that libc version.

The cases are used by `pypackaging/tests/test_packaging_conformance.bzl`.

It is a separate Bazel module, because the generator needs Python and
`packaging` and the library itself does not. Run the commands below in this
directory.

Regenerate the test cases:

```shell
bazel run //:update
```

`//:up_to_date_test` fails if the checked-in test cases are not what the
generator would write.

## Upgrading packaging

1. Change the version, the URL and the checksum of the `packaging` sdist in
   `MODULE.bazel`.
2. Regenerate the test cases.
3. Run `bazel test //...` in the root of the repository and fix the library
   until the tests pass. The diff of the generated files and the changelog of
   `packaging` show what has changed.

## Notes

- This was ported from `tests/support/pypa_packaging` of
  [rules_python](https://github.com/bazel-contrib/rules_python).
- The cases where `packaging` raises an exception are generated, but only the
  ones in the lists of the invalid inputs are tested, because Starlark code
  cannot catch a failure and each of them needs a separate target.
