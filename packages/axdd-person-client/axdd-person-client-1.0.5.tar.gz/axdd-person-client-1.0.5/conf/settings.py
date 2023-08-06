# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import os


class AppSettings:

    AXDD_PERSON_CLIENT_ENV = os.getenv('AXDD_PERSON_CLIENT_ENV',
                                       default='localdev')

    UW_PERSON_DB_USERNAME = os.getenv('UW_PERSON_DB_USERNAME',
                                      default='postgres')
    UW_PERSON_DB_PASSWORD = os.getenv('UW_PERSON_DB_PASSWORD',
                                      default='postgres')
    UW_PERSON_DB_DATABASE = os.getenv('UW_PERSON_DB_DATABASE',
                                      default='postgres')
    UW_PERSON_DB_HOSTNAME = os.getenv('UW_PERSON_DB_HOSTNAME',
                                      default='localhost')
    UW_PERSON_DB_PORT = os.getenv('UW_PERSON_DB_PORT', default='5432')

    def get(self, attr):
        return getattr(AppSettings, attr)
