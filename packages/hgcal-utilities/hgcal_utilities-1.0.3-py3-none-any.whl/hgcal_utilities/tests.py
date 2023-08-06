from _pytest.monkeypatch import monkeypatch
import multiprocessing as mp
import pytest
import zmq
import yaml
import logging
import time

from dict_utils import update_dict
from dict_utils import diff_dict
from dict_utils import nested_dict_from_keylist


def test_update_dict():
    """
    test the update_dict function
    """
    # check that subdicts are properly updated
    original = {'this': [{'a': 1}, {'b': 2}, {'c': 3}, 3], 'that': 'what'}
    update = {'this': [{'a': 3}, {'b': 3}, {'c': 5}, 5]}
    expected_output = {'this': [{'a': 3}, {'b': 3}, {'c': 5}, 5],
                       'that': 'what'}
    updated_dict = update_dict(original, update)
    assert updated_dict == expected_output

    # check that an update with an emty dict is a no-op
    original = {'this': [{'a': 1}, {'b': 2}, {'c': 3}, 3], 'that': 'what'}
    update = {}
    expected_output = {'this': [{'a': 1}, {'b': 2}, {'c': 3}, 3],
                       'that': 'what'}
    updated_dict = update_dict(original, update)
    assert updated_dict == expected_output

    # check that the in_place feature works as expected
    original = {'this': [{'a': 1}, {'b': 2}, {'c': 3}, 3], 'that': 'what'}
    update = {'this': [{'a': 3}, {'b': 3}, {'c': 5}, 5]}
    expected_output = {'this': [{'a': 3}, {'b': 3}, {'c': 5}, 5],
                       'that': 'what'}
    update_dict(original, update, in_place=True)
    assert original == expected_output


def test_diff_dict():
    test_dict_1 = {'a': 1, 'b': {'c': 2, 'f': 4}, 'e': 3}
    test_dict_2 = {'a': 2, 'b': {'c': 3, 'f': 4}, 'e': 3, 'g': 4}
    diff = {'a': 2, 'b': {'c': 3}, 'g': 4}
    result = diff_dict(test_dict_1, test_dict_2)
    assert result == diff
    result = diff_dict(test_dict_2, test_dict_1)
    assert result['b']['c'] == 2
    assert result['a'] == 1


def test_nested_dict_from_keylist():
    """
    test that the generate_patch_dict_from_key_tuple function
    """
    keys = [[['k1', 'k2', 'k3'], 'k4', 'k5'],
            [['k1', 'k2', 'k3'], 'k4', 'k5'],
            [['k1', 'k2', 'k3'], ['k4', 'k5'], 'k6']]
    value = 1
    expected_dict = [{'k1': {'k4': {'k5': 1}},
                      'k2': {'k4': {'k5': 1}},
                      'k3': {'k4': {'k5': 1}}},
                     {'k1': {'k4': {'k5': 1}},
                      'k2': {'k4': {'k5': 1}},
                      'k3': {'k4': {'k5': 1}}},
                     {'k1': {'k4': {'k6': 1}, 'k5': {'k6': 1}},
                      'k2': {'k4': {'k6': 1},
                             'k5': {'k6': 1}},
                      'k3': {'k4': {'k6': 1},
                             'k5': {'k6': 1}}
                      }]
    for key, exd_dict in zip(keys, expected_dict):
        patch_dict = nested_dict_from_keylist(key, value)
        assert patch_dict == exd_dict
