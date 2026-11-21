"""Loads the workloads from `workloads.bzl` with the shim."""

import os

import starlark_shim


def workloads():
    """Return the dict of the workload names and the functions to measure."""
    shim = starlark_shim.Shim(_resolver())
    return shim.load("//:workloads.bzl")["WORKLOADS"]


def _resolver():
    try:
        from python.runfiles import runfiles
    except ImportError:
        # Executed without Bazel, the repository is the parent directory.
        here = os.path.dirname(os.path.abspath(__file__))
        return lambda repo, path: os.path.join(here, ".." if repo else ".", path)

    rfiles = runfiles.Create()
    assert rfiles is not None, "Failed to create runfiles"

    def resolve(repo, path):
        resolved = rfiles.Rlocation("{}/{}".format(repo or "_main", path))
        if not resolved or not os.path.exists(resolved):
            raise FileNotFoundError("{}//{}".format(repo, path))
        return resolved

    return resolve
