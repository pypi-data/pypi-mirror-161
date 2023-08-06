# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Validators to be used in the Message class
"""

from typing import List, Union


def validate_run_number(run_number: Union[int, str, List[int], List[str]]) -> bool:
    """
    Assert a run number is valid
    :param run_number: The run number to validate
    """
    try:
        if isinstance(run_number, list) and all(int(run_number) > 0 for run_number in run_number):
            return True
        elif int(run_number) > 0:
            return True
    except (ValueError, TypeError):
        return False
    return False


def validate_rb_number(rb_number):
    """
    Detects whether the RB number is a 7-digit number.

    :param rb_number:
    :return: False If the RB is not valid, otherwise true
    """
    try:
        rb_number = int(rb_number)
    except (ValueError, TypeError):
        return False

    return 999999 < rb_number < 10000000
