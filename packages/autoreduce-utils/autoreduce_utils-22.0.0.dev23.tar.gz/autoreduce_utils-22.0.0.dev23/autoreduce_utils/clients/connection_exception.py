# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Custom class for connection errors
"""


class ConnectionException(Exception):
    """
    Simple class for raising exceptions when we cannot connect to services
    """

    def __init__(self, service_name):
        message = f"Unable to connect to {service_name} with provided credentials. " \
                  f"Please check the {service_name} settings files then try again."
        super(ConnectionException, self).__init__(message)  # pylint:disable=super-with-arguments
