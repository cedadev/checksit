#!/usr/bin/env python

"""Tests for `checksit` package."""

__author__ = """Ag Stephens"""
__contact__ = 'ag.stephens@stfc.ac.uk'
__copyright__ = "Copyright 2020 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"

import pytest

from click.testing import CliRunner
from checksit import cli


#@pytest.fixture
#def response():
#    """Sample pytest fixture.
#
#    See more at: http://doc.pytest.org/en/latest/fixture.html
#    """
#    # import requests
#    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')
#
#
#def test_content(response):
#    """Sample pytest test function with the pytest fixture as an argument."""
#    # from bs4 import BeautifulSoup
#    # assert 'GitHub' in BeautifulSoup(response.content).title.string

params = [(cli.main, 0,  "Commands:\n  check\n  describe\n  show-specs\n  summary\n"), (cli.check, 2, "Error: Missing argument 'FILE_PATH'.\n")]

@pytest.mark.parametrize("command, exit_code, output_ending", params)
def test_command_line_interface(command, exit_code, output_ending):
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(command)
    assert result.exit_code == exit_code
    assert result.output.endswith(output_ending) == True
    #help_result = runner.invoke(cli.main, ['--help'])
    #assert help_result.exit_code == 0
    #assert '--help  Show this message and exit.' in help_result.output
