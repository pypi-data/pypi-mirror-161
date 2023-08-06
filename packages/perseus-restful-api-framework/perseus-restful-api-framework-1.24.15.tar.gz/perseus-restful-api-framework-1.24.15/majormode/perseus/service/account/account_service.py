# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Majormode.  All rights reserved.
#
# This software is the confidential and proprietary information of
# Majormode or one of its subsidiaries.  You shall not disclose this
# confidential information and shall use it only in accordance with the
# terms of the license agreement or other applicable agreement you
# entered into with Majormode.
#
# MAJORMODE MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY
# OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT.  MAJORMODE SHALL NOT BE LIABLE FOR ANY
# LOSSES OR DAMAGES SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING
# OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

import collections
import hashlib
import io
import logging
import os
import random
import re
import secrets
import string
import traceback
import unidecode
import uuid

from majormode.perseus.constant.account import AccountType
from majormode.perseus.constant.contact import ContactName
from majormode.perseus.constant.obj import ObjectStatus
from majormode.perseus.constant.regex import REGEX_PATTERN_EMAIL_ADDRESS
from majormode.perseus.model.contact import Contact
from majormode.perseus.model.enum import Enum
from majormode.perseus.model.locale import DEFAULT_LOCALE
from majormode.perseus.model.locale import Locale
from majormode.perseus.model.obj import Object
from majormode.perseus.service.base_rdbms_service import RdbmsConnection
from majormode.perseus.utils import cast
from majormode.perseus.utils import file_util
from majormode.perseus.utils import image_util
from majormode.perseus.utils.date_util import ISO8601DateTime
from majormode import prosoponym

from majormode.perseus.service.account.contact_service import ContactService
from majormode.perseus.service.account.session_service import SessionService
from majormode.perseus.service.base_rdbms_service import BaseRdbmsService
from majormode.perseus.service.base_service import BaseService

import settings


# Default file extensions per image file format.  When not defined, the
# file extension is named after the image file format.
DEFAULT_IMAGE_FILE_FORMAT_EXTENSIONS = {
    'JPEG': 'jpg'
}


