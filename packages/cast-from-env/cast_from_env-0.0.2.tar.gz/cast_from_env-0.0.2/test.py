from os import environ
from unittest import TestCase
from unittest.mock import patch

from cast_from_env import from_env


class XMLTests(TestCase):

    @patch.dict(environ, {'TEST_STR': 'a string', 'TEST_INT': '123', 'TEST_FLOAT': '12.34',
                          'TEST_TRUE': 'true', 'TEST_FALSE': 'no'})
    def test_from_env(self):
        assert from_env('NOT_SET') is None, 'Unset env var returns None if no default'
        assert from_env('NOT_SET', 'default') == 'default', 'Unset env var returns default'
        assert from_env('TEST_STR') == 'a string', 'Set env var with no default returns string'
        assert type(from_env('TEST_INT', 1)) is int, 'Env var with int default is cast to int'
        assert type(from_env('TEST_FLOAT', float)) is float, 'Env var is cast to float'
        assert from_env('TEST_TRUE', bool) is True, '"true" cast to bool is True'
        assert from_env('TEST_FALSE', True) is False, '"no" cast to bool is False'
