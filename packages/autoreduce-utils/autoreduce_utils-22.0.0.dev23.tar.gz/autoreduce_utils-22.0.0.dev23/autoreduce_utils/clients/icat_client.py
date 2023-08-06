# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Module to perform ICAT client functionality
Functions for login and query available from class
"""
import os
import icat

from autoreduce_utils.clients.connection_exception import ConnectionException


class ICATClient():
    """
    This class provides a layer of abstraction from Python ICAT.
    Only allowing logging in and querying.
    """

    def __init__(self):
        self.icat_host = os.getenv("ICAT_HOST")
        self.icat_user = os.getenv("ICAT_USER")
        self.icat_auth = os.getenv("ICAT_AUTH")
        self.icat_port = os.getenv("ICAT_PORT") or ''
        self.client = icat.Client(self.icat_host)

    def connect(self):
        """
        Log in to ICAT using the details provided in the credentials.ini file
        """

        self.client.login(auth=self.icat_auth,
                          credentials={
                              'username': self.icat_user,
                              'password': os.getenv("ICAT_PASSWORD")
                          })

    def _test_connection(self):
        """
        Test that the connection has been successful
        """
        try:
            self.client.refresh()
        except icat.exception.ICATSessionError as exp:
            raise ConnectionException("ICAT") from exp
        return True

    def refresh(self):
        """ Refreshes the ICAT session only if necessary """
        self.client.refresh()

    def disconnect(self):
        """ Disconnect the ICAT client """
        self.client.logout()

    def execute_query(self, query):
        """
        Runs a query on ICAT - assumes a valid login has already been obtained
        :param query: The query to run
        :return: The result of the query
        """

        try:
            self.client.refresh()
        except icat.exception.ICATSessionError:
            # Session has most likely expired, try and log in again.
            # Have to set sessionId to None otherwise python ICAT attempts
            # to log out with an expired sessionId
            self.client.sessionId = None
            self.connect()
        return self.client.search(query)
