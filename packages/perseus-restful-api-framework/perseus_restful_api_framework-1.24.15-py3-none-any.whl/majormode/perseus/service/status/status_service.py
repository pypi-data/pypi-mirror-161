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

import datetime
import json
import jsonpickle
import time

from majormode.perseus.model.obj import Object
from majormode.perseus.service.base_rdbms_service import BaseRdbmsService

import settings


class StatusService(BaseRdbmsService):
    def check_status(self):
        """
        Get the status of the different software components that the platform
        is built on.

        @return: a dictionary of software component status, where the key
                 corresponds to the name of the component and the value
                 contains the following attributes:
                 * ``name``: name of the software component.
                 * ``status``: boolean value that indicates whether the
                   component is available.
                 * ``check_duration``: duration, expressed in milliseconds, of
                   the check.
                 * ``error``: possible error detected by the method
                   responsible for checking this component.
        """
        class ComponentStatus(object):
            def __init__(self, name, status, check_duration, error=None):
                self.name = name
                self.status = status
                self.check_duration = check_duration
                if error is not None:
                    self.error = error

        def check_amqp():
            MESSAGE_TYPE_ON_LBS_STATUS_CHECKED = 'on_lbs_status_checked'
            with self.acquire_amqp_connection() as connection:
                connection.publish(MESSAGE_TYPE_ON_LBS_STATUS_CHECKED,
                    { 'check_time': time.strftime('%Y-%m-%dT%H:%M:%S.000+00', time.gmtime()) })

        def check_memcached():
            """
            Check whether memcached is up and running.

            The function tries to read the value of a key from memcached and to
            write a new value for this key corresponding to the current time.
            """
            import pylibmc

            MEMCACHED_CHECK_STATUS_KEY = 'cerberus.status.last_check_time'

            memcached = pylibmc.Client(['%s:%d' % (settings.MEMCACHED_SERVER_HOSTNAME, settings.MEMCACHED_SERVER_PORT) ], binary=True)
            memcached.behaviors = {"tcp_nodelay": True, "ketama": True}
            memcached.get(MEMCACHED_CHECK_STATUS_KEY)

            status = Object()
            status.last_check_time = time.strftime('%Y-%m-%dT%H:%M:%S.000+00', time.gmtime())

            memcached.set(MEMCACHED_CHECK_STATUS_KEY,
                          json.dumps(jsonpickle.Pickler(unpicklable=False).flatten(status)))

        def check_postgresql():
            """
            Check whether PostgreSQL is up and running.

            The function checks whether the status table has been created.  If
            not, the function creates it and stored the current time, otherwise it
            deletes any content from this table and stored the current time.
            """
            POSTGRESQL_CHECK_TABLE_NAME = '_cerberus_status_'

            with self.acquire_rdbms_connection() as connection:
                cursor = connection.execute("""
                    SELECT a.attname as "name",
                           pg_catalog.format_type(a.atttypid, a.atttypmod) as "data_type"
                       FROM pg_catalog.pg_attribute a
                       WHERE a.attnum > 0
                         AND NOT a.attisdropped
                         AND a.attrelid = (
                           SELECT c.oid
                             FROM pg_catalog.pg_class c
                             LEFT JOIN pg_catalog.pg_namespace n
                               ON n.oid = c.relnamespace
                             WHERE c.relname ~ '^(%s)$'
                             AND pg_catalog.pg_table_is_visible(c.oid))""" % POSTGRESQL_CHECK_TABLE_NAME)
                columns = [ row.get_object() for row in cursor.fetch_all() ]
                for column in columns:
                    if column.name == 'last_check_time' and \
                       column.data_type == 'timestamp with time zone':
                        connection.execute("""
                            DELETE FROM %s
                              RETURNING last_check_time""" % POSTGRESQL_CHECK_TABLE_NAME)
                        connection.execute("""
                            INSERT INTO %s(last_check_time)
                              VALUES (current_timestamp)""" % POSTGRESQL_CHECK_TABLE_NAME)
                        break
                else:
                    if len(columns) > 0:
                        connection.execute('DROP TABLE %s' % POSTGRESQL_CHECK_TABLE_NAME)
                    connection.execute("""
                        CREATE TABLE %s(
                          last_check_time timestamp with time zone NOT NULL DEFAULT current_timestamp)""" % POSTGRESQL_CHECK_TABLE_NAME)

                connection.commit()

        def check_redis():
            """
            Check whether redis is up and running.

            The function tries to read the value of a key from redis and to
            write a new value for this key corresponding to the current time.
            """
            import redis

            REDIS_CHECK_STATUS_KEY = 'cerberus.status.last_check_time'

            status = Object()
            status.last_check_time = time.strftime('%Y-%m-%dT%H:%M:%S.000+00', time.gmtime())

            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            r.get(REDIS_CHECK_STATUS_KEY)
            r.set(REDIS_CHECK_STATUS_KEY,
                  json.dumps(jsonpickle.Pickler(unpicklable=False).flatten(status)))

        CHECK_METHODS = [
            ('memcached', check_memcached),
            ('postgresql', check_postgresql),
            ('redis', check_redis)
            #('amqp', check_amqp),
        ]

        component_statuses = []
        for (component_name, check_method) in CHECK_METHODS:
            try:
                begin_time = datetime.datetime.now()
                check_method()
                end_time = datetime.datetime.now()
                component_statuses.append(ComponentStatus(component_name, True, end_time - begin_time))
            except Exception as exception:
                end_time = datetime.datetime.now()
                component_statuses.append(
                    ComponentStatus(component_name, False, end_time - begin_time, error=repr(exception)))

        return component_statuses
