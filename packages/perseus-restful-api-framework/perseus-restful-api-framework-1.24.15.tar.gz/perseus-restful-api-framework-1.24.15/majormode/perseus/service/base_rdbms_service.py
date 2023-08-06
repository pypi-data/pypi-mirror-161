# Copyright (C) 2019 Majormode.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from majormode.perseus.service.base_service import BaseService
from majormode.perseus.utils import rdbms
from majormode.perseus.utils.rdbms import RdbmsConnection

import settings


class BaseRdbmsService(BaseService):
    # Default limit of the size of a result set that a method of the
    # inheriting class returns to a caller.
    DEFAULT_LIMIT = 20

    # Maximum limit of the size of a result set that a method of the
    # inheriting class returns to a caller.
    MAXIMUM_LIMIT = 100

    def acquire_rdbms_connection(
            self,
            auto_commit=False,
            connection=None):
        """
        Return a connection to a Relational DataBase Management System (RDBMS)
        that is the most appropriate for the service requesting this
        connection, as defined in the Python settings file (cf.
        `RDBMS_CONNECTION_PROPERTIES`).


        :param auto_commit: indicate whether the transaction needs to be
           committed at the end of the session.

        :param connection: a `RdbmsConnection` instance to be used
            supporting the Python clause `with ...:`.  This instance is
            returned if not `None`, otherwise the function acquires a new
            connection instance.


        :return: a `RdbmsConnection` instance to be used supporting the
            Python clause `with ...:`.
        """
        if connection is not None and not connection.auto_commit and auto_commit:
            raise self.InvalidArgumentException(
                "Mismatch between requested auto-commit and the auto-commit of the connection passed")

        return connection or RdbmsConnection.acquire_connection(
                settings.RDBMS_CONNECTION_PROPERTIES,
                logger_name=settings.LOGGER_NAME,
                auto_commit=auto_commit,
                #tag=self.get_service_name()
            )

    @staticmethod
    def sql_quote(value):
        return rdbms.sql_quote(value)
