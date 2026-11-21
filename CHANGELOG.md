# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
While the version is 0.x, breaking changes are released as minor versions.

## [Unreleased]

Aligns the library with `packaging` 26.3.

### Breaking changes

These follow the behaviour changes of `packaging` 26.3:

- `tags.get_supported` puts the native `linux_<arch>` tags before the
  `manylinux` and `musllinux` tags, they used to be after them. A wheel that
  is built for `linux_x86_64` is now preferred over a `manylinux` wheel by
  `tags.select_compatible`.
- `tags.get_supported` uses the `fat3` macOS binary format, `fat32` was a typo.
- `tags.get_supported` checks if the first ABI is a free-threaded one before
  it removes `abi3` and `none`, so `abis = ["abi3", "cp313t"]` no longer yields
  the `abi3t` tags, and an explicit `abi3t` no longer results in duplicate
  tags.
- `tags.parse_tag` fails for a tag with an empty component or an empty member
  of a compressed tag set (e.g. `py3--any`), and for an interpreter that is not
  an identifier (e.g. `2.7.6-none-any`).
- `utils.parse_wheel_filename` fails for the same tags and for an empty
  project name, and `utils.parse_sdist_filename` fails for an empty project
  name.
- `markers.parse` and `requirements.parse` fail if there is a trailing line
  break. The trailing spaces and tabs are still accepted.
- `markers.parse` normalizes the value that is tested for the membership in
  `extras` or `dependency_groups` (e.g. `"Foo_Bar" in extras`), and it no
  longer turns a variable that is compared with `extra` into a string (e.g.
  `extra == os_name`).
- `markers.to_string` uses single quotes for the values that have a double
  quote, so that the result can be parsed back, and fails for the values that
  have both of the quote characters.

### Added

- WORKSPACE is supported again with Bazel 7 and 8: define the repository with
  the name `pypackaging.bzl`, see the README. `e2e/workspace` tests it.
- `tags.parse_tag` has the `limit` argument, the maximum number of the tags
  that a compressed tag set may generate.

### Changed

- The error messages follow `packaging` 26.3: `Invalid quoted string` for
  malformed marker string literals, a specific message for a `.*` suffix
  after a pre-release, post-release, dev or local version in a requirement,
  and `Invalid requirement` for the requirements with an invalid specifier.
- `utils.is_normalized_name` behaves the same as in `packaging` now, which no
  longer accepts names like `a--b`.
- The `~=` operator behaves the same as in `packaging` now, which gets the
  prefix from the normalized version too (e.g. `~=1.0c1` and `~=v1.0`).
- The version ranges that were added in `packaging` 26.3 (`packaging.ranges`,
  `SpecifierSet.to_range`, `is_subset`, `is_superset` and `is_disjoint`) and
  `tags.pure_python_tags` are not ported.

### Internal

- The tests include the cases that are generated from the test-suite of
  `packaging`, with the expected values computed by `packaging` itself, see
  `conformance/README.md`.
- `perf/` has the tools to count the steps that the Starlark code executes and
  to benchmark it with Bazel.

## [0.3.0] - 2026-10-16

Aligns version, specifier, marker, requirement, tag, and filename handling with
`packaging` 26.2 and removes the `re.bzl` dependency.

### Breaking changes

Packaging and Bazel support:

- `load("@pypackaging.bzl", "pypackaging")` (`//:pypackaging.bzl`) and the
  `@pypackaging.bzl//:pypackaging` `bzl_library` are the only public
  entrypoints. `@pypackaging.bzl//pypackaging:pypackaging.bzl` is removed, and
  `//pypackaging/private/...` is private.
- Bazel 7.1 or newer with Bzlmod is required (`bazel_compatibility = [">=7.1.0"]`).
  `WORKSPACE.bazel` is removed.

Versions and specifiers:

- The second parameter of `specifiers.contains` and `specifiers.set_contains`
  is renamed from `version_str` to `version` (accepting either a string or a
  parsed version struct).
- `specifiers.parse` rejects `===` specifiers whose version contains Unicode
  whitespace.

Markers:

- `markers.evaluate` uses packaging's string operator table for non-version
  markers: `<` and `>` return `False`, `<=` and `>=` test equality, and `~=`
  and `===` fail with `"Undefined comparison"`.
- `markers.evaluate` validates environment value types and restricts list/tuple
  `extra` values to `==` and `!=`.
- `markers.parse` rejects dangling boolean operators, invalid string literals,
  and `\N{...}` escapes.
- Parsed marker string nodes hold decoded string values, `extra` comparisons
  are normalized at all nesting levels, and `python_implementation` normalizes
  to `platform_python_implementation`.

Requirements:

- `requirements.parse` enforces packaging's PEP 508 grammar and error messages.
- `extras` is deduplicated as well as normalized and sorted.

Tags and utilities:

- `utils.canonicalize_name(name, validate = True)` fails on invalid PEP 508
  project names.
- `utils.canonicalize_version` returns invalid version strings unchanged instead
  of failing, and strips surrounding whitespace.
- `tags.get_supported` matches packaging 26.2 and pip:
  - Places `linux_<arch>` after all `manylinux` and `musllinux` tags.
  - Lowercases all generated tags.
  - Falls back to `["any"]` when platform expansion produces no platforms.
  - Expands custom `macosx*`/`ios*` platform prefixes and normalizes Android
    and iOS ABIs.
  - Detects free-threaded CPython ABIs (`cp313t`) after filtering `abi3`/`none`.
- `tags.parse_tag` and `utils.parse_wheel_filename(...).tags` deduplicate
  expanded tags and accept empty tag components.

### Added

- `version.to_string` and `version.try_parse`.
- `specifiers.filter`, `specifiers.set_filter`, `specifiers.prereleases`, and
  `specifiers.set_prereleases`, plus `prereleases` and `installed` parameters on
  `contains`/`set_contains` and `parsed_version` on specifier structs.
- `markers.to_string` and `requirements.to_string`, plus `marker_str`,
  `raw_name`, and `raw_extras` fields on parsed requirement structs.
- Support for list/tuple `environment["extra"]` in `markers.evaluate`.
- `tags.priority_map`, `tags.select_compatible`, and `tags.tag_str`.
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and upstream license files under
  [LICENSES/](LICENSES/).

### Fixed

- `~=` zero-pads short candidate releases (e.g. `1` matches `~=1.0.0`).
- `specifiers.contains` and `specifiers.set_contains` return `False` for invalid
  PEP 440 candidate strings instead of failing (except `===`).
- `version.parse` and `specifiers.parse` strip ASCII and Unicode whitespace
  across all supported Bazel versions.
- `specifiers.parse_set` ignores empty comma-separated items (`">=1.0,"`).
- Version-keyed markers (`python_version`, `python_full_version`,
  `implementation_version`, `platform_release`) fall back to string comparison
  when the RHS is not a valid specifier and return `False` when the environment
  value is not a valid PEP 440 version.
- `python_full_version` values ending in `+` have `local` appended before
  evaluation.
- Marker parsing and evaluation no longer cap iteration at 1000 steps.
- `manylinux_X_Y` platforms with glibc major version >= 3 are supported.
- Release `docs.tar.gz` archives now ship extracted `.binaryproto` Stardoc
  targets, and dev-only packages are excluded from the release archive.

### Removed

- The `re.bzl` dependency.

## [0.2.2] and earlier

See the [GitHub releases](https://github.com/jvolkman/pypackaging.bzl/releases).

[0.3.0]: https://github.com/jvolkman/pypackaging.bzl/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/jvolkman/pypackaging.bzl/releases/tag/v0.2.2
