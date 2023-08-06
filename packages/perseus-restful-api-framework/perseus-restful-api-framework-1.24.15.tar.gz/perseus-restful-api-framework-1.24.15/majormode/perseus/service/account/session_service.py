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

import json

from majormode.perseus.constant.obj import ObjectStatus
from majormode.perseus.model.obj import Object
from majormode.perseus.service.base_rdbms_service import BaseRdbmsService
from majormode.perseus.service.base_rdbms_service import BaseService
from majormode.perseus.utils import cast
from majormode.perseus.utils.date_util import ISO8601DateTime
from pymemcache.client import base

import settings


class SessionService(BaseRdbmsService):
    """
    A login session is the period of activity between a user sign-in
    and sign-out of the platform.
    """

    class ExpiredSessionException(BaseService.BaseServiceException):
        """
        Signal that the account session of the user has expired.  The user
        needs to login again.
        """
        pass

    # Default user login session duration (token lifetime) expressed in
    # minutes (90 days).
    DEFAULT_LOGIN_SESSION_DURATION = 60 * 24 * 90

    # Maximum user login session duration (token lifetime) expressed in
    # minutes (180 days).
    MAXIMUM_LOGIN_SESSION_DURATION = 60 * 24 * 180

    # Pattern of the key used to store user login session providing the
    # identification of this session.
    MEMCACHED_SESSION_KEY_PATTERN = 'session:login:%s'

    def __init__(
            self,
            memcached_server_hostname=settings.MEMCACHED_SERVER_HOSTNAME or '127.0.0.1',
            memcached_server_port_number=settings.MEMCACHED_SERVER_PORT or 11211):
        """
        Build a new instance of the session service


        :param memcached_server_hostname: host name of the memcached server
            used to store user login session.

        :param memcached_server_port_number: port number of the memcached
            server.
        """
        super(SessionService, self).__init__()
        self._memcached = base.Client((memcached_server_hostname, memcached_server_port_number))

    def create_session(
            self,
            app_id,
            account_id,
            connection=None,
            session_duration=None):
        """
        Create a login session for the specified user.  The identification of
        the session can be used as an authentication token.


        :param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        :param account_id: Identification of a user account.

        :param connection: An `RdbmsConnection` object supporting the Python

        :param session_duration: Login session duration, expressed in
            seconds, corresponding to the interval of time between the
            creation of the token and the expiration of this login session.


        :return: an object containing the following members:

            * ``session_id``: identification of the user login session, also known
              as the authentication token.

            * ``account_id``: identification of the account of the user.

            * ``creation_time``: time when this login session has been created.

            * ``expiration_time``: time when this login session is going to expire.
        """
        session_duration = min(
            session_duration or SessionService.DEFAULT_LOGIN_SESSION_DURATION,
            SessionService.MAXIMUM_LOGIN_SESSION_DURATION)

        # Check whether a login session already exists for the specified user
        # and API key.  If any, reuse this login session by extending its
        # expiration time by the given duration, otherwise create a new login
        # session for this user with this API key.
        with self.acquire_rdbms_connection(connection=connection, auto_commit=True) as connection:
            cursor = connection.execute(
                """
                UPDATE 
                    account_session
                  SET 
                    object_status = %(OBJECT_STATUS_ENABLED)s,
                    expiration_time = current_timestamp + '%(session_duration)s minutes'::interval,
                    update_time = current_timestamp
                  FROM (
                    SELECT 
                        session_id
                      FROM
                        account_session
                      WHERE
                        account_id = %(account_id)s
                        AND app_id = %(app_id)s) AS self
                  WHERE
                    account_session.session_id = self.session_id
                  RETURNING
                    account_session.session_id,
                    account_id,
                    app_id,
                    creation_time,
                    expiration_time
                """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'account_id': account_id,
                    'app_id': app_id,
                    'session_duration': session_duration
                })
            row = cursor.fetch_one()

            if row is None:
                cursor = connection.execute(
                    """
                    INSERT INTO account_session(
                        account_id,
                        app_id,
                        expiration_time)
                      VALUES (
                        %(account_id)s,
                        %(app_id)s,
                        current_timestamp + '%(session_duration)s minutes'::interval)
                      RETURNING 
                        session_id,
                        account_id,
                        creation_time,
                        app_id,
                        expiration_time""",
                    {
                        'account_id': account_id,
                        'app_id': app_id,
                        'session_duration': session_duration
                    })
                row = cursor.fetch_one()

            session = row.get_object({
                'account_id': cast.string_to_uuid,
                'app_id': cast.string_to_uuid,
                'creation_time': cast.string_to_timestamp,
                'expiration_time': cast.string_to_timestamp,
                'session_id': cast.string_to_uuid
            })

        # Set the session token into the cache for future references.
        self._memcached.set(
            SessionService.MEMCACHED_SESSION_KEY_PATTERN % session.session_id.hex,
            json.dumps(session.stringify()),
            expire=session_duration)

        return session

    def drop_session(
            self,
            app_id,
            session,
            connection=None):
        """
        Drop the specified login session of a user.


        :param app_id: identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        :param session: An object containing the following attributes:

            * `account_id` (required): Identification of the account of the a user.

            * `session_id` (required): Identification of the user's session.

        :param connection: An object `RdbmsConnection`.


        :return: an object containing the following attribute:

            * ``session_id``: identification of the session that has been deleted.


        :raise IllegalAccessException: if the specified login session doesn't
            belong to the specified user.

        :raise UndefinedObjectException: if the specified identification
            doesn't refer to any user login session registered to the platform.
        """
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            cursor = connection.execute(
                """
                UPDATE 
                    account_session
                  SET 
                    object_status = %(OBJECT_STATUS_DELETED)s
                  WHERE 
                    account_id = %(account_id)s
                    AND app_id = %(app_id)s
                    AND object_status <> %(OBJECT_STATUS_DELETED)s
                  RETURNING 
                    session_id
                """,
                {
                    'OBJECT_STATUS_DELETED': ObjectStatus.deleted,
                    'account_id': session.account_id,
                    'app_id': app_id
                })

            row = cursor.fetch_one()
            if row is None:
                raise SessionService.UndefinedObjectException(
                        "undefined user session",
                        payload={'account_id': session.account_id, 'app_id': app_id })

            session = row.get_object({'session_id': cast.string_to_uuid})

            if session.session_id != session.session_id:
                raise SessionService.IllegalAccessException(
                    "the session does not belong to the specified user account",
                    payload={
                        'account_id': session.account_id,
                        'session_id': session.session_id
                    })

        self._memcached.delete(SessionService.MEMCACHED_SESSION_KEY_PATTERN % session.session_id.hex)

        return session

    def get_session(self, app_id, session_id):
        """
        Return the information about the specified authentication session.


        :param app_id: identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        :param session_id: identification of a user session.


        :return: a ``SessionToken`` instance containing the following members:

            * ``session_id``: authentication token that references a login session
              of a user.

            * ``account_id``: identification of the account of the user who has
                signed-in.

            * ``app_id``: identification of the client application such as a Web,
              a desktop, or a mobile application, that accesses the service.

            * ``creation_time``: date and time when the authentication token has
              been created, i.e., when the user has signed-in.

            * ``expiration_time``: date and time when the authentication token is
              going to expire.


        :raise ExpiredSessionException: If the account session of the user has
            expired.  The user needs to login again.


        :raise IllegalAccessException: If the user login session is registered
            with an API key other than the one specified.

        :raise UndefinedObjectException: Indicate that the specified
            identification doesn't refer to any user login session registered
            to the platform.
        """
        # Try first to retrieve the session from the cache before trying to
        # retrieve it from database.
        payload = self._memcached.get(SessionService.MEMCACHED_SESSION_KEY_PATTERN % session_id.hex)
        if False:  # deactivate cache
            # if payload is not None:
            session = Object()
            session.__dict__.update(json.loads(payload))
            session.account_id = cast.string_to_uuid(session.account_id)
            session.app_id = cast.string_to_uuid(session.app_id)
            session.creation_id = cast.string_to_timestamp(session.creation_time)
            session.expiration_time = cast.string_to_timestamp(session.expiration_time)
            session.session_id = cast.string_to_uuid(session.session_id)

            if session.expiration_time < ISO8601DateTime.now():
                raise self.ExpiredSessionException('The user session has timeout')

        else:
            with self.acquire_rdbms_connection() as connection:
                cursor = connection.execute(
                    """
                    SELECT 
                        session_id,
                        account_id,
                        app_id,
                        creation_time,
                        expiration_time,
                        object_status
                      FROM
                        account_session
                      WHERE
                        session_id = %(session_id)s
                    """,
                    {
                        'session_id': session_id
                    })
                row = cursor.fetch_one()
                if row is None:
                    raise self.ExpiredSessionException('Undefined user session')

                session = row.get_object({
                    'account_id': cast.string_to_uuid,
                    'app_id': cast.string_to_uuid,
                    'creation_time': cast.string_to_timestamp,
                    'expiration_time': cast.string_to_timestamp,
                    'session_id': cast.string_to_uuid
                })

                # Check the current status of the user session.
                if session.object_status == ObjectStatus.disabled:
                    raise self.ExpiredSessionException('The user has been logout')
                elif session.object_status == ObjectStatus.deleted:
                    raise self.ExpiredSessionException('The user has logout')

                del session.object_status

                # Check whether the user session has expired.
                if session.expiration_time < ISO8601DateTime.now():
                    raise self.ExpiredSessionException('The user session has timeout')

            # Store the user session into the cache for future references.
            self._memcached.set(
                    SessionService.MEMCACHED_SESSION_KEY_PATTERN % session_id.hex,
                    json.dumps(session.stringify()),
                    expire=SessionService.DEFAULT_LOGIN_SESSION_DURATION)

        if session.app_id != app_id:
            raise SessionService.IllegalAccessException(
                'The session is registered with another application',
                payload={'session_id': session_id})

        return session
