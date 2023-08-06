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

import logging

import settings


class BaseService:
    """
    Base class of service.

    It provides logging facility to the inheriting service class.  The
    logger is identifier by the global constant `LOGGER_NAME` of
    the Python module `settings`.

    It also provides facility to publish messages to an Advanced
    Message Queuing Protocol (AMQP) compliant broker, which connection
    properties are defined in the dictionary
    `AMQP_CONNECTION_PROPERTIES` defined in the Python module.
    `settings`.
    """
    class BaseServiceException(Exception):
        """
        Base class of exception that a service might raise to indicate some
        unexpected conditions.
        """
        def __init__(self, message=None, payload=None):
            """
            Build a new instance of an exception that indicates an unexpected
            condition met by a service when processing a client's request.


            :param message: A humanly-readable message that describes this
                exception instance.

            :param payload: A JSON expression that provides detailed information
                about this exception instance.
            """
            super().__init__(message)
            self.payload = payload

    class DeletedObjectException(BaseServiceException):
        """
        Signal that the specified object has been deleted and as such it
        cannot be used or referenced anymore.
        """

    class DisabledObjectException(BaseServiceException):
        """
        Signal that the specified object has been disabled and as such it
        cannot be used.
        """

    class InvalidOperationException(BaseServiceException):
        """
        Signal the operation requested is invalid, for instance one or several
        arguments provided within the request are not coherent together or the
        state of the object on which the operation is requested.
        """

    class IllegalAccessException(BaseServiceException):
        """
        Signal that the user on behalf whom a function is called is not
        authorized to perform the action requested.
        """

    class InvalidArgumentException(BaseServiceException):
        """
        Signal that an argument passed to a function is invalid, more likely
        of the wrong type.
        """

    class PendingObjectException(BaseServiceException):
        """
        Signal that the specified object is still pending and as such it
        cannot be used until it has been enabled.
        """

    class UndefinedObjectException(BaseServiceException):
        """
        Signal that the specified object doesn't exist and as such it cannot
        be referenced.
        """

    # Logger for custom service trace.
    __logger__ = logging.getLogger(getattr(settings, 'LOGGER_NAME'))

    def __init__(self):
        self._service_name = self.__class__.__name__

    def get_service_name(self):
        return self._service_name

    @staticmethod
    def log_critical(message):
        BaseService.__logger__.critical(message)

    @staticmethod
    def log_debug(message):
        BaseService.__logger__.debug(message)

    @staticmethod
    def log_error(message):
        BaseService.__logger__.error(message)

    @staticmethod
    def log_info(message):
        BaseService.__logger__.info(message)

    @staticmethod
    def log_warning(message):
        BaseService.__logger__.warning(message)
