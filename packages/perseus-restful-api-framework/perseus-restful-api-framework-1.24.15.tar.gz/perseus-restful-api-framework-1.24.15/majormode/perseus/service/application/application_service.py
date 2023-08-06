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

import base64
import hmac
import hashlib
import logging
import os
import urllib.parse
import uuid

from majormode.perseus.constant.application import ApplicationPlatform
from majormode.perseus.constant.application import ApplicationStage
from majormode.perseus.constant.obj import ObjectStatus
from majormode.perseus.service.account.account_service import AccountService
from majormode.perseus.service.base_rdbms_service import BaseRdbmsService
from majormode.perseus.service.base_service import BaseService
from majormode.perseus.service.team.team_service import TeamService
from majormode.perseus.utils import cast

import settings


class ApplicationService(BaseRdbmsService):
    """

    """
    # Define the name of the Content Delivery Network (CDN) bucket that
    # groups application logos all together.
    CDN_BUCKET_NAME_PICTURE = 'app'

    # Hash algorithm to use to generate the Consumer Secret key of an
    # application.
    CRYPTOGRAPHIC_HASH_FUNCTION = hashlib.sha1

    # # Determine which properties passed to this function have changed.  If
    # # no property has changed, the function simply returns.
    # IS_PROPERTY_NULLABLE_DICT = {
    #     'app_name': False,
    #     'platform': False,
    #     'logo_url': True,
    # }

    class ApplicationNameAlreadyRegisteredException(BaseService.BaseServiceException):
        """
        Signal the a specified application name is already used by another
        client application registered against the platform.
        """

    class IncorrectSignatureException(BaseService.BaseServiceException):
        """
        Signal that signature of the HTTP request is incorrect.  The API
        Secret Key that has been used to sign the request might no correspond
        to the associated API Consumer Key.
        """

    def _assert_administrator(self, app_id, account_id):
        """
        Assert that the specified user is an administrator of the application,
        either as an individual, either as an administrator of the team that
        owns this application.


        :param app_id: Identification of a application to check whether the
            specified user is administrator of.

        :param account_id: Identification of the account of a user to check
            whether he has the role of administrator for the specified
            application.


        :raise IllegalAccessException: If the user specified by his account is
           not an administrator of the application.
        """
        application = self.get_application(app_id, check_status=True)
        if application.team_id is None:
            if account_id != application.account_id:
                raise self.IllegalAccessException()
        else:
            TeamService()._assert_administrator(account_id, application.team_id)

    @classmethod
    def build_picture_url(cls, picture_id):
        """
        Return the Uniform Resource Locator of the picture of an application.


        @param picture_id: The identification of the picture of an application.


        @return: A string representing the Uniform Resource Locator of the
            picture.
        """
        return picture_id and os.path.join(
            settings.CDN_URL_HOSTNAME,
            cls.CDN_BUCKET_NAME_PICTURE,
            str(picture_id))

    def get_application(
            self,
            app_id,
            check_status=False,
            connection=None):
        """
        Return extended information about the application specified by its
        identification.


        @warning: This function is for internal usage only; it MUST not be
            surfaced to client applications.


        :param app_id: Identification of the application that accesses the service.

        :param check_status: Indicate whether the function must check the
            current status of this application and raise an exception if it is
            not of enabled.

        :param connection: An object `RdbmsConnection`.


        :return: An object containing the following members:

            * ``account_id``: Identification of the account of the user who
              registered this client application.

            * ``app_id``: Identification of the client application.

            * ``consumer_key``: A unique string that identifies the API
              Consumer Key tied to the client application.

            * ``consumer_secret``: A string kept secret used to authenticate the API
              Consumer Key.

            * ``creation_time``: Time when the application has been registered.

            * ``name``: Name of the application.

            * ``object_status``: Current status of the application.

            * ``picture_id``: Identification of the logo of the application.

            * ``package``: Package name of the family this application belongs
              to, if any defined.  This allows to group under a same "branding
              umbrella" several applications that share the functionalities,
              the same users base. For instance, a software product can have a
              lite (free) and full (paid) versions on an Android and an iOS
              platforms, etc. Grouping applications of a same family allows to
              send notification to a user to whatever version(s) and platform(s)
              he could use.

            * ``platform``: Identification of the platform which the application
              runs on (cf. ``ApplicationPlatform``).

            * ``team_id``: Identification of the organization this application
              belongs to.

            * ``update_time``: Most recent time when some information of the
              application has been modified, such as its name or its API keys.


        :raise DeletedObjectException: If the application has been deleted,
            while the argument ``check_status`` has been set to ``True``.

        :raise DisabledObjectException: If the application has been disabled,
            while the argument ``check_status`` has been set to ``True``.

        :raise UndefinedObjectException: If the specified identification
            doesn't refer to a application registered against the platform.
        """
        # Retrieve the information of the application specified by its
        # identification.
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    app_id,
                    app_name
                    package_name,
                    picture_id,
                    stage,
                    platform,
                    consumer_key,
                    consumer_secret,
                    account_id,
                    team_id,
                    object_status,
                    creation_time,
                    update_time
                  FROM
                    application
                  WHERE
                    app_id = %(app_id)s
                """,
                {
                    'app_id': app_id
                }
            )
            row = cursor.fetch_one()

            if row is None:
                raise AccountService.UndefinedObjectException(f'Undefined application "{app_id}"')

            application = row.get_object({
                'account_id': cast.string_to_uuid,
                'app_id': cast.string_to_uuid,
                'creation_time': cast.string_to_timestamp,
                'object_status': ObjectStatus,
                'picture_id': cast.string_to_uuid,
                'platform': ApplicationPlatform,
                'stage': ApplicationStage,
                'team_id': cast.string_to_uuid,
                'update_time': cast.string_to_timestamp
            })

            # Check the current status of the application.
            if check_status:
                if application.object_status == ObjectStatus.deleted:
                    raise ApplicationService.DeletedObjectException(f'Application "{app_id}" is deleted')
                elif application.object_status == ObjectStatus.disabled:
                    raise ApplicationService.DisabledObjectException(f'Application "{app_id}" is disabled')

            return application

    def register_application(
            self,
            account_id,
            name,
            platform,
            package=None,
            picture_id=None,
            stage=ApplicationStage.sandbox,
            team_id=None):
        """
        Register an application that needs to access to the online service.

        Generate a new Application Programming Interface (API) key, which
        uniquely identifies this application.

        :param account_id: Identification of the account of the user who
           registers this application.  This account will own the API key that
           is issued.

        :param name: The name of the application.

        :param picture_id: Identification of the logo of the application.

        :param platform: An item of `ApplicationPlatform` that describes the
            platform that this application runs on.

        :param package: package name of the family this application belongs
            to, if any defined. This allows to group under a same "branding
            umbrella" several applications that share the functionalities, the
            same users base. For instance, a software product can have a lite
            (free) and full (paid) versions on an Android and an iOS platforms,
            etc. Grouping applications of a same family allows to send
            notification to a user to whatever version(s) and platform(s) he
            could use.

        :param stage: An item of ``ApplicationStage`` that indicates the
            environment stage which the application is deployed onto.

        :param team_id: Identification of a team this application belongs to.


        :return: An object that contains the following members:

            * ``app_id``: Identification of the application.

            * ``consumer_key``: A unique string that identifies the API Consumer
              Key.

            * ``consumer_secret``: A string that must be kept secret, which
              is used to authenticate the API Consumer Key.


            * ``picture_id``: Identification of the application's logo picture, if
              any defined.

            * ``picture_url``: Uniform Resource Locator (URL) that specifies the
              location of the application's logo picture, if any defined.  A
              client application can use this URL and append the query parameter
              ``size`` to specify a given pixel resolution of the picture, such as
              ``thumbnail``, ``small``, ``medium``, ``large``.

            * ``object_status``: Current status of the application.

            * ``creation_time``: Time when the application has been registered and
              the application API keys have been generated.

            * ``update_time``: Time of the most recent modification of one or more
              properties of this application.


        :raise ApplicationNameAlreadyRegisteredException: If the name of the
            application to register is already used for an other application.

        :raise DeletedObjectException: If the account of the user who registers
            this application has been deleted.

        :raise DisabledObjectException: If the account of the user who
            registers this application has been disabled.

        :raise UndefinedObjectException: If the argument ``account_id`` doesn't
            refer to a user account registered to the platform.
        """
        with self.acquire_rdbms_connection(True) as connection:
            # Retrieve information about the account of the user who registers this
            # application.
            AccountService().get_account(account_id, check_status=True, connection=connection)

            # Check whether there is no other application registered with the same
            # name for the same platform.
            cursor = connection.execute(
                """
                SELECT 
                    true
                  FROM 
                    application
                  WHERE 
                    lower(app_name) = lower(%(app_name)s)
                    AND platform = %(platform)s
                """,
                {
                    'app_name': name,
                    'platform': platform
                })

            if cursor.fetch_one() is not None:
                raise ApplicationService.ApplicationNameAlreadyRegisteredException('Application name already used')

            # Register the application and generate its API keys.
            cursor = connection.execute(
                """
                INSERT INTO application(
                    app_name,
                    platform,
                    stage,
                    package_name,
                    consumer_key,
                    consumer_secret,
                    picture_id,
                    account_id, 
                    team_id)
                  VALUES 
                    (%(app_name)s,
                     %(platform)s,
                     %(stage)s,
                     %(package_name)s,
                     %(consumer_key)s,
                     %(consumer_secret)s,
                     %(picture_id)s,
                     %(account_id)s,
                     %(team_id)s)
                  RETURNING 
                    app_id,
                    creation_time,
                    object_status,
                    consumer_key,
                    consumer_secret,
                    picture_id,
                    stage,
                    update_time
                """,
                {
                    'account_id': account_id,
                    'app_name': name,
                    'consumer_key': uuid.uuid1().hex,
                    'consumer_secret': base64.urlsafe_b64encode(uuid.uuid4().hex.encode()).decode(),
                    'package_name': package,
                    'picture_id': picture_id,
                    'platform': platform,
                    'stage': stage or ApplicationStage.sandbox,
                    'team_id': team_id
                })
            row = cursor.fetch_one()

            # Return the properties of this application.
            application = row.get_object({
                'app_id': cast.string_to_uuid,
                'creation_time': cast.string_to_timestamp,
                'object_status': ObjectStatus,
                'picture_id': cast.string_to_uuid,
                'stage': ApplicationStage,
                'update_time': cast.string_to_timestamp
            })

            application.picture_url = application.picture_id and os.path.join(
                settings.CDN_URL,
                self.CDN_BUCKET_NAME_PICTURE, str(application.picture_id))

            return application

    def validate_signature(
            self,
            consumer_key,
            path_query_string,
            message_body,
            api_sig=None,
            strict=True):
        """
        Check whether the Uniform Resource Locator (URL) specified in a HTTP
        request performed by a client application against the platform, is
        correctly signed with the secret key associated to the API key of the
        client application.


        :param consumer_key: Application Programming Interface (API) key tied
            to the application that accesses the service.

        :param path_query_string: Path and query string of the HTTP request
            that the application must have signed with its API secret key.

        :param message_body: Content of the HTTP request message body, or
            ``None`` if no message body has been passed along with the HTTP
            request.

        :param api_sig: Signature of the HTTP request as calculated by the
            application.

        :param strict: Indicate whether the signature has to be verified or if
            the function should only checked that the application is at least
            enabled.  For instance, development environments should not require
            HTTP requests to be signed so that developers can easily debug them
            through command line tools such as cURL.


        :return: The identification of the application.


        :raise DeletedObjectException: If the specified API key has been
            deleted, and as such, it cannot be used or referenced anymore.

        :raise DisabledObjectException: If the specified API key has been
            disabled, and as such, it cannot be used anymore

        :raise IncorrectSignatureException: If the HTTP request has not been
            signed while the signature is required (production stage) or
            requested (argument ``strict``), or if the signature of the HTTP
            request is incorrect.  The API Secret Key that has been used to
            sign the request might no correspond to the associated API
            Consumer Key.

        :raise UndefinedObjectException: If the specified API key has not been
            registered against the platform.
        """
        # Retrieve information about the application.
        with self.acquire_rdbms_connection() as connection:
            cursor = connection.execute(
                """
                SELECT 
                    app_id,
                    consumer_secret,
                    stage,
                    object_status
                  FROM
                    application
                  WHERE
                    consumer_key = %(consumer_key)s
                """,
                {
                    'consumer_key': consumer_key
                }
            )
            row = cursor.fetch_one()
            if row is None:
                raise self.UndefinedObjectException(f"Undefined API consumer key {consumer_key}")

            application = row.get_object({
                'app_id': cast.string_to_uuid,
                'object_status': ObjectStatus,
                'stage': ApplicationStage})

        # Check the current status of the application.
        if application.object_status == ObjectStatus.deleted:
            raise ApplicationService.DeletedObjectException(f"The API consumer key {consumer_key} has been deleted")
        elif application.object_status == ObjectStatus.disabled:
            raise ApplicationService.DisabledObjectException(f"The API consumer key {consumer_key} has been disabled")

        # Check whether the HTTP request signature is required.
        if (application.stage == ApplicationStage.live or strict) and api_sig is None:
            raise self.IncorrectSignatureException('Undefined HTTP request signature')

        # Check whether the HTTP request signature is valid.
        if api_sig:
            # Replace %xx escapes from the query string with their single-character
            # equivalent.  Client applications generally build query string without
            # escaping special characters, while the HTTP library they used will do
            # encode them behind the scene.
            #
            # For example, one client application prepare and sign the following URL:
            #
            # ```url
            # /school/child?limit=100&offset=0&sync_time=2020-10-15T09:55:52.108+07:00'
            # ```
            #
            # But, its HTTP library encodes and sends to the RESTful API server the
            # following URL:
            #
            # ```url
            # /school/child?limit=100&offset=0&sync_time=2020-10-15T09%3A55%3A52.108%2B07%3A00"
            # ```
            message = urllib.parse.unquote(path_query_string)

            # Add the decoded version of the message body, if any.
            if message_body is not None:
                message += message_body.decode()

            digest = hmac \
                .new(
                    application.consumer_secret.encode(),
                    msg=message.encode(),
                    digestmod=ApplicationService.CRYPTOGRAPHIC_HASH_FUNCTION) \
                .hexdigest()

            if api_sig.lower() != digest:
                logging.debug(f'Path query string: "{path_query_string}"')
                logging.debug(f'Message body: "{"" if message_body is None else message_body.decode()}"')
                logging.debug(f'Encoded message: "{message}"')
                logging.debug(f'Expected signature: "{digest}"')
                logging.debug(f'Client signature: "{api_sig.lower()}"')
                raise ApplicationService.IncorrectSignatureException("Invalid HTTP request signature")

        return application.app_id

    # def update_application(self, app_id, account_id, this_app_id, properties):
    #     """
    #     Update some modifiable properties of the specified client application.
    #
    #
    #     :param app_id: identification of the client application such as a Web,
    #         a desktop, or a mobile application, that accesses the service.
    #
    #     :param account_id: identification of the account of the user who is
    #         updating the role of the member.  This first user MUST have a role
    #         of administrator.
    #
    #     :param this_app_id: identification of the client application for which
    #         some properties are updated.
    #
    #     :param properties: a dictionary of properties of the specified client
    #         application to be modified.
    #
    #
    #     :raise DeletedObjectException: if the client application has been
    #         deleted.
    #
    #     :raise DisabledObjectException: if the client application has been
    #         disabled.
    #
    #     :raise IllegalAccessException: if the user on behalf of some
    #         properties of the client application are modified is not the agent
    #         or one of the regular administrators of this application.
    #
    #     :raise UndefinedObjectException: if the specified identification
    #         doesn't refer to a client application registered to the platform.
    #     """
    #     with self.acquire_rdbms_connection(True) as connection:
    #         # Retrieve information about the account that registers this API key,
    #         # and check whether the current status of this account allows him to
    #         # register an API key.
    #         AccountService().get_account(account_id, check_status=True)
    #
    #         application = self.get_application(this_app_id, check_status=True)
    #
    #         if account_id != application.account_id:
    #             cursor = connection.execute("""
    #                 SELECT member_role
    #                   FROM application_member
    #                   WHERE app_id = %(app_id)s
    #                     AND account_id = %(account_id)s""",
    #                 { 'account_id': account_id,
    #                   'app_id': this_app_id })
    #             row = cursor.fetch_one()
    #             if row is None or row.get_value('member_role') != str(ApplicationService.MemberRole.administrator):
    #                 raise ApplicationService.IllegalAccessException('Not an administrator of the client application')
    #
    #         # Check whether there is no other API key registered with the same
    #         # name.
    #         name = properties.get('name')
    #         if name is not None and name != application.name:
    #             cursor = connection.execute("""
    #                 SELECT true
    #                   FROM application
    #                   WHERE lower(app_name) = lower(%(app_name)s)""",
    #                 { 'app_name': name })
    #             if cursor.get_row_count() > 0:
    #                 raise ApplicationService.ApplicationNameAlreadyRegisteredException('Application name already registered')
    #
    #         modified_properties = dict(
    #             [ (name, value) for (name, value) in properties.iteritems()
    #                 if ((self.IS_PROPERTY_NULLABLE_DICT[name] or value is not None) and \
    #                     getattr(application, name) != value) ])
    #
    #         if modified_properties:
    #             update_statement = [ "%s = %%(%s)s" % (name, name) for (name, value) in modified_properties.items() ]
    #             modified_properties['app_id'] = this_app_id
    #
    #             cursor = connection.execute("""
    #                 UPDATE application
    #                   SET """ + ','.join(update_statement) + """,
    #                       update_time = current_timestamp
    #                   WHERE app_id = %(app_id)s""",
    #               modified_properties)

    # def get_application_by_name(self, name, check_status=False):
    #     """
    #     Return extended information about the client application specified by
    #     its name.
    #
    #
    #     @warning: this function is for internal usage only; it MUST not be
    #         surfaced to client applications.
    #
    #
    #     :param name: name of the application to return information.
    #
    #     :param check_status: indicate whether the function must check the
    #         current status of this user account and raise an exception if it is
    #         not of enabled.
    #
    #     :return: an instance containing the following members:
    #
    #         * ``account_id``: identification of the account of the user who
    #           registered this client application.
    #
    #         * ``app_id``: identification of the application.
    #
    #         * ``app_name``: the name of the application.
    #
    #         * ``consumer_key``: a unique string that identifies the API key
    #           tied to the client application.
    #
    #         * ``consumer_secret``: a string kept secret, which is used to
    #           authenticate the API key.
    #
    #         * ``creation_time``: time when the application has been registered.
    #
    #         * ``picture_id``: identification of the logo of the client
    #           application.
    #
    #         * ``object_status``: current status of the application.
    #
    #         * ``package_name``: package name of the family this application belongs
    #           to, if any defined. This allows to group under a same "branding
    #           umbrella" several applications that share the functionalities,
    #           the same users base. For instance, a software product can have a
    #           lite (free) and full (paid) versions on an Android and an iOS
    #           platforms, etc. Grouping applications of a same family allows to
    #           send notification to a user to whatever version(s) and platform(s)
    #           he could use.
    #
    #         * ``platform``: identification of the platform on which the client
    #          application runs (cf. ``ApplicationService.ApplicationPlatform``).
    #
    #         * ``team_id``: identification of the team this client application
    #           belongs to.
    #
    #         * ``update_time``: most recent time when some information, such as
    #           the name of the application, or the API keys, has been modified.
    #
    #
    #     :raise DeletedObjectException: if the client application has been
    #        deleted, while the argument ``check_status`` has been set to
    #        ``True``.
    #
    #     :raise DisabledObjectException: if the client application has been
    #        disabled, while the argument ``check_status`` has been set to
    #        ``True``.
    #
    #     :raise UndefinedObjectException: if the specified name doesn't refer
    #        to a client application registered against the platform.
    #     """
    #     with self.acquire_rdbms_connection() as connection:
    #         cursor = connection.execute("""
    #             SELECT app_id,
    #                    app_name,
    #                    package_name,
    #                    picture_id,
    #                    platform,
    #                    consumer_key,
    #                    consumer_secret,
    #                    account_id,
    #                    team_id,
    #                    object_status,
    #                    creation_time,
    #                    update_time
    #               FROM application
    #               WHERE lower(app_name) = %(name)s""",
    #             { 'name': name.strip().lower() })
    #         row = cursor.fetch_one()
    #         if row is None:
    #             raise AccountService.UndefinedObjectException('The client application "%s" is not registered against the platform' % name)
    #         application = row.get_object({
    #                 'account_id': cast.string_to_uuid,
    #                 'app_id': cast.string_to_uuid })
    #
    #         if check_status:
    #             if application.object_status == ObjectStatus.disabled:
    #                 raise ApplicationService.DisabledObjectException('The client application referenced by the specified identification has been deleted')
    #
    #             if application.object_status == ObjectStatus.deleted:
    #                 raise ApplicationService.DeletedObjectException('The client application reference by the specified API key has been disabled')
    #
    #         return application

    # def get_applications(self, app_id, account_id):
    #     """
    #     Return extended information about client applications that the end
    #     user on behalf of this function is called has access to, either as a
    #     developer, either as an administrator.
    #
    #
    #     :param app_id: identification of the client application such as a Web,
    #         a desktop, or a mobile application, that accesses the service.
    #
    #     :param account_id: identification of a user account.
    #
    #
    #     :return: a list of instances containing the following members:
    #
    #         * ``account_id``: identification of the account of the user who
    #           registered this client application.
    #
    #         * ``app_id``: identification of the application.
    #
    #         * ``app_name``: the title of the application.
    #
    #         * ``consumer_key``: a unique string that identifies the API key
    #           tied to the client application.
    #
    #         * ``consumer_secret``: a string kept secret, which is used to
    #           authenticate the API key.
    #
    #         * ``creation_time``: time when the application has been registered.
    #
    #         * ``picture_id``: identification of the logo of the client
    #           application.
    #
    #         * ``object_status``: current status of the application.
    #
    #         * ``package_name``: package name of the family this application belongs
    #           to, if any defined. This allows to group under a same "branding
    #           umbrella" several applications that share the functionalities,
    #           the same users base. For instance, a software product can have a
    #           lite (free) and full (paid) versions on an Android and an iOS
    #           platforms, etc. Grouping applications of a same family allows to
    #           send notification to a user to whatever version(s) and platform(s)
    #           he could use.
    #
    #         * ``platform``: identification of the platform on which the client
    #          application runs (cf. ``ApplicationService.ApplicationPlatform``).
    #
    #         * ``team_id``: identification of the team this client application
    #           belongs to.
    #
    #         * ``update_time``: most recent time when some information, such as
    #           the name of the application, or the API keys, has been modified.
    #
    #
    #     :raise DeletedObjectException: if the user account has been deleted.
    #
    #     :raise DisabledObjectException: if the user account has been disabled.
    #
    #     :raise UndefinedObjectException: if the specified identification
    #         doesn't refer to a user account registered against the platform.
    #     """
    #     AccountService().get_account(account_id, check_status=True)
    #
    #     with self.acquire_rdbms_connection() as connection:
    #         # Retrieve the list of identification of the applications that the
    #         # specified user has access to, either as an individual, either as
    #         # the member of a team.
    #         teams = dict([ (team.team_id, team) for team in
    #               TeamService()._get_all_teams(app_id, account_id) ])
    #
    #         cursor = connection.execute("""
    #             SELECT app_id,
    #                    app_name,
    #                    package_name,
    #                    picture_id,
    #                    platform,
    #                    consumer_key,
    #                    consumer_secret,
    #                    account_id,
    #                    team_id,
    #                    object_status,
    #                    creation_time,
    #                    update_time
    #               FROM application
    #               WHERE app_id IN (
    #                 SELECT app_id
    #                   FROM application
    #                   WHERE account_id = %(account_id)s
    #                     AND team_id IS NULL
    #                 UNION ALL
    #                 SELECT app_id
    #                   FROM application
    #                   WHERE team_id IN (%[team_ids]s))""",
    #             { 'account_id': account_id,
    #               'team_ids': [ team.team_id for team in teams.iterkeys() ] })
    #         applications = [ row.get_object({
    #               'account_id': cast.string_to_uuid,
    #               'app_id': cast.string_to_uuid,
    #               'creation_time': cast.string_to_timestamp,
    #               'update_time': cast.string_to_timestamp })
    #             for row in cursor.fetch_all() ]
    #
    #         for application in applications:
    #             if application.team_id is not None:
    #                 application.team = team[application.team_id]
    #
    #         return applications.values()