class AccountService(BaseRdbmsService):
    """
    A user's account allows a user to authenticate to the platform and be
    granted authorization to access them; however, authentication does not
    imply authorization.  To log in to an account, a user is typically
    required to authenticate oneself with a password or other credentials
    for the purposes of accounting, security, logging, and resource
    management.  Once the user has logged on, the platform uses an
    identifier to refer to him, rather than his email address or his
    username, through a process known as identity correlation.
    """
    class AuthenticationFailureException(BaseService.IllegalAccessException):
        """
        Signal that the email address or password passed to authenticate a
        user is incorrect
        """

    class PictureSizeTooSmallException(BaseService.BaseServiceException):
        """
        Signal that a new photo of an account is too small
        """

    class UnverifiedContactException(BaseService.BaseServiceException):
        """
        Signal that the user's contact information has not been verified
        """

    class UsernameAlreadyUsedException(BaseService.InvalidOperationException):
        """
        Signal that a username is already used
        """

    # Define the name of the Content Delivery Network (CDN) bucket that
    # groups user avatars all together.
    CDN_BUCKET_NAME_PICTURE = 'avatar'

    # Default image file format to store the picture of an account with
    # (cf. https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).
    DEFAULT_IMAGE_FILE_FORMAT = 'JPEG'

    # Default quality to store the image with, on a scale from `1` (worst)
    # to `95` (best).  Values above `95` should be avoided; `100` disables
    # portions of the JPEG compression algorithm, and results in large files
    # with hardly any gain in image quality.
    DEFAULT_IMAGE_QUALITY = 75

    # Duration in seconds a password reset request lives before it expires.
    DEFAULT_PASSWORD_RESET_REQUEST_LIFESPAN = 60 * 5  # 5 minutes

    # Default minimal size of the photo of an account.
    DEFAULT_PICTURE_MINIMAL_SIZE = (400, 400)

    NONCE_DEFAULT_DIGIT_COUNT = 6

    # Maximum number of digits that composed a nonce used to reset the
    # password of a user.
    NONCE_MAXIMUM_DIGIT_COUNT = 9

    # Minimal number of characters that composes a password.
    MINIMUM_PASSWORD_LENGTH = 8

    # Define the minimal allowed duration of time, expressed in seconds,
    # between two consecutive requests of a same user to reset his
    # forgotten password.
    MINIMAL_TIME_BETWEEN_PASSWORD_RESET_REQUEST = 60 * 5

    # Regular expression to whether a password complies with the following
    # complexity requirements:
    #
    # - Be at least eight characters
    # - Contain at least one number (0-9)
    # - Contain at least one uppercase letter (A-Z)
    # - Contain at least one lowercase letter (a-z)
    # - Contain at least one symbol character (i.e., other than alphanumeric
    #   character)
    REGEX_PASSWORD_COMPLEXITY_REQUIREMENTS = re.compile(r'/^(?=.{8,}$)(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*\W).*$')

    def __add_picture(
            self,
            app_id,
            account_id,
            submitter_account_id,
            image,
            image_file_checksum,
            image_file_size,
            connection=None,
            is_review_required=False,
            team_id=None):
        """
        Add a new picture

        The function stores the image file in the NFS storage.


        @param app_id: The identification of the client application such as a
            Web, a desktop, or a mobile application, that accesses the service.

        @param account_id: The identification of the account of the user who
            is associated to this picture.

        @param submitter_account_id: The identification of the account of the
            user who submitted this picture.

        @param image: An object `PIL.Image`.

        @param image_file_checksum: Message digest of the the binary data of
            the user's original photo image file.

        @param image_file_size: Size in bytes of the user's original photo
            image file.

        @param connection: An object `RdbmsConnection` with auto-commit.

        @param is_review_required: Indicate whether the picture needs to be
            reviewed by someone who has authority on the online service used
            by the end users.

        @param team_id: The identification of the organization of the user who
            submitted this picture.


        @return: An object containing the following attributes:

            * `account_id` (required): The identification of the account of the user
              this picture is associated with.

            * `picture_id` (required): The identification of the new picture.

            * `object_status` (required): An item of the enumeration `ObjectStatus`
              representing the current status of the picture.

            * `update_time` (required): The time of the most recent modification of
              the picture's status.
        """
        picture_id = uuid.uuid4()
        image_width, image_height = image.size

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            cursor = connection.execute(
                """
                INSERT INTO account_picture (
                    app_id,
                    account_id,
                    image_file_checksum,
                    image_file_size,
                    image_height,   
                    image_width,
                    is_review_required,
                    picture_id,
                    submitter_account_id,
                    team_id
                  )
                  VALUES (
                    %(app_id)s,
                    %(account_id)s,
                    %(image_file_checksum)s,
                    %(image_file_size)s,
                    %(image_height)s,   
                    %(image_width)s,
                    %(is_review_required)s,
                    %(picture_id)s,
                    %(submitter_account_id)s,
                    %(team_id)s
                  )
                  RETURNING
                    account_id,
                    object_status,
                    picture_id,
                    update_time
                """,
                {
                    'account_id': account_id,
                    'app_id': app_id,
                    'image_file_checksum': image_file_checksum,
                    'image_file_size': image_file_size,
                    'image_height': image_height,
                    'image_width': image_width,
                    'is_review_required': is_review_required,
                    'picture_id': picture_id,
                    'submitter_account_id': submitter_account_id,
                    'team_id': team_id,
                }
            )

            row = cursor.fetch_one()
            picture = row.get_object({
                'account_id': cast.string_to_uuid,
                'object_status': ObjectStatus,
                'picture_id': cast.string_to_uuid,
                'update_time': cast.string_to_timestamp,
            })

            self.__store_picture_image_file(picture_id, image)

            return picture

    @staticmethod
    def __cleanse_keywords(keywords):
        """
        Remove any punctuation character from the specified list of keywords,
        remove any double or more space character and represent Unicode
        characters in ASCII.


        @param keywords: a list of keywords strip out any punctuation characters.


        @return: the set of keywords cleansed from any special Unicode
            accentuated character, punctuation character, and double space
            character.
        """
        if not isinstance(keywords, (list, set, tuple)):
            keywords = [keywords]

        # Normalize the given keywords and split them into sub-keywords if
        # needed.  For instance:
        #
        #   [ u'Saint-Élie-de-Caxton', u'Québec' ]
        #
        # becomes:
        #
        #   [ [ u'saint', u'elie', u'de', u'caxton' ], [ u'Québec' ]]
        sub_keywords_list = [
            re.sub(                                         # 3. Remove any double space character
                r'\s{2,}',
                ' ',
                re.sub(                                     # 2. Remove any punctuation character
                    r"""[.,\\/#!$%\^&*;:{}=\-_`~()<>"']""",
                    ' ',
                    unidecode.unidecode(keyword).lower()))  # 1. Convert to ASCII characters
            .split(' ')                                     # 4. Split sub-keywords
            for keyword in keywords]

        # Merge all the sub-keywords in a single list.
        cleansed_keywords = set()
        map(lambda sub_keywords: cleansed_keywords.update(sub_keywords), sub_keywords_list)

        # Filter out sub-keywords of less than 2 characters.
        return [ keyword for keyword in cleansed_keywords if len(keyword) > 2 ]

    @classmethod
    def __convert_uploaded_photo_file_to_image(cls, uploaded_file):
        """
        Convert an uploaded photo file to an image


        @param uploaded_file: An object `HttpRequest.HttpRequestUploadedFile`.


        @return: An object `PIL.Image`.


        @raise InvalidOperationException: If the uploaded file has not a
            supported format.
        """
        # Retrieve the pixel resolution of the photo image, and check whether
        # it respects the minimal size required.  If not, ignore this photo.
        try:
            string_io_stream = io.BytesIO(uploaded_file.data)
            image = image_util.convert_image_to_rgb_mode(
                image_util.open_and_reorient_image(string_io_stream))
        except Exception as exception:
            logging.error(exception)
            raise cls.InvalidOperationException("Unsupported image file format")

        return image

    @classmethod
    def __encrypt_password(cls, password):
        """
        Return the encrypted version of a password.


        @param password: A password.


        @return: The encrypted password.
        """
        password = password.strip()
        encrypted_password = hashlib.md5(password.encode()).hexdigest()
        return encrypted_password

    @staticmethod
    def __generate_nonce(digit_count):
        """
        Generate a string composed of the requested number of digits


        @param digit_count: Number of digit to generate.


        @return: A string composed of the request number of digits.
        """
        return ''.join([
            str(random.randint(0, 9))
            for _ in range(digit_count)
        ])

    @classmethod
    def __generate_password(cls, length=8, are_symbols_allowed=False):
        """
        Generate a password


        @param length: Number of characters that composes the password to be
            generated.

        @param are_symbols_allowed: Indicate whether the password can
            contain punctuation characters.


        @return: A string representing a password randomly generated.
        """
        alphabet = string.ascii_letters + string.digits
        if are_symbols_allowed:
            alphabet += cls.PASSWORD_ALLOWED_SYMBOL_CHARACTERS

        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    def __get_password_reset_request(
            self,
            app_id,
            check_app=False,
            connection=None,
            contact=None,
            nonce=None,
            request_id=None):
        """
        Return extended information about a password reset request


        @param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        @param check_app: indicate whether the function must check if the
            client application on behalf of which the function is called is
            the same than the client application that requested the password
            reset of the user's account.

        @param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...`.

        @param contact: An object `Contact` corresponding to an email address
            or a mobile phone number where a random number (nonce) has been
            sent to for verifying the password reset request.  The argument
            `nonce` is also required.

        @param nonce: "Number used once", a pseudo-random number issued when
            generating the request to allow the user to change his password
            through a mobile application.  The argument `account_id` is
            required.

        @param request_id: Identification of the request of the user to reset
             his forgotten password (cf. function `request_password_reset`).


        @return: An instance containing the following members:

            * `account_id` (required): identification of the user's account
              which the user has requested to reset his password.

            * `app_id` (required): identification of the client application that
              submitted on behalf of the user the request to reset the password
              of his account.

            * `attempt_count` (required): number of times the platform sent an
              email to the user with an embedded link to let this user reset his
              password.

            * `creation_time` (required): time when the user requested to reset
              the password of his account.

            * `request_count` (required): number of times the user requested to
              reset his password before he finally changed it.

            * `request_id` (required): identification of this password reset
              request.

            * `update_time` (required): the most recent time when the platform
              sent an email to the user with an embedded link to let this user
              reset his password.


        @raise `DeletedObjectException`: if the specified password reset
            request has been cancelled by the user or if this request has
            expired.

        @raise `DisabledObjectException`: if the specified password reset
            request has been already used by the user to reset the password
            of his account.

        @raise `IllegalAccessException`: if the client application or the
            user account, on behalf of this function is called, is not allowed
            to retrieve the information of this password reset request.

        @raise `UndefinedObjectException`: if the specified password reset
            request has not been registered on the platform.
        """
        if contact is None and request_id is None:
            raise ValueError("A password reset request or a contact information MUST be passed")

        if contact and nonce is None:
            raise ValueError("A nonce MUST be passed")

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            account = self.get_account_by_contact(
                contact,
                check_status=True,
                connection=connection)

            # Retrieve extended information about this password reset request.
            cursor = connection.execute(
                """
                SELECT 
                    account_id,
                    app_id,
                    attempt_count,
                    creation_time,
                    expiration_time,
                    object_status,
                    request_id,
                    request_count,
                    update_time
                  FROM
                    account_password_reset
                  WHERE
                    ((%(request_id)s IS NOT NULL AND request_id = %(request_id)s)
                     OR (%(property_name)s IS NOT NULL 
                         AND property_name = %(property_name)s
                         AND property_value = %(property_value)s
                         AND nonce = %(nonce)s))
                    AND object_status = %(OBJECT_STATUS_ENABLED)s 
                """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'property_name': contact.property_name,
                    'property_value': contact.property_value,
                    'nonce': nonce,
                    'request_id': request_id,
                })

            row = cursor.fetch_one()
            if row is None:
                raise self.UndefinedObjectException("No password reset request found for the specified criteria")

            request = row.get_object({
                'account_id': cast.string_to_uuid,
                'creation_time': cast.string_to_timestamp,
                'expiration_time': cast.string_to_timestamp,
                'request_id': cast.string_to_uuid,
                'update_time': cast.string_to_timestamp
            })

            # Check whether this password reset request didn't expire, and if so,
            # update its current status.
            if ISO8601DateTime.now() >= request.expiration_time:
                connection.execute(
                    """
                    UPDATE 
                        account_password_reset
                      SET
                        object_status = %(OBJECT_STATUS_DISABLED)s,
                        update_time = current_timestamp
                      WHERE
                        request_id = %(request_id)s
                    """,
                    {
                        'OBJECT_STATUS_DISABLED': ObjectStatus.disabled,
                        'request_id': request.request_id
                    })

                connection.commit()  # Commit the update before raising the exception.

                raise self.DisabledObjectException("This password reset request has expired")

            if account.account_id and request.account_id != account.account_id:
                raise self.IllegalAccessException("This password reset request doesn't belong to the specified user")

            if check_app and request.app_id != app_id:
                raise self.IllegalAccessException(
                    "This password reset request hasn't been initiated by this client application")

            return request

    def __get_picture(
            self,
            picture_id,
            check_status=False,
            connection=None):
        """
        Return a picture


        @param picture_id: The identification of the picture.

        @param check_status: Indicate whether to check the current status of
            the picture.

        @param connection: An object `RdbmsConnection`.


        @return: An object containing the following attributes:

            * `account_id` (required): The identification of the user account that
              the picture is associated with.

            * `creation_time` (required): The time when this photo has been
              registered to the platform

            * `image_file_checksum` (required): The message digest of the the binary
              data of the user's original photo image file.

            * `image_file_size` (required): The size in bytes of the user's original
                photo image file.

            * `image_height` (required): The number of pixel rows of the user's
              original photo image.

            * `image_width` (required): The number of pixel columns of the user's
              original photo image.

            * `is_review_required` (required): Indicate whether the picture needs to
              be reviewed by someone who has authority on the online service.

            * `object_status` (required): The current status of the picture.

            * `picture_id` (required): The identification of the picture.

            * `submitter_account_id` (required): The identification of the account
              of the user who submitted this picture.

            * `team_id` (required): The identification of the organization of the
              user who submitted this picture.

            * `update_time` (required): The time of the most recent modification of
              the status of this picture.
        """
        with self.acquire_rdbms_connection(connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT
                    account_id,
                    creation_time,
                    image_file_checksum,
                    image_file_size,
                    image_height,
                    image_width,
                    is_review_required,
                    object_status,
                    picture_id,
                    submitter_account_id,
                    team_id,
                    update_time
                  FROM
                    account_picture
                  WHERE
                    picture_id = %(picture_id)s
                """,
                {
                    'picture_id': picture_id,
                }
            )

            row = cursor.fetch_one()
            if row is None:
                raise self.UndefinedObjectException(f"The picture {picture_id} doesn't exist")

            picture = row.get_object({
                'account_id': cast.string_to_uuid,
                'creation_time': cast.string_to_timestamp,
                'object_status': ObjectStatus,
                'picture_id': cast.string_to_uuid,
                'submitter_account_id': cast.string_to_uuid,
                'team_id': cast.string_to_uuid,
                'update_time': cast.string_to_timestamp,
            })

            if check_status:
                if picture.object_status == ObjectStatus.deleted:
                    raise self.DeletedObjectException(f"The picture {picture_id} has been deleted")
                elif picture.object_status == ObjectStatus.disabled:
                    raise self.DisabledObjectException(f"The picture {picture_id} has been disabled")

            return picture

    def __index_account(
            self,
            account_id,
            full_name,
            connection=None):
        """
        Index the account of a user with the personal name by which this user
        is known.


        @param account_id: identification of the account of this child.

        @param full_name: Personal name by which this user is known.

        @param connection: An object `RdbmsConnection` with auto commit.
        """
        keywords = self.__string_to_keywords(full_name)

        if keywords:
            with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
                connection.execute(
                    """
                    DELETE FROM 
                        account_index
                      WHERE 
                        account_id = %(account_id)s
                    """,
                    {
                        'account_id': account_id
                    })

                connection.execute(
                    """
                    INSERT INTO account_index(
                        account_id,
                        keyword)
                      VALUES 
                        %[values]s
                    """,
                    {
                        'values': [
                            (account_id, keyword)
                            for keyword in keywords
                        ]
                    })

    def __is_password_correct(
            self,
            account_id,
            password,
            connection=None):
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT
                    true
                  FROM
                    account
                  WHERE
                    account_id = %(account_id)s
                    AND password = %(password)s
                """,
                {
                    'account_id': account_id,
                    'password': self.__encrypt_password(password),
                }
            )

            return cursor.get_row_count() == 1

    def __set_picture_status(
            self,
            picture_id,
            status,
            connection=None):
        """
        Set the current status of a picture


        @param picture_id: The identification of a picture.

        @param status: An item of the enumeration `ObjectStatus`
            representing the new status of the picture.

        @param connection: An object `RdbmsConnection` with auto-commit.


        @return: An object containing the following attributes:

            * `account_id` (required): The identification of the account of the user
              this picture is associated with.

            * `picture_id` (required): The identification of the new picture.

            * `object_status` (required): An item of the enumeration `ObjectStatus`
              representing the current status of the picture.

            * `update_time` (required): The time of the most recent modification of
              the picture's status.


        @raise DeletedObjectException: If the picture has been deleted.

        @raise UndefinedObjectException: If the picture doesn't not exist.
        """
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            picture = self.__get_picture(picture_id, check_status=False, connection=connection)
            if picture.object_status == status:
                return
            elif picture.object_status == ObjectStatus.deleted:
                raise self.DeletedObjectException(f"The picture {picture_id} has been deleted")

            # Update the current status of the picture.
            cursor = connection.execute(
                """
                UPDATE 
                    account_picture
                  SET 
                    object_status = %(object_status)s,
                    update_time = current_timestamp
                  WHERE
                    picture_id = %(picture_id)s
                  RETURNING
                    account_id,
                    object_status,
                    picture_id,
                    update_time
                """,
                {
                    'object_status': status,
                    'picture_id': picture_id
                }
            )

            row = cursor.fetch_one()
            picture = row.get_object({
                'account_id': cast.string_to_uuid,
                'object_status': ObjectStatus,
                'picture_id': cast.string_to_uuid,
                'update_time': cast.string_to_timestamp
            })

            # If this picture is enabled, set this picture has active for the user
            # and disabled the previous active picture of the user.
            if status == ObjectStatus.enabled:
                connection.execute(
                    """
                    UPDATE 
                        account
                      SET 
                        picture_id = %(picture_id)s,
                        update_time = current_timestamp
                      WHERE
                        account_id = %(account_id)s
                    """,
                    {
                        'account_id': picture.account_id,
                        'picture_id': picture_id,
                    })

                connection.execute(
                    """
                    UPDATE 
                        account_picture
                      SET 
                        object_status = %(OBJECT_STATUS_DISABLED)s,
                        update_time = current_timestamp
                      WHERE
                        account_id = %(account_id)s
                        AND picture_id <> %(picture_id)s
                        AND object_status = %(OBJECT_STATUS_ENABLED)s
                    """,
                    {
                        'OBJECT_STATUS_DISABLED': ObjectStatus.disabled,
                        'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                        'account_id': picture.account_id,
                        'picture_id': picture_id,
                    })

            # If this picture is deleted or disabled, disable the active picture
            # for the user.
            elif status in (ObjectStatus.deleted, ObjectStatus.disabled):
                connection.execute(
                    """
                    UPDATE 
                        account
                      SET 
                        picture_id = NULL,
                        update_time = current_timestamp
                      WHERE
                        account_id = %(account_id)s
                    """,
                    {
                        'account_id': picture.account_id,
                    })

            return picture

    def __sign_in(
            self,
            app_id,
            account_id,
            password,
            connection=None,
            include_contacts=False,
            session_duration=None):
        """

        @param app_id:
        @param account_id:
        @param password:
        @param connection:
        @param include_contacts:
        @param session_duration:
        @return:
        """
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            if not self.__is_password_correct(account_id, password, connection=connection):
                raise self.AuthenticationFailureException()

            account = self.get_account(
                account_id,
                check_status=True,
                connection=connection,
                include_contacts=include_contacts)

            self.__update_last_login_time(account.account_id, connection)

            session = SessionService().create_session(
                app_id,
                account.account_id,
                connection=connection,
                session_duration=session_duration)

            session.merge(account)

        return session

    @classmethod
    def __store_picture_image_file(
            cls,
            picture_id,
            image,
            image_file_format=DEFAULT_IMAGE_FILE_FORMAT,
            image_quality=DEFAULT_IMAGE_QUALITY):
        """
        Store the image data of the avatar/photo of an account to the temporary
        directory of the local Network File System (NFS).  This file will be
        read by background tasks for additional processing.


        @param picture_id: The identification of the photo of a user account.

        @param image: An object `PIL.Image`.

        @param image_file_format: Image file format to store the image with
            (cf. https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).

        @param image_quality: The image quality to store locally, on a scale from `1`
            (worst) to `95` (best).  Values above `95` should be avoided; `100`
            disables portions of the JPEG compression algorithm, and results
            in large files with hardly any gain in image quality.


        @return: The absolute file path name of the photo image stored in the
            local Network File System (NFS)
        """
        # Create the path of the folder to store the image file in.
        path = os.path.join(
            settings.CDN_NFS_ROOT_PATH,
            cls.CDN_BUCKET_NAME_PICTURE,
            file_util.build_tree_pathname(str(picture_id)))

        file_util.make_directory_if_not_exists(path)

        # Define the name and the extension of the image file to create.
        if not image_file_format:
            image_file_format = cls.DEFAULT_IMAGE_FILE_FORMAT

        file_extension = DEFAULT_IMAGE_FILE_FORMAT_EXTENSIONS.get(image_file_format, image_file_format)
        file_path_name = os.path.join(path, f'{str(picture_id)}.{file_extension}')

        # Save the image with the specified format in its folder.
        image.save(
            file_path_name,
            format=cls.DEFAULT_IMAGE_FILE_FORMAT,
            quality=image_quality or cls.DEFAULT_IMAGE_QUALITY)

        return file_path_name

    @staticmethod
    def __string_to_keywords(s, keyword_minimal_length=1):
        """
        Remove any punctuation character from the specified list of keywords,
        remove any double or more space character and represent Unicode
        characters in ASCII.


        @param s: a list of keywords strip out any punctuation characters.

        @param keyword_minimal_length: minimal number of characters of the
            keywords to be returned.


        @return: the set of keywords cleansed from any special Unicode
            accentuated character, punctuation character, and double space
            character.
        """
        if not s:
            return

        # Convert the string to ASCII lower characters.
        ascii_string = unidecode.unidecode(s).lower()

        # Replace any punctuation character with space.
        punctuationless_string = re.sub(r"""[.,\\/#!$%\^&*;:{}=\-_`~()<>"']""", ' ', ascii_string)

        # Remove any double space character.
        cleansed_string = re.sub(r'\s{2,}', ' ', punctuationless_string)

        # Decompose the string into distinct keywords.
        keywords = set(cleansed_string.split(' '))

        # Filter out sub-keywords of less than 2 characters.
        return [keyword for keyword in keywords if len(keyword) > keyword_minimal_length]

    def __update_last_login_time(self, account_id, connection=None):
        """
        Update the last login time of a user.


        @param account_id: Identification of the user's account.

        @param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...`.
        """
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            connection.execute(
                """
                UPDATE
                    account
                  SET
                    last_login_time = current_timestamp
                  WHERE
                    account_id = %(account_id)s
                """,
                {
                    'account_id': account_id
                })

    @classmethod
    def __validate_image_size(cls, image, minimal_size):
        """
        Validate the resolution of a new photo of an account


        @param image: An object `PIL.Image`.

        @param minimal_size: A tuple of two integers `(width, height)`
            representing the minimal size of the image of a photo.


        @raise PictureSizeTooSmallException: If the photo is too small.
        """
        image_width, image_height = image.size
        min_width, min_height = minimal_size

        if (image_width < min_width and image_height < min_height) or \
           (image_width < min_height and image_height < min_width):
            raise cls.PictureSizeTooSmallException(f"Image is too small: minimal size is {min_width}x{min_height}")

    @classmethod
    def __validate_password_complexity_requirements(cls, password):
        """
        Check whether a new password meets the complexity requirements.


        @param password: A password.


        @raise InvalidArgumentException: If the new password doesn't meet
            the complexity requirements {@link
            AccountService.REGEX_PASSWORD_COMPLEXITY_REQUIREMENTS}.
        """
        if not cls.REGEX_PASSWORD_COMPLEXITY_REQUIREMENTS.match(password):
            raise cls.InvalidArgumentException("The password doesn't meet complexity requirements")

    def assert_password_reset_request_nonce_valid(
            self,
            contact,
            nonce=None,
            connection=None,
            request_id=None):
        """
        Check whether a password reset request exists and has not expired


        @param contact: An object `Contact` representing a contact of the user
            who is requesting to reset his forgotten password.

        @param nonce: A nonce ("number used once") composed of digits that has
            been generated when the user requested to reset his password.

        @param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...:`.

        @param request_id: Identification of a password reset request.


        @return: An object containing the following attributes:

            * `expiration_time` (required): The time when this password reset
              request will expire.

            * `object_status` required): The current status of this password reset
              request.


        @raise DisabledObjectException: If the password reset request has
            expired.

        @raise IllegalAccessException: If the nonce or the password reset
            request identification passed to the function is not valid.

        @raise UndefinedObjectException: If the password reset request doesn't
            exist.  It may be an expired request that has been deleted.

        @raise ValueError: If both the argument `nonce` and `request_id` have
            not been passed to this function.
        """
        if not nonce and not request_id:
            raise ValueError("A nonce or request identification MUST be passed")

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    expiration_time,
                    nonce,
                    object_status,
                    request_id
                  FROM
                    account_password_reset
                  WHERE
                    property_name = %(property_name)s
                    AND property_value = %(property_value)s
                """,
                {
                    'property_name': contact.property_name,
                    'property_value': contact.property_value
                }
            )

            requests = [
                row.get_object({
                    'expiration_time': cast.string_to_timestamp,
                    'object_status': ObjectStatus,
                    'request_id': cast.string_to_uuid,
                })
                for row in cursor.fetch_all()
            ]

            # Check that a password reset request exists for the user's contact
            # information.
            if not requests:
                raise self.UndefinedObjectException("The password reset request doesn't not exist")

            # Check whether the nonce or the request identification passed to the
            # function is valid.
            for request in requests:
                if request.nonce == nonce or request.request_id == request_id:
                    break
            else:
                raise self.IllegalAccessException("Invalid nonce or password reset request identification")

            # Delete the request if it has expired.
            has_request_expired = \
                request.object_status != ObjectStatus.enabled \
                or ISO8601DateTime.now() > request.expiration_time

            if has_request_expired and request.object_status == ObjectStatus.enabled:
                self.update_password_reset_request(
                    request.request_id,
                    connection=connection,
                    object_status=ObjectStatus.disabled)

        # Raise an exception if this request has expired.
        #
        # @note: The exception MUST be raised outside the database connection
        #     statement context manager, otherwise that would rollback the
        #     current transaction (cf. `__delete_password_reset_request`).
        if has_request_expired:
            raise self.DisabledObjectException('This password reset request has expired')

        # Remove security information from the object to return to the caller.
        del request.request_id
        del request.nonce

        return request

    @classmethod
    def build_picture_url(cls, picture_id):
        """
        Return the Uniform Resource Locator of an account's picture.


        @param picture_id: Identification of the picture of an account.


        @return: A string representing the Uniform Resource Locator of the
            picture.
        """
        return picture_id and os.path.join(
            settings.CDN_URL_HOSTNAME,
            cls.CDN_BUCKET_NAME_PICTURE,
            str(picture_id))

    def change_password(
            self,
            app_id,
            account_id,
            old_password,
            new_password,
            connection=None):
        """
        Change the password of a user's account with a new password

        The new password must respect the rules of definition of a password.
        It cannot be identical to the old password.  It cannot contains part
        of the email address of the user.


        @param app_id: identification of the client application such as a Web,
           a desktop, or a mobile application, that accesses the service.

        @param account_id: identification of the account of the user who is
           changing his password.

        @param old_password: old password of the user's account.

        @param new_password: new password of this user's account.

        @param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...`.


        @raise DeletedObjectException: If the user's account has been deleted.

        @raise DisabledObjectException: If the user's account has been
            disabled.

        @raise IllegalAccessException: If the old password that is passed to
            the function doesn't match the current password of the user's
            account.

        @raise InvalidArgumentException: If the new password doesn't conform
           to the rules of password definition, if the new  password is
           identical to the old password of the user.

        @raise UndefinedObjectException: If the user's account doesn't exist.
        """
        # Encrypt both the old password and the new password passed to the
        # function.
        encrypted_old_password = self.__encrypt_password(old_password)
        self.__validate_password_complexity_requirements(new_password)
        encrypted_new_password = self.__encrypt_password(new_password)

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            # Check the status of the user's account.
            self.get_account(account_id, check_status=True, connection=connection)

            # Retrieve the encrypted version of the old password of the user's
            # account.
            cursor = connection.execute(
                """
                SELECT 
                    password
                  FROM 
                    account
                  WHERE 
                    account_id = %(account_id)s
                  FOR UPDATE
                """,
                {
                    'account_id': account_id
                })

            encrypted_current_password = cursor.fetch_one().get_value('password')

            # Check whether the old password passed to this function matches the
            # old password of the user's account.
            if encrypted_current_password != encrypted_old_password:
                raise self.IllegalAccessException("The specified old password doesn't match the user's current password")

            # Check that the new password is not identical to the current password
            # of the user's account.
            if encrypted_current_password == encrypted_new_password:
                raise self.InvalidArgumentException("The new password cannot be identical to the previous password")

            # Update the password of the user's account.
            connection.execute(
                """
                UPDATE account
                  SET 
                    password = %(encrypted_new_password)s,
                    update_time = current_timestamp
                  WHERE
                    account_id = %(account_id)s
                """,
                {
                    'account_id': account_id,
                    'encrypted_new_password': encrypted_new_password,
                })

    def delete_account(
            self,
            account_id,
            connection=None,
            hard_delete=False):
        """
        Delete the account of user


        @param account_id: Identification of a user account.

        @param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...`.

        @param hard_delete: Indicate whether to do a hard-delete of this
            account, i.e, completely removing its record. By default, the
            function performs a soft-delete, marking this account has
            deleted.
        """
        with self.acquire_rdbms_connection(
                auto_commit=True,
                connection=connection) as connection:
            if hard_delete:
                # @note: Deleting the account's record from the root table `account`
                #     automatically delete this record from the inherited table.
                connection.execute(
                    """
                    DELETE FROM 
                        account
                      WHERE
                        account_id = %(account_id)s
                    """,
                    {
                        'account_id': account_id
                    })
            else:
                connection.execute(
                    """
                    UPDATE 
                        account
                      SET
                        object_status= %(OBJECT_STATUS_DELETED)s,
                        update_time = current_timestamp
                      WHERE
                        account_id = %(account_id)s
                    """,
                    {
                        'OBJECT_STATUS_DELETED': ObjectStatus.deleted,
                        'account_id': account_id
                    })

    def find_picture(
            self,
            image_file_size,
            image_file_checksum,
            connection=None):
        """
        Return a picture corresponding to the specified file size and checksum.


        @param image_file_size: The size in bytes of the user's original photo
            image file.

        @param image_file_checksum: The message digest of the the binary data
            of the user's original photo image file.

        @param connection: An object `RdbmsConnection`.


        @return: An object containing the following attributes:

            * `account_id` (required): The identification of the user account that
              the picture is associated with.

            * `image_height` (required): Number of pixel rows of the user's
              original photo image.

            * `image_width`  (required): Number of pixel columns of the user's
              original photo image.

            * `object_status`: (required): An item of the enumeration `ObjectStatus`
              that indicates the current status of this picture.

            * `picture_id`: (required): The identification of the picture.

            * `submitter_account_id` (required): The identification of the account
              of the user who submitted this picture.

            * `team_id` (required): The identification of the organization of the
              user who submitted this picture.

            * `update_time` (required): Time of the most recent modification of the
              status of this picture.
        """
        with self.acquire_rdbms_connection(connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT
                    account_id,
                    image_height,
                    image_width,
                    object_status,
                    picture_id,
                    submitter_account_id,
                    team_id,
                    update_time  
                  FROM
                    account_picture
                  WHERE
                    image_file_size = %(image_file_size)s
                    AND image_file_checksum = %(image_file_checksum)s
                    AND object_status <> %(OBJECT_STATUS_DELETED)s
                """,
                {
                    'OBJECT_STATUS_DELETED': ObjectStatus.deleted,
                    'image_file_checksum': image_file_checksum,
                    'image_file_size': image_file_size,
                }
            )

            row = cursor.fetch_one()
            picture = row and row.get_object({
                'account_id': cast.string_to_uuid,
                'object_status': ObjectStatus,
                'picture_id': cast.string_to_uuid,
                'submitter_account_id': cast.string_to_uuid,
                'team_id': cast.string_to_uuid,
                'update_time': cast.string_to_timestamp,
            })

            return picture

    def get_account(
            self,
            account_id,
            check_status=False,
            connection=None,
            include_contacts=False):
        """
        Return extended information about a user account specified by its
        identification.

        @warning: this function is for internal usage only; it MUST not be
            surfaced to client applications.


        @param account_id: identification of the user account that is
            requested its information.

        @param check_status: indicate whether the function must check the
            current status of this user account and raise an exception if it
            is not of enabled.

        @param include_contacts: indicate whether to include the contacts
            information of this user account.

        @param connection: a `RdbmsConnection` instance to be used
            supporting the Python clause `with ...:`.


        @return: an instance containing the following members:

             * `account_id`: identification of the user account.

             * `account_type`: type of the user account as defined in the
               enumeration `AccountType`.

             * `contacts` (optional): list of properties such as e-mail
                addresses, phone numbers, etc., in respect of the electronic
                business card specification (vCard).  The contact information
                is represented by a list of tuples of the following form::

                   (name:Contact.ContactName, value:string, is_primary:boolean, is_verified:boolean)

                where:

                * `name`: type of this contact information, which can be one
                  of these standard names in respect of the electronic
                  business card specification (vCard).

                * `value`: value of this contact information representing by
                  a string, such as `+84.01272170781`, the formatted value
                  for a telephone number property.

                * `is_primary`: indicate whether this contact information is
                  the primary.

                * `is_verified`: indicate whether this contact information
                  has been verified, whether it has been grabbed from a
                  trusted Social Networking Service (SNS), or whether through
                  a challenge/response process.

             * `creation_time`: time when this user account has been
               registered against the platform.  This attribute is returned
               only if the user on behalf of whom this function is called is
               the owner of this account or connected with this user.

             * `full_name`: full name of the user.

             * `language`: a `Locale` instance that identifies the preferred
               language of the user, or English by default.

            * `object_status`: An item of the enumeration `ObjectStatus`
              representing thr current status of this user account.

             * `picture_id`: identification of the user account's picture,
               if any picture defined for this user account.

             * `picture_url`: Uniform Resource Locator (URL) that specifies
               the location of the user account's picture, if any defined.
               The client application can use this URL and append the query
               parameter `size` to specify a given pixel resolution of the
               user account's picture, such as `thumbnail`, `small`,
               `medium`, `large` (cf. `settings.IMAGE_PIXEL_RESOLUTIONS['avatar']`).

             * `timezone`: time zone of the default location of the user.
               It is the difference between the time at this location and UTC
               (Universal Time Coordinated).  UTC is also  known as GMT or
               Greenwich Mean Time or Zulu Time.

             * `update_time`: time when the information of this user account
               has been updated for the last time.

             * `username`: a name used to gain access to a the platform.


        @raise DeletedObjectException: if the user account has been deleted
            while the argument `check_status` has been set to `True`.

        @raise DisabledObjectException: if the user account has been disabled
            while the argument `check_status` has been set to `True`.

        @raise UndefinedObjectException: if the specified identification
            doesn't refer to a user account registered against the platform.
        """
        with self.acquire_rdbms_connection(
                auto_commit=False,
                connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT
                    account_id,
                    account_type,
                    creation_time,
                    first_name,
                    full_name,
                    last_name,
                    language,
                    nationality,
                    object_status,
                    picture_id,
                    timezone,
                    update_time,
                    username
                  FROM
                    account
                  WHERE
                    account_id = %(account_id)s
                """,
                {
                    'account_id': account_id
                })
            row = cursor.fetch_one()
            if row is None:
                raise self.UndefinedObjectException(
                    f"The account {account_id} is not registered to the platform",
                    payload={'account_id': account_id})

            account = row.get_object({
                'account_id': cast.string_to_uuid,
                'account_type': AccountType,
                'creation_time': cast.string_to_timestamp,
                'language': cast.string_to_locale,
                'object_status': ObjectStatus,
                'update_time': cast.string_to_timestamp
            })

            if check_status:
                if account.object_status == ObjectStatus.disabled:
                    raise self.DisabledObjectException()
                elif account.object_status == ObjectStatus.deleted:
                    raise self.DeletedObjectException()

            account.picture_url = self.build_picture_url(account.picture_id)

            # Include the contact information of this user account.
            if include_contacts:
                account.contacts = ContactService().get_contacts(account_id, connection=connection)

            return account

    def get_account_by_contact(
            self,
            contact,
            check_status=False,
            connection=None,
            include_pending=False,
            is_verified=True):
        """
        Return extended information about the user account specified by a
        contact information, such as, for instance, an email address, a phone
        number.


        @note: The provided contact information MUST have been verified in
        order to return a user account.

        @warning: This function is for internal usage only; it MUST not be
            surfaced to client applications.


        @param contact: An object `Contact`.

        @param check_status: Indicate whether the function MUST check the
            current status of this user account and raise an exception if is
            not of enabled.

        @param connection: Am object `RdbmsConnection` to be used supporting
            the Python clause `with ...:`.

        @param include_pending: indicate whether to include pending account
            or only enabled account.

        @param is_verified: Indicate whether the function MUST only return a
            user account if the matching contact information has been
            verified.


        @return: An object containing the following members:

            * `account_id`: Identification of the user account.

            * `full_name`: Full name of the user.

            * `username`: Name of the account of the user, if any defined.

            * `picture_id`: Identification of the user account's picture, if any
              picture defined for this user account.

            * `picture_url`: Uniform Resource Locator (URL) that specifies the
              location of the user account's picture, if any defined.  The client
              application can use this URL and append the query parameter `size`
              to specify a given pixel resolution of the user account's picture,
              such as `thumbnail`, `small`, `medium`, `large` (cf.
              `settings.IMAGE_PIXEL_RESOLUTIONS['avatar']`).

            * `locale` (required): An object `Locale` that identifies the
              preferred language of the user, or English by default.

            * `timezone`: Time zone of the default location of the user.  It is
              the difference between the time at this location and UTC (Universal
              Time Coordinated).  UTC is also  known as GMT or Greenwich Mean Time
              or Zulu Time.

            * `account_type`: Type of the user account as defined in the
              enumeration `AccountType`.

            * `is_verified`: Indicate whether the matching contact information
              has been verified.

            * `object_status`: Current status of this user account.

            * `creation_time`: Time when this user account has been registered
              against the platform.  This attribute is returned only if the user
              on behalf of whom this function is called is the owner of this
              account or connected with this user.

            * `update_time`: Time when the information of this user account has
              been updated for the last time.


        @raise DeletedObjectException: If the user account has been deleted,
            while the argument `check_status` has been set to `True`.

        @raise DisabledObjectException: If the user account has been disabled,
            while the argument `check_status` has been set to `True`.

        @raise UndefinedObjectException: If the specified contact doesn't
            refer to a user account registered against the platform.
        """
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    account.account_id,
                    account.account_type,
                    account.creation_time,
                    account.full_name,
                    account_contact.is_verified,
                    account.language,
                    account.nationality,
                    account.object_status,
                    account.picture_id,
                    account.update_time,
                    account.username
                  FROM 
                    account
                  INNER JOIN account_contact
                    USING (account_id)
                  WHERE 
                    property_name = %(property_name)s
                    AND lower(property_value) = lower(%(property_value)s)
                    AND (account.object_status = %(OBJECT_STATUS_ENABLED)s
                         OR (%(include_pending)s AND account.object_status = %(OBJECT_STATUS_PENDING)s))
                    AND (NOT %(is_verified)s OR is_verified)
                """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'OBJECT_STATUS_PENDING': ObjectStatus.pending,
                    'include_pending': include_pending,
                    'is_verified': is_verified,
                    'property_name': contact.property_name,
                    'property_value': contact.property_value.strip()
                })
            row = cursor.fetch_one()

            if row is None:
                raise self.UndefinedObjectException('No account associated to the specified contact information')

            account = row.get_object({
                'account_id': cast.string_to_uuid,
                'account_type': AccountType,
                'creation_time': cast.string_to_timestamp,
                'language': cast.string_to_locale,
                'update_time': cast.string_to_timestamp
            })

            if check_status:
                if account.object_status == ObjectStatus.disabled:
                    raise self.DisabledObjectException()
                elif account.object_status == ObjectStatus.deleted:
                    raise self.DeletedObjectException()

            account.picture_url = self.build_picture_url(account.picture_id)

            return account

    def get_accounts(
            self,
            account_ids,
            connection=None,
            include_contacts=False,
            include_hashed_password=False,
            include_verified_only=False):
        """
        Return up to 100 users worth of extended information, specified by
        their identification.

        If a requested user is unknown, suspended, or deleted, then that user
        will not be returned in the results list.


        @param account_ids: a list of account identifications or email
               addresses.

        @param connection: An object `RdbmsConnection`.

        @param include_contacts: indicate whether to include the contacts
            information of these user accounts.

        @param include_hashed_password: Indicate whether to include the hashed
            password of these accounts.  The called MUST ensure that this
            information will be secretly communicated to a client application
            owned by the organization to which these users belong to.

        @param include_verified_only: Indicate whether to only return accounts
            whose given contact information has been verified.


        @return: A list of objects containing the following members:

                 * `account_id`: identification of the user account.

                 * `full_name`: full name of the user.

                 * `username`: name of the account of the user,
                   if any defined.

                 * `picture_id`: identification of the user account's
                   picture, if any picture defined for this user account.

                 * `picture_url`: Uniform Resource Locator (URL) that
                   specifies the location of the user account's picture, if
                   any defined.  The client application can use this URL and
                   append the query parameter `size` to specify a given
                   pixel resolution of the user account's picture, such as
                   `thumbnail`, `small`, `medium`, `large`.

                 * `language`: a `Locale` instance that identifies the
                   preferred language of the user, or English by default.

                * `update_time`: time when the information of this user
                  account has been updated for the last time.


        @raise DeletedObjectException: if the user account has been deleted.

        @raise DisabledObjectException: if the user account has been disabled.

        @raise UndefinedObjectException: if the specified identification
               doesn't refer to a user account registered against the
               platform.
        """
        account_ids = set(account_ids)
        if not account_ids:
            return []

        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            # For any email address provided, determine the identification of the
            # corresponding account.
            email_addresses = [
                email_address
                for email_address in account_ids
                if isinstance(email_address, str)
                   and REGEX_PATTERN_EMAIL_ADDRESS.match(email_address.strip().lower())
            ]

            if email_addresses:
                account_ids = account_ids - set(email_addresses)
                cursor = connection.execute(
                    """
                    SELECT DISTINCT 
                        account_id
                      FROM 
                        account_contact
                      WHERE 
                        property_name = %(PROPERTY_NAME_EMAIL)s
                        AND lower(property_value) IN (%(email_addresses)s)
                        AND (NOT %(is_verified)s OR is_verified)
                    """,
                    {
                        'PROPERTY_NAME_EMAIL': ContactName.EMAIL,
                        'email_addresses': [
                            email_address.strip().lower()
                            for email_address in email_addresses
                        ],
                        'is_verified': include_verified_only,
                    })

                account_ids.update([
                    row.get_value('account_id', cast.string_to_uuid)
                    for row in cursor.fetch_all()
                ])

            cursor = connection.execute(
                """
                SELECT 
                    account_id,
                    first_name,
                    full_name,
                    language,
                    last_name,
                    nationality,
                    object_status,
                    password,
                    picture_id,
                    update_time,
                    username
                  FROM 
                    account
                  WHERE 
                    account_id IN (%(account_ids)s)
                """,
                {
                    'account_ids': list(account_ids),
                })

            accounts = [
                row.get_object({
                    'account_id': cast.string_to_uuid,
                    'language': cast.string_to_locale,
                    'object_status': ObjectStatus,
                    'update_time': cast.string_to_timestamp
                })
                for row in cursor.fetch_all()
            ]

            for account in accounts:
                if not include_hashed_password:
                    del account.password

                account.picture_url = self.build_picture_url(account.picture_id)

            # Include the contacts information of the user accounts.
            if include_contacts:
                accounts_dict = dict([(account.account_id, account) for account in accounts])

                cursor = connection.execute(
                    """
                    SELECT 
                        account_id,
                        property_name,
                        property_value,
                        is_primary,
                        is_verified
                      FROM
                        account_contact
                      WHERE
                        account_id IN (%(account_ids)s)
                        AND object_status = %(OBJECT_STATUS_ENABLED)s
                    """,
                    {
                        'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                        'account_ids': accounts_dict.keys()
                    })

                accounts_contacts = collections.defaultdict(list)
                for account_contact in [
                    row.get_object({
                        'account_id': cast.string_to_uuid,
                        'name': ContactName
                    })
                    for row in cursor.fetch_all()
                ]:
                    accounts_contacts[account_contact.account_id].append(account_contact)
                    del account_contact.account_id

                for account_id, account_contacts in accounts_contacts.items():
                    accounts_dict[account_id].contacts = account_contacts

            return accounts

    def get_accounts_by_contacts(
            self,
            contacts,
            verified_only=False,
            ignore_deleted=True):
        """
        Return a list of accounts that match the specified contact
        information.


        @param contacts: a list of tuple `(name, value)` where:

               * `name`: name of a property, which can be one of a set of
                 pre-defined strings such as:

                 * `EMAIL`: e-mail address.

                 * `PHONE`: phone number in E.164 numbering plan, an ITU-T
                   recommendation which defines the international public
                   telecommunication numbering plan used in the Public
                   Switched Telephone Network (PSTN).

              * `value`: value of the property representing by a string,
                such as `+84.01272170781`, the formatted value for the
                Telephone Number property.

        @param verified_only: indicate whether the function must only return
               accounts that match contact information which has been
               verified.

        @param ignore_deleted: indicate whether the function must ignore
               accounts that are deleted.


        @return: a list of instances containing the following members:

            * `account_id`: identification of the user account.

            * `full_name`: full name of the user.

            * `username`: name of the account of the user, if any defined.

            * `picture_id`: identification of the user account's picture, if any
              picture defined.

            * `picture_url`: Uniform Resource Locator (URL) that specifies the
              location of the user account's picture, if any defined.  The client
              application can use this URL and append the query parameter `size`
              to specify a given pixel resolution of the user account's picture,
              such as `thumbnail`, `small`, `medium`, `large` (cf.
              `settings.IMAGE_PIXEL_RESOLUTIONS['avatar']`).

            * `language`: a `Locale` instance that identifies the preferred
              language of the user, or English by default.

            * `timezone`: time zone of the default location of the user.  It is
              the difference between the time at this location and UTC (Universal
              Time Coordinated).  UTC is also  known as GMT or Greenwich Mean Time
              or Zulu Time.

            * `account_type`: type of the user account as defined in the
              enumeration `AccountType`.

            * `object_status`: current status of this user account.

            * `creation_time`: time when this user account has been registered
              to the platform.

            * `update_time`: time when the information of this user account has
              been updated for the last time.
        """
        if not isinstance(contacts, (list, set)) or len(contacts) == 0:
            return []

        with self.acquire_rdbms_connection() as connection:
            cursor = connection.execute("""
                SELECT
                    account.account_id,
                    account.account_type,
                    account.creation_time,
                    account.language,
                    account.nationality,
                    account.picture_id,
                    account.object_status,
                    account.timezone,
                    account.update_time
                  FROM (
                    SELECT DISTINCT
                        account_id
                      FROM
                          account_contact,
                          (VALUES %[values]s) AS foo(name, value)
                        WHERE 
                          account_contact.property_name = foo.name
                          AND lower(account_contact.property_value) = lower(trim(both ' ' from foo.value))
                          AND (NOT %(verified_only)s OR is_verified)
                          AND object_status = %(OBJECT_STATUS_ENABLED)s) AS foo
                  INNER JOIN account
                    USING (account_id)""",
                { 'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                  'values': contacts,
                  'verified_only': verified_only })
            accounts = [ row.get_object({
                    'account_id': cast.string_to_uuid,
                    'creation_time': cast.string_to_timestamp,
                    'picture_id': cast.string_to_uuid,
                    'update_time': cast.string_to_uuid })
                for row in cursor.fetch_all() ]

            if ignore_deleted:
                accounts = [ account for account in accounts
                        if account.object_status != ObjectStatus.deleted ]

            for account in accounts:
                account.picture_url = self.build_picture_url(account.picture_id)

            return accounts


    def get_sns_data_deletion(self, app_id, request_id):
        """
        Return information about a request sent to the platform to delete the
        data of auser that an application has collected from the given Social
        Networking Service about this user.


        @param app_id: identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        @param request_id: identification of the data deletion request as
            registered to the platform.


        @return: an instance containing the following attributes:

            * `creation_time` (required): time when the request to delete the data
              of a user has been initiated.

            * `object_status` (required): current status of this data deletion
              request.

            * `request_id` (required): the identification of the data deletion
              request as registered to the platform.

            * `sns_app_id` (required): identification of the application as
              registered to the 3rd party Social Networking Service.

            * `sns_name` (required): code name of the 3rd party Social Networking
              Service.

            * `sns_user_id` (required): identification of the user as registered
              to the 3rd party Social Networking Service.

            * `update_time` (required): time of the most recent update of the
              access token of this user.
        """
        with self.acquire_rdbms_connection(auto_commit=False) as connection:
            cursor = connection.execute(
                """
                SELECT request_id,
                       sns_name,
                       sns_app_id,
                       sns_user_id,
                       object_status,
                       creation_time,
                       update_time 
                  FROM account_sns_data_deletion_request
                  WHERE request_id = %(request_id)s
                """,
                {
                    'request_id': request_id
                })

            row = cursor.fetch_one()
            if row is None:
                raise self.UndefinedObjectException('Undefined SNS data deletion request')

            return row.get_object({
                'creation_time': cast.string_to_timestamp,
                'object_status': ObjectStatus,
                'request_id': cast.string_to_uuid,
                'update_time': cast.string_to_timestamp
            })

    def index_all_accounts(self, connection=None):
        """
        Reindex all the accounts


        :note: This function MUST NOT be surfaced to any client applications,
            but called from Python terminal as follows:

            ```bash
            $ python
            Python 3.7.4 (default, Jul 12 2019, 18:26:19)
            [GCC 5.4.0 20160609] on linux
            Type "help", "copyright", "credits" or "license" for more information.
            >>> from majormode.perseus.service.account.account_service import AccountService
            >>> AccountService().index_all_accounts()
            ```

        :todo: This function SHOULD be replaced with the use of another
            technology such as Elasticsearch more suitable for indexing and
            indexing data.


        @param connection: An object `RdbmsConnection` with auto commit.
        """
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT
                    account_id, 
                    full_name
                  FROM ONLY
                    account
                """
            )

            accounts = [
                row.get_object({
                    'account_id': cast.string_to_uuid
                })
                for row in cursor.fetch_all()
            ]

            for account in accounts:
                self.__index_account(account.account_id, account.full_name, connection=connection)

    def is_contact_verification_request(
            self,
            contact: Contact = None,
            request_id: uuid.UUID = None,
            verification_code: str = None):
        """
        Indicate whether the specified contact verification request exists.


        @param contact: An object `Contact`.

        @param request_id: The identification of the contact verification request.


        @return: `True` if the specified identification corresponds to a
            contact verification request registered to the platform;
            `False` otherwise.
        """
        return ContactService().validate_contact_verification_request(
            contact=contact,
            request_id=request_id,
            verification_code=verification_code)

    def is_username_available(self, app_id, username):
        """
        Indicate whether the specified username is available or not.


        @param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        @param username: A username to check whether it is already registered
            by an existing user or not.  A username is unique across the
            platform.  A username is not case sensitive.

        @return: `True` if the username is not registered by any existing
            account; `False` otherwise.
        """
        with self.acquire_rdbms_connection() as connection:
            cursor = connection.execute(
                """
                SELECT 
                    true
                  FROM 
                    account
                  WHERE
                    lower(username) = lower(%(username)s)
                    AND object_status = %(OBJECT_STATUS_ENABLED)s
                """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'username': username
                })

            return cursor.get_row_count() == 0

    def request_password_reset(
            self,
            app_id,
            contact,
            connection=None,
            context=None,
            lifespan=DEFAULT_PASSWORD_RESET_REQUEST_LIFESPAN,
            language=None,
            nonce_digit_count=0):
        """
        Initiate the process to help the user in resetting his forgotten
        password

        The function generates a request composed of a unique identifier, and
        possibly a *nonce* ("number used once"), to be used to reset the user's
        password (cf. function `reset_password`).

        The identifier is generally used in a HTML link that is emailed to the
        user's email address.  This link redirects the user to a web
        application responsible for allowing the user to enter a new password.

        The nonce is composed of digits that are sent in an email addressed to
        the user.  The user needs to enter this nonce in a mobile application
        along with his new password.

        Note: If the user sends consecutively two requests to reset his
        password within the minimal allowed duration of time (cf. the constant
        `MINIMAL_TIME_BETWEEN_PASSWORD_RESET_REQUEST`), the function ignores the
        last request and returns the identification of the first request.


        @param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        @param contact: An object `Contact` representing a contact of the user
            who is requesting to reset his forgotten password.

        @param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...:`.

        @param context: A JSON expression corresponding to the context in
            this contact information has been added and needs to be verified.

        @param lifespan: Duration in seconds the password reset request lives
            before it expires.

        @param language: A `Locale` instance referencing the preferred language
            of the user that will be used to generate a message to be sent to
            this user.

        @param nonce_digit_count: Number of digits that composed the nonce, or
            `0` if the function doesn't need to generate a nonce.


        @raise DeletedObjectException: If the user account has been deleted.

        @raise DisabledObjectException: If the user account has been disabled.

        @raise InvalidOperationException: If a password reset has already been
            requested recently for this email address.

        @raise UndefinedObjectException: If the specified email address
            doesn't refer to any user account registered against the platform.
        """
        account = self.get_account_by_contact(
            contact,
            check_status=True,
            is_verified=False)

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            # Check whether there is an active password reset request that would
            # have been sent to the specified recipient (cf. contact information).
            cursor = connection.execute(
                """
                SELECT 
                    expiration_time,
                    nonce,
                    request_id
                  FROM
                    account_password_reset
                  WHERE
                    account_id = %(account_id)s
                    AND property_name = %(property_name)s
                    AND property_value = %(property_value)s
                    AND object_status = %(OBJECT_STATUS_ENABLED)s
                """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'account_id': account.account_id,
                    'property_name': contact.property_name,
                    'property_value': contact.property_value
                })

            row = cursor.fetch_one()
            request = row and row.get_object({
                'expiration_time': cast.string_to_timestamp,
                'request_id': cast.string_to_uuid,
            })

            # Disable a previous request that exists but has expired.
            has_previous_request_expired = request is not None and ISO8601DateTime.now() > request.expiration_time
            if has_previous_request_expired:
                self.update_password_reset_request(
                    request.request_id,
                    connection=connection,
                    object_status=ObjectStatus.disabled)

            # If no password reset request is active, generate one to be sent to the
            # specified recipient (cf. contact information).
            if request is None or has_previous_request_expired:
                nonce = None if nonce_digit_count <= 0 \
                    else self.__generate_nonce(min(nonce_digit_count, self.NONCE_MAXIMUM_DIGIT_COUNT))

                connection.execute(
                    f"""
                    INSERT INTO account_password_reset(
                        account_id,
                        app_id,
                        expiration_time,
                        property_name,
                        property_value,
                        context,
                        language,
                        nonce)
                      VALUES (
                        %(account_id)s,
                        %(app_id)s,
                        current_timestamp + '{lifespan} seconds'::interval,
                        %(property_name)s,
                        %(property_value)s,
                        %(context)s,
                        %(language)s,
                        %(nonce)s
                      )
                    """,
                    {
                        'account_id': account.account_id,
                        'app_id': app_id,
                        'context': context,
                        'language': language or account.language or DEFAULT_LOCALE,
                        'nonce': nonce,
                        'property_name': contact.property_name,
                        'property_value': contact.property_value,
                    })

            # Otherwise, reattempt sending the reset password instruction to the
            # specified contact.
            else:
                connection.execute(
                    """
                    UPDATE 
                        account_password_reset
                      SET
                        update_time = current_timestamp,
                        request_count = request_count + 1
                      WHERE
                        account_id = %(account_id)s
                        AND property_name = %(property_name)s
                        AND property_value = %(property_value)s
                    """,
                    {
                        'account_id': account.account_id,
                        'property_name': contact.property_name,
                        'property_value': contact.property_value
                    })

    def request_sns_data_deletion(self, app_id, sns_name, sns_app_id, sns_user_id):
        """
        Request the platform to delete the data of the specified user that an
        application has collected from the given Social Networking Service
        about this user.


        @param app_id: identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        @param sns_name: code name of the 3rd party Social Networking Service.

        @param sns_app_id: identification of the application as registered to
            the 3rd party Social Networking Service.

        @param sns_user_id: identification of the user as registered to the
            3rd party Social Networking Service.


        @return: an instance containing the following attributes:

            * `creation_time` (required): time when this request has been
              registered to the platform.

            * `request_id` (required): identification of the data deletion
              request as registered to the platform.
        """
        with self.acquire_rdbms_connection(auto_commit=True) as connection:
            cursor = connection.execute(
                """
                INSERT INTO 
                    account_sns_data_deletion_request(
                        sns_name,
                        sns_app_id,
                        sns_user_id)
                  VALUES 
                    (lower(%(sns_name)s),
                     %(sns_app_id)s,
                     %(sns_user_id)s)
                  ON CONFLICT (sns_user_id, sns_app_id, sns_name) DO
                    UPDATE
                      SET 
                        object_status = %(OBJECT_STATUS_ENABLED)s,
                        update_time = current_timestamp
                      WHERE
                        account_sns_data_deletion_request.sns_name = EXCLUDED.sns_name
                        AND account_sns_data_deletion_request.sns_app_id = EXCLUDED.sns_app_id
                        AND account_sns_data_deletion_request.sns_user_id = EXCLUDED.sns_user_id
                  RETURNING
                    request_id,
                    creation_time
                """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'sns_app_id': sns_app_id,
                    'sns_name': sns_name,
                    'sns_user_id': sns_user_id
                })

            return cursor.fetch_one().get_object({
                'creation_time': cast.string_to_timestamp,
                'request_id': cast.string_to_uuid,
            })

    def reset_password_from_admin(
            self,
            account_id,
            admin_account_id=None,
            connection=None,
            is_password_change_required=True,
            are_symbols_allowed=True,
            new_password=None,
            password_length=None):
        """
        Reset the password of a user account

        If a user forgets the password for their managed account, or if an
        administrator thinks their account has been compromised, he can reset
        their password.


        :todo: Store this password reset in the history of actions, including
            the account of the administrator who performs this action, for
            security audit purpose.


        @param account_id: Identification of the account of the user to reset
            their password.

        @param connection: An object `RdbmsConnection` with auto commit.

        @param is_password_change_required: Indicate whether the user will
            have to change their password at the next login.

        @param are_symbols_allowed: Indicate whether the password can
            contain punctuation characters.

        @param new_password: New password to be associated to the user's
            account, or `None` to automatically generate a new password.

        @param password_length: Number of characters that composes the
            password to be generated.


        @return: An object containing the following attributes:

            * `account_id` (required): Identification of the account of the user
                whose password has been reset.

            * `new_password` (required): Plain text password that has been set for
              this user.
        """
        # Generate a new password if no password has been passed.
        if not new_password:
            new_password = self.__generate_password(
                length=password_length or self.MINIMUM_PASSWORD_LENGTH,
                are_symbols_allowed=are_symbols_allowed)

        # Encrypt the new password passed to the function.
        self.__validate_password_complexity_requirements(new_password)
        encrypted_new_password = self.__encrypt_password(new_password)

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            # Reset the password of the user's account with the new password
            # passed to this function or automatically generated.
            connection.execute(
                """
                UPDATE 
                    account
                  SET
                    password = %(password)s,
                    is_password_change_required=%(is_password_change_required)s,
                    update_time = current_timestamp
                  WHERE 
                    account_id = %(account_id)s
                """,
                {
                    'account_id': account_id,
                    'is_password_change_required': is_password_change_required,
                    'password': encrypted_new_password
                })

        account = Object(
            account_id=account_id,
            new_password=new_password
        )

        return account

    def reset_password_from_request(
            self,
            app_id,
            new_password,
            connection=None,
            contact=None,
            nonce=None,
            request_id=None):
        """
        Change the password of the account of a user who forgot his password
        and who requested the platform to reset, as this user cannot login
        into the platform anymore.


        @param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        @param new_password: New password to be associated to the user's
            account.

        @param connection: An object `RdbmsConnection` with auto commit.

        @param contact: An object `Contact` corresponding to an email address
            or a mobile phone number where a random number (nonce) has been
            sent to for verifying the password reset request.  The argument
            `nonce` is also required.

        @param nonce: "Number used once", a pseudo-random number issued when
            generating the request to allow the user to change his password
            through a mobile application.  The argument `contact` is also
            required.

        @param request_id: Identification of the request of the user to reset
             his forgotten password (cf. function `request_password_reset`).


        @raise `DeletedObjectException`: if the specified password reset
            request has been cancelled by the user or if this request has
            expired.

        @raise `DisabledObjectException`: if the specified password reset
            request has been already used by the user to reset the password
            of his account.

        @raise `IllegalAccessException`: if the client application or the
            user account, on behalf of this function is called, is not allowed
            to reset this password.

        @raise InvalidArgumentException: if the new password doesn't conform
            to the rules of password definition.

        @raise `UndefinedObjectException`: if the specified password reset
            request has not been registered on the platform.
        """
        # Encrypt the new password passed to the function.
        self.__validate_password_complexity_requirements(new_password)
        encrypted_new_password = self.__encrypt_password(new_password)

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            request = self.__get_password_reset_request(
                app_id,
                connection=connection,
                contact=contact,
                nonce=nonce,
                request_id=request_id)

            # Reset the password of the user's account with the new password
            # passed to this function.
            connection.execute(
                """
                UPDATE 
                    account
                  SET
                    password = %(password)s,
                    update_time = current_timestamp
                  WHERE 
                    account_id = %(account_id)s
                """,
                {
                    'account_id': request.account_id,
                    'password': encrypted_new_password
                })

            # Deleted the password reset request of the user that has been
            # fulfilled.
            self.update_password_reset_request(
                request.request_id,
                connection=connection,
                object_status=ObjectStatus.deleted)

    # def search_users(
    #         self,
    #         full_name,
    #         account_id=None,
    #         connection=None,
    #         limit=BaseRdbmsService.DEFAULT_LIMIT,
    #         offset=0):
    #     """
    #     Search for users providing input text that may correspond to partial
    #     name, or contact information, such as email address or phone number.
    #
    #
    #     @param full_name: partial or complete personal name by which the child
    #         is known.
    #
    #     @param account_id: identification of the account of the user who is
    #         requesting this search.
    #
    #     @param connection: a `RdbmsConnection` instance to be used
    #         supporting the Python clause `with ...:`.
    #
    #     @param limit: constrain the number of children to return to the
    #         specified number.  If not specified, the default value is
    #         `BaseService.DEFAULT_RESULT_SET_SIZE`.  The maximum value is
    #         `BaseService.MAXIMUM_RESULT_SET_LIMIT`.
    #
    #     @param offset: require to skip that many records before beginning to
    #         return records to the client.  Default value is `0`.  If both
    #         `offset` and `limit` are specified, then `offset` records
    #         are skipped before starting to count the limit records that are
    #         returned.
    #
    #
    #     @return: an instance containing the following members:
    #
    #         * `account_id`: identification of the user account.
    #
    #         * `full_name`: full name of the user.
    #
    #         * `username`: name of the account of the user, if any defined.
    #
    #         * `picture_id`: identification of the user account's picture, if any
    #           picture defined for this user account.
    #
    #         * `picture_url`: Uniform Resource Locator (URL) that specifies the
    #           location of the user account's picture, if any defined.  The client
    #           application can use this URL and append the query parameter `size`
    #           to specify a given pixel resolution of the user account's picture,
    #           such as `thumbnail`, `small`, `medium`, `large` (cf.
    #           `settings.IMAGE_PIXEL_RESOLUTIONS['avatar']`).
    #
    #         * `language` (required): a `Locale` instance that identifies the
    #           preferred language of the user, or English by default.
    #     """
    #     if REGEX_PATTERN_EMAIL_ADDRESS.match(full_name):
    #         return self.get_accounts_by_contacts([ Contact.ContactName.EMAIL, input ])
    #
    #     if full_name.isdigit():
    #         return self.get_accounts_by_contacts([ Contact.ContactName.PHONE, input ])
    #
    #     keywords = self.__string_to_keywords(full_name)
    #
    #     with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
    #         cursor = connection.execute(
    #             """
    #             SELECT account_id,
    #                    full_name,
    #                    username,
    #                    picture_id,
    #                    language
    #               FROM account
    #               INNER JOIN (
    #                   SELECT account_id,
    #                          COUNT(*) AS score
    #                     FROM account_index
    #                     INNER JOIN account
    #                       USING (account_id)
    #                     WHERE keyword IN (%[keywords]s)
    #                       AND (%(account_id)s IS NULL OR account_id <> %(account_id)s)
    #                       AND object_status IN (%(OBJECT_STATUS_PENDING)s, %(OBJECT_STATUS_ENABLED)s)
    #                       GROUP BY account_id) AS foo
    #               USING (account_id)
    #               ORDER BY score DESC,
    #                        account_id DESC -- @hack: to preserve order of accounts with same score from an offset to anoth
    #               LIMIT %(limit)s
    #               OFFSET %(offset)s
    #             """,
    #             {
    #                 'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
    #                 'OBJECT_STATUS_PENDING': ObjectStatus.pending,
    #                 'account_id': account_id,
    #                 'keywords': keywords,
    #                 'limit': min(limit, self.MAXIMUM_LIMIT) or self.MAXIMUM_LIMIT,
    #                 'offset': offset
    #             })
    #
    #         accounts = [
    #             row.get_object({
    #                 'account_id': cast.string_to_uuid,
    #                 'language': Locale,
    #                 'picture_id': cast.string_to_uuid})
    #             for row in cursor.fetch_all()]
    #
    #         for account in accounts:
    #             account.picture_url = self.build_picture_url(account.picture_id)
    #
    #         return accounts

    def set_full_name(self, app_id, account_id, full_name):
        """
        Update the complete full_name of a user.


        @param app_id: identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        @param account_id: identification of the user's account.

        @param full_name: complete full name of the user as given by the user
            himself, i.e., untrusted information.


        @return: an instance containing the following members:

            * `account_id` (required): identification of the user's account.

            * `full_name` (required): the new complete full name of the user as
              given by the user himself.

            * `update_time` (required): time of the most recent modification of
              the properties of the user's account.


        @raise DeletedObjectException: if the user's account has been deleted.

        @raise DisabledObjectException: if the user's account has been
            disabled.

        @raise Undefined ObjectException: if the specified identification
            doesn't refer to a user account registered to the platform.
        """
        with self.acquire_rdbms_connection(auto_commit=True) as connection:
            cursor = connection.execute(
                """
                UPDATE
                    account
                  SET
                    full_name = %(full_name)s,
                    update_time = current_timestamp
                  WHERE
                    account_id = %(account_id)s
                  RETURNING
                    account_id,
                    full_name,
                    object_status,
                    update_time
                """,
                {
                    'account_id': account_id,
                    'full_name': full_name.strip()
                })
            row = cursor.fetch_one()
            if row is None:
                raise self.UndefinedObjectException()

            account = row.get_object({
                'account_id': cast.string_to_uuid,
                'update_time': cast.string_to_timestamp
            })

            if account.object_status == ObjectStatus.disabled:
                raise self.DisabledObjectException()
            elif account.object_status == ObjectStatus.deleted:
                raise self.DeletedObjectException()

            del account.object_status

            # Re-index this account with this new full_name.
            self.__index_account(account_id, full_name)

            return account

    def set_language(
            self,
            account_id,
            language,
            connection=None):
        """
        Change the preferred language of a user


        @param account_id: The identification of user's account.

        @param language: An object `Locale`.

        @param connection: An object `RdbmsConnection` with auto commit.


        @return: An object containing the following attributes:

            * `account_id` (required): The identification of the user's account.

            * `object_status` (required): An item of the enumeration `ObjectStatus`
              representing the current status of the user's account.

            * `update_time` (required): The time of the most recent modification of
              the attribute of the user's account.
        """

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            cursor = connection.execute(
                """
                UPDATE
                    account
                  SET
                    language = %(language)s
                  WHERE
                    account_id = %(account_id)s
                  RETURNING
                    account_id,
                    object_status,
                    update_time
                """,
                {
                    'account_id': account_id,
                    'language': language or DEFAULT_LOCALE,
                }
            )

            row = cursor.fetch_one()
            account = row and row.get_object({
                'account_id': cast.string_to_uuid,
                'object_status': ObjectStatus,
                'update_time': cast.string_to_timestamp,
            })

            return account

    def set_nationality(
            self,
            account_id,
            nationality,
            connection=None):
        """
        Change the nationality of a user


        @param account_id: The identification of user's account.

        @param nationality: A ISO 3166-1 alpha-2 code referencing the
            nationality of the user.

        @param connection: An object `RdbmsConnection` with auto commit.


        @return: An object containing the following attributes:

            * `account_id` (required): The identification of the user's account.

            * `object_status` (required): An item of the enumeration `ObjectStatus`
              representing the current status of the user's account.

            * `update_time` (required): The time of the most recent modification of
              the attribute of the user's account.
        """

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            cursor = connection.execute(
                """
                UPDATE
                    account
                  SET
                    nationality = %(nationality)s
                  WHERE
                    account_id = %(account_id)s
                  RETURNING
                    account_id,
                    object_status,
                    update_time
                """,
                {
                    'account_id': account_id,
                    'nationality': nationality,
                }
            )

            row = cursor.fetch_one()
            account = row and row.get_object({
                'account_id': cast.string_to_uuid,
                'object_status': ObjectStatus,
                'update_time': cast.string_to_timestamp,
            })

            return account

    def set_username(
            self,
            app_id,
            account_id,
            username,
            connection=None):
        """
        Set the username of a user account.


        @param app_id: The identification of the client application that
            accesses this service.

        @param account_id: The identification of the user account to set the
            username.

        @param username: The username to set for the user account.

        @param connection: An object `RdbmsConnection` with auto commit.
        """
        if not self.is_username_available(app_id, username):
            raise self.UsernameAlreadyUsedException(f'The username "{username}" is already used')

        self.get_account(account_id, check_status=True, connection=connection)

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            # Remove the username from a deleted user account.
            connection.execute(
                """
                UPDATE
                    account
                  SET
                    username = NULL,
                    update_time = current_timestamp
                  WHERE
                    username = %(username)s
                """,
                {
                    'username': username,
                }
            )

            # Set the username to the specified user account.
            connection.execute(
                """
                UPDATE
                    account
                  SET
                    username = %(username)s,
                    update_time = current_timestamp
                  WHERE
                    account_id = %(account_id)s
                """,
                {
                    "account_id": account_id,
                    "username": username,
                }
            )

    def sign_in_with_id(
            self,
            app_id,
            account_id,
            password,
            connection=None,
            include_contacts=False,
            session_duration=None):
        """
        Sign in the user with his account identification


        @param app_id: The identification of the client application that
            accesses this service.

        @param account_id: The identification of the user account.

        @param password: The password of the user account.

        @param connection: An object `RdbmsConnection` with auto commit.

        @param include_contacts: Indicate whether to return the contact
            information of the user.

        @param session_duration: The login session duration, expressed in
            seconds, corresponding to the interval of time between the
            creation of the token and the expiration of this login session.


        @return: An object containing the following attributes:

            * `account_id`: identification of the account of the user.

            * `expiration_time`: time when the login session will expire.

            * `session_id`: identification of the login session of the user.


        @raise AuthenticationFailureException: If the account identification
            and/or the password don't match an account registered to the
            server platform.

        @raise DeletedObjectException: If the user account has been deleted.

        @raise DisabledObjectException: If the user account has been disabled.
        """
        session = self.__sign_in(
            app_id,
            account_id,
            password,
            connection=connection,
            include_contacts=include_contacts,
            session_duration=session_duration)

        return session

    def sign_in_with_contact(
            self,
            app_id: uuid.UUID,
            contact: Contact,
            password: str,
            allow_unverified_contact: bool = True,
            connection: RdbmsConnection = None,
            include_contacts: bool = False,
            session_ttl: int = None):
        """
        Sign-in the user with a contact information and a password.


        @param app_id: The identification of the client application that
            initiates this call.

        @param contact: The contact information associated with the account of
            a user.

        @param password: The password of the user account.

        @param allow_unverified_contact: Indicate whether the user is allowed
            to sign in with a contact not yet verified.

        @param connection: An existing connection to the user database with
            the option `auto_commit` enabled.

        @param include_contacts: Indicate whether to return the contact
            information of the user.

        @param session_ttl: Login session time-to-live (TTL), expressed in
            seconds, of the user.


        @return: An object containing the following members:

            - `account_id: uuid.UUID` (required): The identification of the accoun
              of the user.

            - `expiration_time: ISO8601DateTime` (required): The time when the login
              session of the user will expire.

            - `full_name: str` (required): The complete full name of the user.

            - `is_verified: bool` (required): Indicate whether the given contact
              information has been verified, whether it has been grabbed from a
              trusted Social Networking Service (SNS), or whether through a
              challenge/response process.  The user should be reminded to confirm
              his contact information if not already verified, or the user would
              take the chance to have his account suspended.

            - `is_primary: bool` (required): Indicate whether the given contact
              information is the primary one for the given property.

            - `session_id: uuid.UUID` (required): The identification of the login
              session of the user.

            - `username: str` (optional): The username of the user.  Also known as
              the screen name or the nickname of the user.


        @raise AuthenticationFailureException: If the given contact
            information and/or password don't match any account registered
            against the platform.

        @raise DeletedObjectException: If the user account has been deleted.

        @raise DisabledObjectException: If the user account has been disabled.

        @raise UnverifiedContactException: If the contact of this user has not
            been verified yet, while the parameter `allow_unverified_contact`
            has been passed with the value `False`.
        """
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            # Retrieve the identification of the user account corresponding to this
            # contact information, including the hashed version of its password
            # since the method `get_account` doesn't return it for security reason.
            cursor = connection.execute(
                """
                SELECT 
                    account_id,
                    password,
                    is_verified
                  FROM
                    account_contact
                  INNER JOIN account
                    USING (account_id)
                  WHERE
                    property_name = %(property_name)s
                    AND lower(property_value) = %(property_value)s
                    AND account_contact.object_status = %(OBJECT_STATUS_ENABLED)s
                """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'property_name': contact.property_name,
                    'property_value': contact.property_value,
                }
            )

            row = cursor.fetch_one()
            if row is None:
                # @note: do not inform that no user has been registered with this
                #     contact information, which might be sensitive information.
                raise self.AuthenticationFailureException()

            account_contact = row.get_object({
                'account_id': cast.string_to_uuid,
            })

            if not account_contact.is_verified and not allow_unverified_contact:
                raise self.UnverifiedContactException("The user's contact information has not been verified yet")

            session = self.__sign_in(
                app_id,
                account_contact.account_id,
                password,
                connection=connection,
                include_contacts=include_contacts,
                session_duration=session_ttl)

            return session

    def sign_in_with_username(
            self,
            app_id: uuid.UUID,
            username: str,
            password: str,
            connection: RdbmsConnection = None,
            include_contacts: bool = False,
            session_duration: int = None):
        """
        Sign-in the user against the platform providing a username and a
        password.


        @param app_id: identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        @param username: the username of the user account.

        @param password: the password of the user account.

        @param connection: An object `RdbmsConnection` that supports Python
            clause `with ...`.

        @param include_contacts: Indicate whether to return the contact
            information of the user.

        @param session_duration: Login session duration, expressed in
            seconds, corresponding to the interval of time between the
            creation of the token and the expiration of this login session.


        @return: a session instance containing the following members:

            - `account_id`: identification of the account of the user.

            - `expiration_time`: time when the login session will expire.

            - `session_id`: identification of the login session of the user.


        @raise DeletedObjectException: if the user account has been deleted.

        @raise DisabledObjectException: if the user account has been disabled.

        @raise AuthenticationFailureException: if the given username and/or
            password don't match any account registered against the
            platform.
        """
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    account_id
                  FROM
                    account
                  WHERE
                    lower(username) = lower(%(username)s)
                    AND object_status = %(OBJECT_STATUS_ENABLED)s
                  """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'username': username.strip()
                })
            row = cursor.fetch_one()
            if row is None:
                # @note: Do not inform that no user has been registered with this
                #     username, which might be sensitive information.
                raise self.AuthenticationFailureException()

            account_id = row.get_value('account_id', cast.string_to_uuid)
            session = self.__sign_in(
                app_id,
                account_id,
                password,
                connection=connection,
                include_contacts=include_contacts,
                session_duration=session_duration)

            return session

    def sign_out(self, app_id, session):
        """
        Sign out the specified user from his login session.


        @param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        @param session: An object containing the following attributes:

            * `account_id` (required): Identification of the account of the a user.

            * `session_id` (required): Identification of the user's session.


        @raise IllegalAccessException: If the specified login session doesn't
            belong to the specified user.

        @raise UndefinedObjectException: If the specified identification
            doesn't refer to any user login session registered against the
            platform.
        """
        SessionService().drop_session(app_id, session)

    def sign_up(
            self,
            account_type=AccountType.standard,
            action_type=None,
            app_id=None,
            auto_sign_in=False,
            bypass_recaptcha=True,
            can_password_be_changed=True,
            connection=None,
            contacts=None,
            context=None,
            inherited_table_name=None,
            does_password_never_expire=True,
            enable_account=True,
            has_been_verified=False,
            is_password_change_required=False,
            first_name=None,
            full_name=None,
            last_name=None,
            nationality=None,
            password=None,
            language=None,
            recaptcha=None,
            set_pending_if_unverified_contact=False,
            strict_prosoponym=True,
            team_id=None,
            to_be_verified=False,
            username=None,
            validate_password=True):
        """
        Register a new user account to the platform.

        A user account is identified by a contact or/and a username, except
        account that is created from a 3rd-party Social Networking Service
        (SNS), in which case contacts and username are optional.

        A password is mandatory except for botnet, ghost, and SNS user
        accounts.

        The specified contact MUST not be already registered and verified by
        another user account.

        If the specified contact has been already registered but not verified
        yet, the function doesn't create a new account but returns the user
        account which this contact is associated to.


        @param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        @param account_type: an item of `AccountType` that
            describes the context that caused the registration of this user
            account.

        @param action_type: Indicate the type of the action that initiates
            the request for verifying the specified contact information.

        @param auto_sign_in: Indicate whether the platform is requested to
            sign-in this user once the sign-up procedure completes
            successfully.

        @param can_password_be_changed: Indicate whether the user can change
            his password.

        @param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...`.

        @param contacts: An object `Contact` or a list of objects `Contact`.

        @param context: A JSON expression corresponding to the context in
            which this contact has been added and need to be verified.

        @param inherited_table_name: Name of the table, inheriting from the
            base table `account`, in which to insert the information of the
            account of the user to create.

        @param does_password_never_expire: Indicate whether the password of
            the user never expires.

        @param enable_account: Indicate whether this user account is immediately
            enabled, or whether it needs to be flagged as pending until the
            user takes some action, such as, for instance, confirming his
            contact information.

        @param full_name: Complete name of the user.

        @param first_name: Forename (also known as *given name*) of the user.

        @param is_password_change_required: Indicate whether user must change
            his password at the next login.

        @param last_name: Surname (also known as *family name*) of the user.

        @param language: An object `Locale` referencing the preferred language
            of the user.

        @param nationality: A ISO 3166-1 alpha-2 code referencing the
            nationality of the user.

        @param password: Password associated to the user account.  A password
            is required if the argument `set_enabled` is `True`.

        @param set_pending_if_unverified_contact: Indicate whether to set the
            account of this user in a pending status if the specified contact
            information has not been verified.

        @param strict_prosoponym: Indicate whether the function must verify
            if the full name of a user matches the first and the last name of
            this user.

        @param team_id: Identification of the organization that creates this
            user account.

        @param to_be_verified: Indicate whether the platform needs to send a
            request to the user to verify his contact information.  This
            argument cannot be set to `True` if the argument `has_been_verified`
            has been set to `True`.

        @param username: A name used to gain access to the platform.  The
            username MUST be unique among all the usernames already registered
            by other users to the platform.  This argument is optional if and
            only if contact information has been passed.

        @param validate_password: Indicate whether the format of the password
            needs to be validated.


        @return: An object containing the following attributes:

            * `account_id` (required): identification of the account of the
              user.

            * `creation_time` (required): time when this account has been
              registered.  This information should be stored by the client
              application to manage its cache of accounts.

            * `expiration_time` (optional): time when the login session will
              expire.  This information is provided if the client application
              requires the platform to automatically sign-in the user (cf.
              parameter `auto_sigin`).

            * `language` (required): an instance `Locale` specifying the preferred
              language of the user.


            * `object_status` (required): current status of this user account.

            * `session_id` (optional): identification of the login session of
              the user.  This information is provided if the client application
              requires the platform to automatically sign-in the user (cf.
              parameter `auto_sigin`).


        @raise ContactAlreadyUsedException: if one or more contacts are
            already associated and verified for a user account.

        @raise InvalidArgumentException: if one or more arguments are not
            compliant with their required format, if some required information
            is missing.

        @raise UsernameAlreadyUsedException: if the specified username is
            already associated with an existing user account.
        """
        if account_type not in AccountType:
            raise self.InvalidArgumentException(f'Unsupported type "{str(account_type)}" of user account')

        # A user name must be provided when the given contact information has
        # not be verified.  The reason is if another user provides the same
        # contact information and he passes the verification challenge, this
        # identification will be reallocated to this second user account,
        # meaning that the first user won't have any more identification to
        # sign-in to the platform.
        if not username and not contacts and account_type not in [
                AccountType.sns,
                AccountType.ghost
            ]:
            raise self.InvalidArgumentException(
                "A username and/or a contact information MUST be provided")

        if username:
            username = username.strip().lower()
            if not self.is_username_available(app_id, username):
                raise self.UsernameAlreadyUsedException(
                    "This username is already associated with an existing user account")

        generate_password = password is None and enable_account and account_type not in [
                AccountType.sns,
                AccountType.ghost,
                AccountType.botnet
        ]
        if generate_password:
            password = self.__generate_password(self.MINIMUM_PASSWORD_LENGTH)
            generated_password = password

        if password:
            password = password.strip()
            if validate_password:
                self.__validate_password_complexity_requirements(password)
            password = self.__encrypt_password(password)

        if is_password_change_required and not can_password_be_changed:
            raise self.InvalidArgumentException(
                f"Conflicting values of arguments `is_password_change_required` f{is_password_change_required} "
                f"and `can_password_be_changed` f{can_password_be_changed}")

        # Format first name, last name, and full name.
        first_name = prosoponym.format_first_name(first_name, locale=language)
        last_name = prosoponym.format_last_name(last_name, locale=language)
        if first_name and last_name:
            full_name = prosoponym.format_full_name(
                first_name,
                last_name,
                language,
                full_name=full_name,
                strict=strict_prosoponym)

        # The creation of a user account requires to pass a reCAPTCHA
        # challenge, except under the following conditions:
        #
        # * The function is explicitly requested to bypass the reCAPTCHA
        #   challenge, which option is useful for internal service usage only,
        #   when creating a new user account who authenticates with
        #   credentials on trusted 3rd party platforms, such as an OAuth
        #   access token.
        # * The environment stage of the platform is development or
        #   integration.
        # * The user account to be created is either a botnet or a test
        #   account.
        if recaptcha:
            (recaptcha_private_key, client_ip_address, recaptcha_challenge, recaptcha_response) = recaptcha
            if not recaptcha.verify(recaptcha_private_key, client_ip_address, recaptcha_challenge, recaptcha_response):
                raise self.IllegalAccessException('Incorrect reCAPTCHA response')

        if contacts:
            for contact in contacts:
                print(f"Verifying the contact {contact.property_value} ({contact.property_name})")
                is_available, is_verified = ContactService().is_contact_available(contact)
                if not is_available:
                    raise ContactService.ContactAlreadyInUseException(
                        f"The contact information {contact.property_value} is already in use")

        with self.acquire_rdbms_connection(
                auto_commit=True,
                connection=connection) as connection:

            # # Register the account with the provided information.
            # account_status = ObjectStatus.enabled if (set_enabled and (not set_pending_if_unverified_contact or verified_contacts)) \
            #         else ObjectStatus.pending

            cursor = connection.execute(
                f"""
                INSERT INTO {inherited_table_name or 'account'} (       
                    account_type,
                    app_id,         
                    can_password_be_changed,
                    does_password_never_expire,
                    is_password_change_required,
                    first_name,
                    full_name,
                    last_name,
                    language,
                    nationality,
                    object_status,
                    password,
                    username)
                  VALUES (
                    %(account_type)s,
                    %(app_id)s,  
                    %(can_password_be_changed)s,
                    %(does_password_never_expire)s,
                    %(is_password_change_required)s,
                    %(first_name)s,
                    %(full_name)s,
                    %(last_name)s,
                    %(language)s,
                    %(nationality)s,
                    %(object_status)s,
                    %(password)s,
                    %(username)s
                  )
                  RETURNING 
                    account_id,
                    language,
                    object_status,
                    creation_time
                """,
                {
                    'account_type': account_type,
                    'app_id': app_id,
                    'can_password_be_changed': can_password_be_changed,
                    'does_password_never_expire': does_password_never_expire,
                    'is_password_change_required': is_password_change_required,
                    'first_name': first_name or None,
                    'full_name': full_name,
                    'last_name': last_name or None,
                    'language': language or DEFAULT_LOCALE,
                    'nationality': nationality,
                    'object_status': ObjectStatus.enabled if enable_account else ObjectStatus.pending,
                    'password': password,
                    'username': username or None,
                })

            account = cursor.fetch_one().get_object({
                'account_id': cast.string_to_uuid,
                'creation_time': cast.string_to_timestamp,
                'language': cast.string_to_locale,
            })

            # Index the user with his full_name.
            if full_name and account_type in [
                AccountType.standard,
                AccountType.sns,
                AccountType.ghost
            ]:
                self.__index_account(
                    account.account_id,
                    full_name,
                    connection=connection)

            # Add the specified contact to the user account.
            if contacts:
                if not isinstance(contacts, (list, set, tuple)):
                    contacts = [contacts]

                for contact in contacts:
                    ContactService().add_contact(
                        account.account_id,
                        contact,
                        connection=connection,
                        context=context,
                        has_been_verified=has_been_verified,
                        language=language,
                        to_be_verified=to_be_verified,
                        verification_code_length=self.NONCE_DEFAULT_DIGIT_COUNT)

            if auto_sign_in:
                account_session = SessionService().create_session(
                    app_id,
                    account.account_id,
                    connection=connection)

                account_session.creation_time = account.creation_time
                account_session.language = account.language
                account_session.object_status = account.object_status

                self.__update_last_login_time(account.account_id, connection)

        # @todo: Remove this ugly hack with a message queue system.
        if generate_password:
            account.password = generated_password

        return account_session if auto_sign_in else account



    # @deprecated
    # def upload_avatar(
    #         self,
    #         app_id,
    #         account_id,
    #         uploaded_file,
    #         connection=None):
    #     """
    #     Upload a new picture of this user account, also known as the avatar,
    #     which is the graphical representation of the user.
    #
    #
    #     @param app_id: identification of the client application such as a Web,
    #         a desktop, or a mobile application, that accesses the service.
    #
    #     @param account_id: identification of the account of the user on behalf
    #         of whom the picture files are added to the platform.
    #
    #     @param uploaded_file: an instance `HttpRequest.HttpRequestUploadedFile`.
    #
    #     @param connection: a `RdbmsConnection` instance to be used
    #         supporting the Python clause `with ...:`.
    #
    #
    #     @return: an instance containing the following members:
    #
    #         * `file_name` (required): the original local file name as the
    #         `filename` parameter of the `Content-Disposition` header.
    #
    #         * `picture_id` (required): identification of the new avatar of the
    #             user's account as registered to the platform.
    #
    #         * `picture_url` (required): Uniform Resource Locator (URL) that
    #           specifies the location of the user's avatar.  The client application
    #           can use this URL and append the query parameter `size` to specify
    #           a given pixel resolution of the photo, such as `thumbnail`,
    #           `small`, `medium`, or `large`.
    #
    #         * `update_time` (required): time of the most recent modification of
    #           the properties of the user's account.  This information should be
    #           stored by the client application to manage its cache of user
    #           accounts.
    #
    #
    #     @raise DeletedObjectException: if the user's account has been deleted.
    #
    #     @raise DisabledObjectException: if the user's account has been
    #         disabled.
    #
    #     @raise InvalidOperationException: if the format of the uploaded image
    #         is not supported.
    #
    #     @raise UndefinedObjectException: if the specified identification
    #         doesn't refer to a user account registered to the platform.
    #     """
    #     # Retrieve the pixel resolution of the photo image, and check whether
    #     # it respects the minimal size required.  If not, ignore this photo.
    #     try:
    #         string_io_stream = io.BytesIO(uploaded_file.data)
    #         image = image_util.convert_image_to_rgb_mode(Image.open(string_io_stream))
    #         image_width, image_height = image.size
    #     except:
    #         import traceback
    #         traceback.print_exc()
    #         raise self.InvalidOperationException("Unsupported image file format")
    #
    #     # Store the watermark file in the temporary directory of the local
    #     # Network File System (NFS).  This file will be read by background task
    #     # for additional processing.
    #     with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
    #         # Register the new avatar of the user's account.
    #         picture_id = uuid.uuid1()
    #
    #         cursor = connection.execute(
    #             """
    #             UPDATE
    #                 account
    #               SET
    #                 picture_id = %(picture_id)s,
    #                 update_time = current_timestamp
    #               WHERE
    #                 account_id =%(account_id)s
    #               RETURNING
    #                 account_id,
    #                 picture_id,
    #                 object_status,
    #                 update_time
    #             """,
    #             {
    #                 'account_id': account_id,
    #                 'picture_id': picture_id
    #             })
    #         row = cursor.fetch_one()
    #         if row is None:
    #             raise self.UndefinedObjectException("The user account is not registered to the platform")
    #
    #         # Retrieve the properties of the avatar to return to the client
    #         # application.
    #         account_avatar = row.get_object({
    #             'account_id': cast.string_to_uuid,
    #             'picture_id': cast.string_to_uuid,
    #             'update_time': cast.string_to_timestamp
    #         })
    #
    #         if account_avatar.object_status == ObjectStatus.disabled:
    #             raise self.DisabledObjectException()
    #         elif account_avatar.object_status == ObjectStatus.deleted:
    #             raise self.DeletedObjectException()
    #
    #         del account_avatar.object_status
    #
    #         # Complete the properties of the watermark.
    #         account_avatar.picture_url = os.path.join(
    #             settings.CDN_URL_HOSTNAME,
    #             self.CDN_BUCKET_NAME_AVATAR,
    #             str(account_avatar.picture_id))
    #         account_avatar.file_name = uploaded_file.file_name
    #
    #         # Store the image file of the avatar to the platform's CDN.
    #         picture_path_name = os.path.join(
    #             settings.CDN_NFS_ROOT_PATH,
    #             self.CDN_BUCKET_NAME_AVATAR,
    #             file_util.build_tree_pathname(str(picture_id)))
    #
    #         file_util.make_directory_if_not_exists(picture_path_name)
    #
    #         with open(os.path.join(picture_path_name, str(picture_id)), 'wb') as handle:
    #             handle.write(uploaded_file.data)
    #
    #         # Generate multiple resolutions of the photo for various client
    #         # applications' usages.
    #         for (logical_size, scaled_image) in \
    #                 image_util.generate_multiple_pixel_resolutions(
    #                     image, settings.IMAGE_PIXEL_RESOLUTIONS['avatar'],
    #                     does_crop=True,
    #                     filter=image_util.Filter.AntiAlias):
    #             scaled_image.save(
    #                 os.path.join(
    #                     settings.CDN_NFS_ROOT_PATH,
    #                     self.CDN_BUCKET_NAME_AVATAR,
    #                     file_util.build_tree_file_pathname(f'{picture_id}_{logical_size}.jpg')),
    #                 'JPEG', quality=75)
    #
    #     return account_avatar

    def update_password_reset_request(
            self,
            request_id,
            connection=None,
            object_status=ObjectStatus.deleted):
        """
        Delete a password reset request


        @param request_id: Identification of the request of the user to reset
             his forgotten password (cf. function `request_password_reset`).

        @param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...`.

        @param object_status: An item of the enumeration `ObjectStatus`

            * `deleted`:  The request has been fulfilled.

            * `disabled`: The request has expired.
        """
        if object_status not in [ObjectStatus.deleted, ObjectStatus.disabled]:
            raise ValueError("Wrong value of the argument 'object_status'")

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            connection.execute(
                """
                UPDATE 
                    account_password_reset
                  SET
                    object_status = %(object_status)s,
                    update_time = current_timestamp
                  WHERE
                    request_id = %(request_id)s
                """,
                {
                    'object_status': object_status,
                    'request_id': request_id
                })

    def upload_picture(
            self,
            app_id,
            account_id,
            submitter_account_id,
            uploaded_file,
            connection=None,
            is_review_required=False,
            picture_minimal_size=None,
            team_id=None):
        """
        Upload a user's picture of a user


        @param app_id: The identification of the client application such as a
            Web, a desktop, or a mobile application, that accesses the service.

        @param account_id: The identification of the account of the user who
            is associated to this picture.

        @param submitter_account_id: The identification of the account of the
            user who submitted this picture.

        @param uploaded_file: An object `HttpRequest.HttpRequestUploadedFile`.

        @param connection: An object `RdmbsConnection` with auto-commit.

        @param is_review_required: Indicate whether the picture needs to be
            reviewed by someone who has authority on the online service used
            by the end users.

        @param picture_minimal_size: A tuple `width, height` specifying the
            minimal width and height of a user's picture.

        @param team_id: The identification of the organization of the user who
            submitted this picture.


        @return: An object containing the following attributes:

            * `account_id` (required): The identification of the account of the user
              this picture is associated with.

            * `picture_id` (required): The identification of the new picture.

            * `object_status` (required): An item of the enumeration `ObjectStatus`
              representing the current status of the picture.

            * `update_time` (required): The time of the most recent modification of
              the picture's status.


        @raise IllegalAccessException: If the picture has been already
            associated to another user.

        @raise PictureSizeTooSmallException: If the size of the picture is too
            small.
        """
        # Convert the uploaded file to a PIL image and check that the image is
        # of the minimal required size.
        image = self.__convert_uploaded_photo_file_to_image(uploaded_file)
        self.__validate_image_size(image, picture_minimal_size or self.DEFAULT_PICTURE_MINIMAL_SIZE)

        # Check whether this image has been previously downloaded.
        image_file_checksum = hashlib.md5(uploaded_file.data).hexdigest()
        image_file_size = len(uploaded_file.data)
        picture = self.find_picture(image_file_size, image_file_checksum, connection=connection)

        if picture:
            if picture.account_id != account_id:
                raise self.IllegalAccessException('This picture is already associated to another user')

            if picture.object_status == ObjectStatus.disabled:
                picture = self.__set_picture_status(
                    picture.picture_id,
                    ObjectStatus.enabled,
                    connection=connection)
        else:
            picture = self.__add_picture(
                app_id,
                account_id,
                submitter_account_id,
                image,
                image_file_checksum,
                image_file_size,
                connection=connection,
                is_review_required=is_review_required,
                team_id=team_id)

            if not is_review_required:
                self.__set_picture_status(picture.picture_id, ObjectStatus.enabled)

        return picture

    def __register_account(
            self,
            record,
            team_id,
            connection=None):
        """
        Register the account of a user to allow an account registration agent
        to send an email to the user providing his credentials to connect to
        the service


        @todo: Replace this ugly hack with a message queue system.

        @param record:
        @param connection:
        @param team_id:
        @return:
        """
        email_address_contact = [
            contact
            for contact in record.contacts
            if contact.property_name == ContactName.EMAIL
        ]

        email_address = email_address_contact[0].value

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            connection.execute(
                """
                INSERT INTO _account_registration (
                    account_id,
                    email_address,
                    first_name,
                    full_name,
                    last_name,
                    language,
                    password,
                    team_id
                  )
                  VALUES (
                    %(account_id)s,
                    %(email_address)s,
                    %(first_name)s,
                    %(full_name)s,
                    %(last_name)s,
                    %(language)s,
                    %(password)s,
                    %(team_id)s
                  )
                """,
            {
                'account_id': record.account_id,
                'email_address': email_address,
                'first_name': record.first_name,
                'full_name': record.full_name,
                'last_name': record.last_name,
                'language': record.language,
                'password': record.password,
                'team_id': team_id,
            }
        )

    def upsert_account(
            self,
            record,
            team_id,
            connection=None,
            strict_prosoponym=True):
        """
        Insert a new account or update an existing account depending on
        whether the contact information match

        @todo: The function doesn't support for the moment the update of an
            existing account.


        @param record: An object containing the following attributes:

            * `account_type` (optional) An item of the enumeration `AccountType`.
              Defaults to `AccountType.standard`.

            * `can_password_be_changed` (optional): Indicate whether the user can
              change his password.

            * `does_password_never_expire` (optional): Indicate whether the
              password of the user never expires.

            * `email_address` (required): email address of the user.

            * `first_name` (optional): Forename (also known as *given name*) of the
              user.

            * `full_name` (optional): Full name by which the user is known.  This
              attribute is required if the attribute `account_id` has not been given.

            * `is_password_change_required` (optional): Indicate whether user must
              change his password at the next login.

            * `last_name` (optional): Surname (also known as *family name*) of the
              user.

            * `language` (optional): An object `Locale` representing the preferred
              language of the user.

            * `password` (optional): Hash version of the password.  This attribute
              is mandatory if the attribute `account_id` is not given and if the
              attribute `account_type` is `AccountType.standard`.

            * `phone_number` (optional): Mobile phone number of the user.

            * `username` (optional): Username to associate with the user account.
              The bulk operation for this user account will fail if this username
              already exists and the attribute `account_id` is not given or if this
              username is associated to another user account.

        @param team_id: Identification of the organization that creates this
            user account.

        @param connection: An object `RdbmsObject` with auto commit.

        @param strict_prosoponym: Indicate whether the function must verify
            if the full name of a user matches the first and the last name of
            this user.


        @return: An object containing information about the account.
        """
        if not record.contacts:
            raise ValueError("Missing contact information of the user")

        email_address_contact = [
            contact
            for contact in record.contacts
            if contact.property_name == ContactName.EMAIL
        ]

        if len(email_address_contact) != 1:
            raise ValueError("Zero or multiple email addresses")

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            account = ContactService().find_account(email_address_contact[0], connection=connection)

            if account:
                pass  # @todo: Complete this feature.
            else:
                account = self.sign_up(
                    account_type=AccountType.standard,
                    auto_sign_in=False,
                    connection=connection,
                    contacts=record.contacts,
                    enable_account=True,
                    has_been_verified=False,
                    first_name=record.first_name,
                    full_name=record.full_name,
                    last_name=record.last_name,
                    language=record.language,
                    strict_prosoponym=strict_prosoponym,
                    team_id=team_id,
                )

                # @todo: Remove this ugly hack with a message queue system.
                record.account_id = account.account_id
                record.password = account.password
                self.__register_account(record, team_id, connection=connection)

            return account
