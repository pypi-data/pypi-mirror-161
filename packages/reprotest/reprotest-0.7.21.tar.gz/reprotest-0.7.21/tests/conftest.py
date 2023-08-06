import distro
import pytest

SUPPORTED_DIST = ["debian", "fedora"]


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "need_builddeps: need need_builddeps"
    )
    config.addinivalue_line(
        "markers", "debian: filter tests for debian only"
    )
    config.addinivalue_line(
        "markers", "fedora: filter tests for fedora only"
    )


def pytest_runtest_setup(item):
    # get current dist
    dist = distro.id()
    # filter markers
    supported_dist = set(SUPPORTED_DIST).intersection(
        mark.name for mark in item.iter_markers())
    if supported_dist and dist not in supported_dist:
        pytest.skip("cannot run on {}".format(dist))
