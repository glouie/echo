#!/usr/bin/python
# vim: set fileencoding=utf-8 :

import pytest

# it is strongly suggested NOT to use this property directly
# please use the following function instead
PYTEST_CONFIG = '__pytest_config'


def pytest_addoption(parser):
    splunk_config_group = parser.getgroup('Splunk Config Options')

    splunk_config_group.addoption(
        "--enable-warnings",
        action="store_true",
        dest="enable_warnings",
        default=False,
        help="enable warnings summary",
    )


@pytest.mark.tryfirst
def pytest_configure(config):
    """
    This is used for:
     1. bind config to PYTEST_CONFIG to avoid Pytest4 Warning
     about pytest.config.
     2. set log_print to False, to avoid captured log issue
     3. if not enable_warnings, then disable_warnings
    """
    setattr(pytest, PYTEST_CONFIG, config)

    config.option.log_print = False

    if not config.option.enable_warnings:
        config.option.disable_warnings = True


def get_pytest_config():
    """
    Get PYTEST_CONFIG object

    :return: pytest.config but avoid warning in pytest4
    :rtype: _pytest.config.Config
    """
    return getattr(pytest, PYTEST_CONFIG)
