# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Exercise the functions that handle validating a message at each pipeline stage
"""
from unittest import TestCase, mock

from autoreduce_utils.message.validation import stages, validators
from autoreduce_utils.message.message import Message


class TestStages(TestCase):
    """
    Assert the stages return the correct bool value based on if they are valid
    """

    def setUp(self):
        self.valid_message = Message(
            run_number=1234,
            instrument='GEM',
            rb_number=1000000,
            started_by=-1,
            data='test/file/path',
        )

    def test_valid_validate_data_ready(self):
        """
        Test: validate_data_ready returns true
        When: supplied with a valid message
        """
        # This function raises on invalid message
        # if this test passes there was no raise
        stages.validate_data_ready(self.valid_message)

    @mock.patch("autoreduce_utils.message.validation.stages.validators", spec=validators)
    def test_validate_data_ready_calls_validators(self, patched_validators):
        """
        Test: validate data calls the correct validators whilst running
        When: supplied with any message
        """
        stages.validate_data_ready(self.valid_message)

        patched_validators.validate_run_number.assert_called_once()
        patched_validators.validate_rb_number.assert_called_once()
