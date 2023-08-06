# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Combination of validation checks to be performed on the Message at each stage of the pipeline
"""
from autoreduce_utils.message.validation import validators
from autoreduce_utils.message.validation.process import dict_to_string


def validate_data_ready(message):
    """
    Assert a message is ready to be passed to the /DataReady queue
    :param message: A message object to be validated
    :return: True if valid
    """
    validity_dict = {
        'run_number': validators.validate_run_number(message.run_number),
        'rb_number': validators.validate_rb_number(message.rb_number),
        'started_by': isinstance(message.started_by, int),
        'file_path': isinstance(message.data, (str, list)),
        'facility': isinstance(message.facility, str),
        'software': isinstance(message.software, dict)
    }
    if False in validity_dict.values():
        raise RuntimeError(f"Validation failed: {dict_to_string(validity_dict)}")
