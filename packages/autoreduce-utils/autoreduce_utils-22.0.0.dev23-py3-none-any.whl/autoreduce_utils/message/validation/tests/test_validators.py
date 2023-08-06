# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Exercise the validation functions
"""
import unittest

from autoreduce_utils.message.validation import validators


class TestValidators(unittest.TestCase):
    """
    As the validators are simple bool returns,
    we are validating a function completely per test case
    """

    def test_validate_run_number(self):
        """
        Test: validate_run_number returns the expected result
        When: In valid and invalid cases
        """
        self.assertTrue(validators.validate_run_number(1))
        self.assertTrue(validators.validate_run_number("001"))
        self.assertTrue(validators.validate_run_number([123, 123]))
        self.assertTrue(validators.validate_run_number(["123", "123"]))

        self.assertFalse(validators.validate_run_number(0))
        self.assertFalse(validators.validate_run_number(-1))
        self.assertFalse(validators.validate_run_number("string"))
        self.assertFalse(validators.validate_run_number(["string", "string"]))

    def test_validate_rb_number(self):
        """
        Tests the valid and invalid cases for RB numbers
        """
        valid_values = [1000000, 2000000, "1000000", 9999999]
        for i in valid_values:
            self.assertTrue(validators.validate_rb_number(i), f"Failed with value {i}")

        invalid_values = [0, 0.1, -1, -100, None, "foo", 12345678910, "1231435252242"]
        for i in invalid_values:
            self.assertFalse(validators.validate_rb_number(i), f"Failed with value {i}")
