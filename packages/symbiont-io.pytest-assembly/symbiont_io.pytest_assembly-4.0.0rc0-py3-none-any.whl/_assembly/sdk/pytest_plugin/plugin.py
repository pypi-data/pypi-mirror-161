import pytest

from _assembly.sdk.pytest_plugin.arguments import add_pytest_arguments

from _assembly.sdk.pytest_plugin.fixtures import nodes_networks
from _assembly.sdk.pytest_plugin.fixtures.pytest_args import PytestArgs
from _assembly.sdk.pytest_plugin.markers import run_marker_setup
from assembly_client.api.network_client import NetworkClient


####################
### pytest hooks ###
####################


def pytest_addoption(parser):
    return add_pytest_arguments(parser)


def pytest_runtest_setup(item):
    return run_marker_setup(item)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "proptest: mark test as an expensive property test that only runs with --proptests",
    )
    config.addinivalue_line(
        "markers", "incremental: mark test as a depenent of a previous one"
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):

    # an incremental marker for classes that makes a class stop on first failure,
    # taken from http://doc.pytest.org/en/latest/example/simple.html
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item

    # set data on the test items so that we can check in fixtures if tests passed or failed
    # https://docs.pytest.org/en/latest/example/simple.html#making-test-result-information-available-in-fixtures

    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"

    setattr(rep, "markers", list(item.iter_markers()))
    setattr(item, "rep_" + rep.when, rep)


#######################
### pytest fixtures ###
#######################

### testing basics


@pytest.fixture(scope="class")
def store():
    """a dictionary for passing data between tests in a class"""
    return {}


@pytest.fixture(scope="class")
def async_network(sdk_args):
    """a network client that allows invoking contract functions, either locally or remote"""
    network = nodes_networks.network_fixture(sdk_args, NetworkClient)
    yield network

    if "benchmark" not in sdk_args.request.fixturenames:
        network.consistency_check()


@pytest.fixture(scope="class")
def network(sdk_args):
    """a network client that allows invoking contract functions, either locally or remote"""
    network = nodes_networks.network_fixture(sdk_args)
    yield network

    if "benchmark" not in sdk_args.request.fixturenames:
        network.consistency_check()


@pytest.fixture(scope="session")
def sdk_args(request):
    """
    provide access to configuration data post argument parsing and config file merging
    """
    return PytestArgs(request)
