# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
# pylint: skip-file
"""
Settings for connecting to the test services that run locally
"""
import os
from autoreduce_utils.clients.settings.client_settings_factory import ClientSettingsFactory

SETTINGS_FACTORY = ClientSettingsFactory()

ICAT_CREDENTIALS = SETTINGS_FACTORY.create('icat',
                                           username=os.getenv('ICAT_USER'),
                                           password=os.getenv('ICAT_PASSWORD'),
                                           host=os.getenv('ICAT_HOST'),
                                           port='',
                                           authentication_type=os.getenv('ICAT_AUTH'))

DB_CREDENTIALS = SETTINGS_FACTORY.create('database',
                                         username=os.getenv('DATABASE_USERNAME'),
                                         password=os.getenv('DATABASE_PASSWORD'),
                                         host=os.getenv('DATABASE_HOST'),
                                         port=os.getenv('DATABASE_PORT'),
                                         database_name=os.getenv('DATABASE_NAME'))

ACTIVEMQ_CREDENTIALS = SETTINGS_FACTORY.create('queue',
                                               username=os.getenv('ACTIVEMQ_USERNAME'),
                                               password=os.getenv('ACTIVEMQ_PASSWORD'),
                                               host=os.getenv('ACTIVEMQ_HOST'),
                                               port=os.getenv('ACTIVEMQ_PORT'))

CYCLE_SETTINGS = SETTINGS_FACTORY.create('cycle',
                                         username=os.getenv('CYCLE_USER'),
                                         password=os.getenv('CYCLE_PASSWORD'),
                                         host='',
                                         port='',
                                         uows_url=os.getenv('CYCLE_UOWS_URL'),
                                         scheduler_url=os.getenv('CYCLE_SCHEDULER_URL'))

SFTP_SETTINGS = SETTINGS_FACTORY.create('sftp',
                                        username=os.getenv('SFTP_USERNAME'),
                                        password=os.getenv('SFTP_PASSWORD'),
                                        host=os.getenv('SFTP_HOST'),
                                        port=os.getenv('SFTP_PORT'))
