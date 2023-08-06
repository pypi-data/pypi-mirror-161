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

import collections
import hashlib
import io
import os
import traceback
import uuid

from PIL import Image
from majormode.perseus.constant.team import MemberRole
from majormode.perseus.constant.contact import ContactName
from majormode.perseus.constant.obj import ObjectStatus
from majormode.perseus.service.account.account_service import AccountService
from majormode.perseus.service.base_rdbms_service import BaseRdbmsService
from majormode.perseus.service.base_service import BaseService
from majormode.perseus.utils import cast
from majormode.perseus.utils import file_util
from majormode.perseus.utils import image_util
from majormode.perseus.utils import key_util
from majormode.perseus.utils import string_util

import settings


# Default file extensions per image file format.  When not defined, the
# file extension is named after the image file format.
DEFAULT_IMAGE_FILE_FORMAT_EXTENSIONS = {
    'JPEG': 'jpg'
}


class TeamService(BaseRdbmsService):
    """

    """
    # Define the name of the Content Delivery Network (CDN) bucket that
    # groups teams' logos.
    DEFAULT_CDN_BUCKET_NAME_LOGO = 'logo'

    # Define the path to the default letter to be sent to user who is
    # invited to join a team.
    DEFAULT_INVITE_EMAIL_FILE_PATH_NAME = os.path.join(
        os.path.normpath(os.path.dirname(__file__)),
        'template', 'default_invitation_email.txt')

    # Default image file format to store the logo of a team with (cf.
    # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).
    DEFAULT_LOGO_IMAGE_FILE_FORMAT = 'JPEG'

    # Default quality to store the image of a team's logo with, on a scale
    # from `1` (worst) to `95` (best).  Values above `95` should be avoided;
    # `100` disables portions of the JPEG compression algorithm, and results
    # in large files with hardly any gain in image quality.
    DEFAULT_LOGO_IMAGE_QUALITY = 75

    # Default minimal size of the image of a team's logo.
    DEFAULT_LOGO_IMAGE_MINIMAL_SIZE = (400, 400)

    # Define the default time interval between two consecutive sending
    # email to remind a user that he has been invited to join a team.
    # This time is expressed in days.
    DEFAULT_TIME_INTERVAL_BETWEEN_SENDING_INVITE_REMINDER = 2

    # Define the character used to separate the invitation identification from
    # the invitation nonce.  The whole string correspond to the invite
    # security key that is sent to the user who is invited to join at
    # team.
    INVITE_KEY_NONCE_SEPARATOR = '.'

    # Define the maximum number of times an invitation can be sent to a
    # user to join a team before this invitation is soft-deleted as the user
    # doesn't reply.
    MAXIMUM_SENDING_INVITE_REMINDER_COUNT = 3

    @staticmethod
    def __build_picture_file_path_name(
            picture_id,
            root_path,
            image_file_format,
            logical_size):
        """
        Return the path and name of a picture stored in the local CDN.


        :param picture_id: Identification of the picture of an account.

        :param root_path: Absolute root path where the image files of team
            logos are stored into.

        :param image_file_format: File format to store the image with  (cf.
            https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).

        :param logical_size: A string representation of the image size, such
            as "thumbnail", "small", "medium", and "large".


        :return: A string representing the path and name of an image file.
        """
        # Name the file against its identification and its logical size.
        file_name = f'{str(picture_id)}_{logical_size}'

        # Create the path of the folder where the image file will be stored in.
        path = os.path.join(
            root_path,
            file_util.build_tree_pathname(file_name))

        # Add the extension to the file depending on the image format.
        file_extension = DEFAULT_IMAGE_FILE_FORMAT_EXTENSIONS.get(image_file_format) or image_file_format.lower()

        # Build the absolute path and name of the image file.
        file_path_name = os.path.join(path, f'{file_name}.{file_extension}')

        return file_path_name

    @staticmethod
    def __get_multiple_pixel_resolutions(bucket_name):
        """
        Return the multiple pixel resolutions of the scaled-down raster images
        to be generated


        :param bucket_name: The name of the bucket where multiple pixel
            resolutions of the scaled-down raster images will be stored in.
            It corresponds to the name of a Content Delivery Network (CDN)
            bucket.


        :return: A List of tuple `(width, height, logical image size)` where:

            * `width`: Positive integer corresponding to the number of pixel columns
              of the image.

            * height: positive integer corresponding to the number of pixel rows.

            * logical image size: string representation of the image size, such as
             'thumbnail', 'small', 'medium', and 'large'.
        """
        resolutions = settings.IMAGE_PIXEL_RESOLUTIONS[bucket_name] or settings.IMAGE_PIXEL_RESOLUTIONS[None]
        return resolutions

    @classmethod
    def __load_image_from_bytes(cls, data):
        """
        Load an image from a bytes-like object.


        :param data: A bytes-like object that contains the image's data.


        :return: An object `PIL.Image`.


        :raise InvalidArgumentException: If the format of the image is not
            supported.
        """
        try:
            bytes_stream = io.BytesIO(data)
            image = image_util.convert_image_to_rgb_mode(Image.open(bytes_stream))
        except:
            traceback.print_exc()
            raise cls.InvalidArgumentException("Unsupported image file format")

        return image

    @classmethod
    def __save_multiple_resolution_logo_files(
            cls,
            picture_id,
            image,
            resolutions,
            image_file_format=DEFAULT_LOGO_IMAGE_FILE_FORMAT,
            image_quality=DEFAULT_LOGO_IMAGE_QUALITY):
        """
        Generate multiple resolutions of the logo's image.


        :param picture_id: Identification of the logo.

        :param image: An object `PIL.Image` corresponding to the logo's image.

        :param resolutions: An array of pixel resolutions of the scaled-down
            JPEG raster images to be generated:

               [
                 (width, height, logical_size),
                 ...
               ]

            where:

            - width: Positive integer corresponding to the number of pixel colunms
              of the image.

            - height: Positive integer corresponding to the number of pixel rows.

            - logical_size (string): String representation of the image size, such
              as "thumbnail", "small", "medium", and "large".

        :param image_file_format: Image file format to store the image with
            (cf. https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).

        :param image_quality: The image quality to store locally, on a scale from `1`
            (worst) to `95` (best).  Values above `95` should be avoided; `100`
            disables portions of the JPEG compression algorithm, and results
            in large files with hardly any gain in image quality.
        """
        for logical_size, scaled_image in image_util.generate_multiple_pixel_resolutions(
                image,
                resolutions,
                does_crop=True,
                filter=image_util.Filter.AntiAlias):
            scaled_image.save(
                cls.__build_picture_file_path_name(
                    picture_id,
                    os.path.join(settings.CDN_NFS_ROOT_PATH, cls.DEFAULT_CDN_BUCKET_NAME_LOGO),
                    image_file_format,
                    logical_size),
                image_file_format,
                quality=image_quality)

    @classmethod
    def __store_logo_image_file(
            cls,
            picture_id,
            image,
            image_file_format=DEFAULT_LOGO_IMAGE_FILE_FORMAT,
            image_quality=DEFAULT_LOGO_IMAGE_QUALITY):
        """
        Store the image of a team's logo onto the Network File System (NFS)

        The function generates the multiple resolutions of this image.


        :param picture_id: The identification of the team's logo.

        :param image: An object `PIL.Image`.

        :param image_file_format: Image file format to store the image with
            (cf. https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).

        :param image_quality: The image quality to store locally, on a scale from `1`
            (worst) to `95` (best).  Values above `95` should be avoided; `100`
            disables portions of the JPEG compression algorithm, and results
            in large files with hardly any gain in image quality.
        """
        # Create the path of the folder to store the image file in.
        path = os.path.join(
            settings.CDN_NFS_ROOT_PATH,
            cls.DEFAULT_CDN_BUCKET_NAME_LOGO,
            file_util.build_tree_pathname(str(picture_id)))

        file_util.make_directory_if_not_exists(path)

        # Retrieve the multiple pixel resolutions of the images to generate.
        resolutions = cls.__get_multiple_pixel_resolutions(cls.DEFAULT_CDN_BUCKET_NAME_LOGO)

        # Generate and store the multiple pixel resolutions of the images of
        # this logo.
        cls.__save_multiple_resolution_logo_files(
            picture_id,
            image,
            resolutions,
            image_file_format=image_file_format,
            image_quality=image_quality)

    @classmethod
    def __validate_image_size(cls, image, minimal_size):
        """
        Validate the resolution of the image of the new logo of a team.


        :param image: An object `PIL.Image`.

        :param minimal_size: A tuple of two integers `(width, height)`
            representing the minimal size of the image of a photo.


        :raise InvalidArgumentException: If the image is too small, or if the
            image dimension is not in a square aspect ratio.
        """
        image_width, image_height = image.size
        min_width, min_height = minimal_size

        if (image_width < min_width and image_height < min_height) or \
           (image_width < min_height and image_height < min_width):
            raise cls.InvalidArgumentException(f"Image is too small: minimal size is {min_width}x{min_height}")

        if image_width != image_height:
            raise cls.InvalidArgumentException("Image dimensions must be in a square aspect ratio")

    def add_member(
            self,
            account_id,
            team_id,
            role,
            connection=None):
        """
        Add a user to a team


        :warning: This function MUST NOT be surfaced to any client application.
            Its usage is for internal services only.


        :param team_id: Identification of an existing organization.

        :param account_id: Identification of an account of a user to add as a
            member of the specified organization.

        :param role: Role of the member within the organization.

        :param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...`.


        :raise InvalidOperationException: If the user is already a member of
            the specified team but with another role.
        """
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            # Check that the team exists.
            self.get_team(team_id, check_status=True, connection=connection)

            # Check whether the specified user is not already a member of this team.
            try:
                existing_role = self.get_member_role(
                    account_id,
                    team_id)
            except self.InvalidArgumentException:  # The user is not member of this team.
                existing_role = None

            # Add the user to the team, when not already added.
            if existing_role is None:
                connection.execute(
                    """
                    INSERT INTO team_member(
                        team_id,
                        account_id,
                        role)
                      VALUES (
                        %(team_id)s,
                        %(account_id)s,
                        %(role)s
                      )
                    """,
                    {
                        'account_id': account_id,
                        'role': role,
                        'team_id': team_id,
                    }
                )

            # Otherwise check that this user has been already added to this team
            # with the same role.
            elif existing_role != role:
                raise self.InvalidOperationException("This user is already a member of the team but with another role")

    def assert_member(
            self,
            account_id,
            team_id,
            check_status=False,
            connection=None):
        """
        Assert that the specified user is a member of the team, or a botnet or
        an administrator of the platform, and raise an exception if this
        assertion is not verified.


        :param account_id: Identification of the account of a user to check
            whether he is a member of the team.

        :param team_id: Identification of a team.

        :param check_status: Indicate whether the membership of this user must
            be active.

        :param connection: An `RdbmsConnection` object that supports the
            Python clause `with ...:`.


        :raise IllegalAccessException: If the specified user is not a member
            of the team, or if the membership of this user has been disabled.
        """
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    object_status
                  FROM 
                    team_member
                  WHERE 
                    team_id = %(team_id)s
                    AND account_id = %(account_id)s
                """,
                {
                    'account_id': account_id,
                    'team_id': team_id,
                }
            )

            row = cursor.fetch_one()
            if row is None:
                raise self.IllegalAccessException(f"The user {account_id} is not a member of the team {team_id}")

            if check_status:
                # Check that the membership of the user in the organization is enabled.
                membership_status = row.get_value('object_status', ObjectStatus)
                if membership_status != ObjectStatus.enabled:
                    raise self.IllegalAccessException(
                        f"The membership of the user {account_id} in the organization {team_id} is not enabled")

                # Check that the account of the user is enabled.
                AccountService().get_account(account_id, check_status=True, include_contacts=False)

    def assert_member_role(
            self,
            account_id,
            team_id,
            roles,
            connection=None):
        """
        Assert that a user has one of the specified roles.


        :param account_id: Identification of the account of a user to check
            whether he has the role of administrator for the specified team.

        :param team_id: Identification of a team.

        :param roles: A string or a list of strings representing one or more
            role, or an item or a list of items of the `MemberRole`
            enumeration.

        :param connection: An `RdbmsConnection` object that supports the
            Python clause `with ...:`.


        :raise IllegalAccessException: If the specified user has none of the
            specified roles.
        """
        if not isinstance(roles, (list, set, tuple)):
            roles = [roles]

        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    true
                  FROM 
                    team_member
                  WHERE
                    team_id = %(team_id)s
                    AND account_id = %(account_id)s
                    AND role IN (%(roles)s)
                """,
                {
                    'roles': roles,
                    'account_id': account_id,
                    'team_id': team_id
                })

            if cursor.get_row_count() == 0:
                raise self.IllegalAccessException(f"the user {account_id} is not {'/'.join([str(role) for role in roles])} of the team")

        return True

    @classmethod
    def build_picture_url(cls, picture_id):
        """
        Return the Uniform Resource Locator of a team's logo.


        :param picture_id: Identification of the logo of a team.


        :return: A string representing the Uniform Resource Locator of the
            team's logo.
        """
        return picture_id and os.path.join(
            settings.CDN_URL_HOSTNAME,
            cls.DEFAULT_CDN_BUCKET_NAME_LOGO,
            str(picture_id))

    def get_account_teams(
            self,
            account_id,
            connection=None,
            limit=BaseRdbmsService.DEFAULT_LIMIT,
            offset=0):
        """
        Return a list of teams that a user belongs to.


        :param account_id: Identification of the account of a user.

        :param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...`.

        :param limit: Constrain the number of teams that are returned to the
            specified number.

        :param offset: Require to skip that many teams before beginning to
            return teams.


        :return: A list of object containing the following members:

            * `account_id` (required): Identification of the account of the agent
              of this team.

            * `creation_time`: Date and time when the team has been registered.

            * `description` (optional): A short textual description of the team.

            * `name` (required): Name of the team.

            * `picture_id` (optional): Identification of the logo that represents
              the team.

            * `picture_url` (optional): Uniform Resource Locator (URL) that
              specifies the location of the team's logo.

            * `role` (required): Role of the user in the organization.

            * `team_id` (required): Identification of a team.
        """
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    team.account_id,
                    team.creation_time,
                    team.description,
                    team.name,
                    team.picture_id,
                    team_member.role,
                    team.team_id
                  FROM
                    team_member
                  INNER JOIN team
                    USING (team_id)
                  WHERE 
                    team_member.account_id = %(account_id)s
                    AND team_member.object_status = %(OBJECT_STATUS_ENABLED)s
                    AND team.object_status = %(OBJECT_STATUS_ENABLED)s
                  ORDER BY 
                    team.creation_time DESC
                  LIMIT %(limit)s
                  OFFSET %(offset)s
                """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'account_id': account_id,
                    'limit': min(limit or self.DEFAULT_LIMIT, self.MAXIMUM_LIMIT),
                    'offset': offset
                })

            teams = [
                row.get_object({
                    'account_id': cast.string_to_uuid,
                    'creation_time': cast.string_to_timestamp,
                    'picture_id': cast.string_to_uuid,
                    'team_id': cast.string_to_uuid
                })
                for row in cursor.fetch_all()
            ]

            # Build the Uniform Resource Locator (URL) that specifies the location
            # of the picture representing the team.
            for team in teams:
                team.picture_url = self.build_picture_url(team.picture_id)

            return teams

    def get_members(
            self,
            team_id,
            connection=None,
            include_deleted=False,
            include_disabled=False,
            limit=None,
            offset=0,
            roles=None,
            sync_time=None):
        """
        Return the list of the members of a team.


        :note: The user on behalf of whom the function is called must be an
            administrator of the team.


        :param team_id: Identification of a team.

        :param connection: An `RdbmsConnection` object that supports the
            Python clause `with ...:`.

        :param include_deleted: Indicate whether to return also members that
            have been recently removed from the team (soft-deleted).

        :param include_disabled: Indicate whether to return also members that
            are currently suspended from the team.

        :param limit: Constrain the number of members that are returned to the
            specified number.

        :param offset: Require to skip that many members before beginning to
            return members.

        :param roles: A string or a list of strings representing one or more
            role, or an item or a list of items of the `MemberRole`
            enumeration, to filter the list of members.

        :param sync_time: Earliest non-inclusive time to filter members based
            on the time of the last modification of their attributes.  If not
            specified, no time filter is applied; all the members are returned.


        :return: An array of objects containing the following attributes:

            * `account_id`: Identification of the account of a member.

            * `object_status`: An item of the enumeration `ObjectStatus`

            * `role`: Role of this member in the team.


        :raise DeletedObjectException: If the team has been deleted.

        :raise DisabledObjectException: If the team has been disabled.

        :raise IllegalAccessException: If the user on behalf of the function
            is called is not an administrator of the team.

        :raise UndefinedObjectException: If the specified identification
            doesn't refer to a team registered against the platform.
        """
        if roles and not isinstance(roles, (list, set, tuple)):
            roles = [roles]

        # Check that the team exists.
        self.get_team(team_id, check_status=True)

        # # Check that the user on behalf of whom the function is called must be
        # # an administrator of the team.
        # self.assert_member_role(account_id, team_id, MemberRole.administrator)

        # Retrieve a list of members of the team.
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    account_id,
                    team_member.object_status,
                    role
                  FROM
                    team_member
                  INNER JOIN account
                    USING (account_id)
                  WHERE
                    team_id = %(team_id)s
                    AND (team_member.object_status = %(OBJECT_STATUS_ENABLED)s
                         OR (%(include_deleted)s AND team_member.object_status = %(OBJECT_STATUS_DELETED)s)
                         OR (%(include_disabled)s AND team_member.object_status = %(OBJECT_STATUS_DISABLED)s))
                    AND account.object_status = %(OBJECT_STATUS_ENABLED)s
                    AND ((%(roles)s) IS NULL OR role IN (%(roles)s))
                    AND (%(sync_time)s IS NULL OR account.update_time > %(sync_time)s) 
                  ORDER BY
                    account.update_time ASC
                  LIMIT %(limit)s
                  OFFSET %(offset)s
                """,
                {
                    'OBJECT_STATUS_DELETED': ObjectStatus.deleted,
                    'OBJECT_STATUS_DISABLED': ObjectStatus.disabled,
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'include_deleted': include_deleted,
                    'include_disabled': include_disabled,
                    'limit': min(limit or self.DEFAULT_LIMIT, self.MAXIMUM_LIMIT),
                    'offset': offset,
                    'roles': roles,
                    'sync_time': sync_time,
                    'team_id': team_id,
                })

            members = [
                row.get_object({
                    'account_id': cast.string_to_uuid,
                    'object_status': ObjectStatus
                })
                for row in cursor.fetch_all()
            ]

            return members





























    # def get_invitation_code(self, team_id, account_id):
    #     """
    #     Return the invitation code that needs to be sent to a user who is
    #     invited to join a team.
    #
    #
    #     @note: this function is intended to be used by unit tests only.
    #
    #
    #     @warning: this function MUST not be surfaced to client application and
    #         it MUST not be used by any other services.
    #
    #     :param team_id: Identification of a team the user has been invited to
    #         join.
    #     :param account_id: Identification of the account of the user who has
    #         been invited to join the specified team.
    #
    #     :return: the invitation code that needs to be sent to the user who is
    #         invited to join the team.
    #
    #     :raise DeletedObjectException: If the account has been deleted.
    #     :raise DisabledObjectException: If the account has been disabled.
    #     :raise IllegalAccessException: If the account is not used for unit
    #        test purpose.
    #     :raise UndefinedObjectException: If the specified identification
    #        doesn't refer to a user account registered against the
    #        platform, or if if the user has not been invited to join
    #        the given team.
    #     """
    #     account = AccountService().get_account(account_id, check_status=True)
    #     if account.account_type != AccountService.AccountType.test:
    #         raise self.IllegalAccessException("This function can be used with test account only")
    #
    #     with self.acquire_rdbms_connection() as connection:
    #         cursor = connection.execute(
    #             """
    #             SELECT
    #                 invitation_id,
    #                 invitation_nonce
    #               FROM
    #                 team_membership_invitation
    #               WHERE
    #                 team_id = %(team_id)s
    #                 AND account_id = %(account_id)s
    #                 AND object_status = %(OBJECT_STATUS_ENABLED)s
    #             """,
    #             {
    #                 'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
    #                 'account_id': account_id,
    #                 'team_id': team_id
    #             })
    #         row = cursor.fetch_one()
    #         if row is None:
    #             raise self.UndefinedObjectException('The user has not been invited to join this team')
    #
    #         invitation = row.get_object()
    #         return '%s%s%s' % (key_util.int_to_key(invitation.invitation_id),
    #                            TeamService.INVITE_KEY_NONCE_SEPARATOR,
    #                            invitation.invitation_nonce)

    def get_invitations(
            self,
            offset=0,
            limit=BaseRdbmsService.DEFAULT_LIMIT,
            time_interval_between_invitation_reminder=DEFAULT_TIME_INTERVAL_BETWEEN_SENDING_INVITE_REMINDER):
        """
        Return a list of invitations to be sent to members who were invited to
        join a team.


        @warning: This function is for internal usage only; it MUST not be
            surfaced to any client applications.


        :param offset: Require to skip that many invitations before beginning
            to return invitations.

        :param limit: Constrain the number of invitations that are returned to
            the specified number.

        :param time_interval_between_invitation_reminder: Time interval
            between two consecutive sending email to remind a user that he has
            been invited to join a team.  This time is expressed in days.


        :return A list of instances containing the following members:

            * `account_id`: Identification of the account of the user who is invited
              to join the team.

            * `attempt_count`: Number of times the platform notified the user from
              the invitation to join the team.  After a certain number of time, the
              invitation may be cancelled.

            * `recipient_name`: Name of the user who is invited to join the team.
            * `email_address`: email address of the user who is invited to
              join the team.

            * `invitation_code`: Invitation code that has been sent to the user to
              join the team.

            * `invitation_email`: Template of the letter to send by email to the
              user who is invited to join the team.  If no specific template is
              defined for this team, the platform provides a default template.

            * `invitation_id`: Identification number of the invitation that has
              been sent to this user to join the team.

            * `invitation_nonce`: "Number used once", a pseudo-random number issued
              when generating the invitation key to ensure that this key cannot be
              reused in replay attacks.

            * `invitation_url`: Uniform Resource Locator (URL) that is provided as a
              link in the email the platform sends to a user who is invited to join
              the team.  When the user clicks on the link embedded in the email, the
              email reader application issues a HTTP GET request to this URL.

            * `team_id`: Identification of the team this user is invited to join.

            * `sender_name`: Name of the administrator of the team who invited the
              user to join this team.

            * `team_name`: Name of the team this user is invited to join.
        """
        default_invitation_email = None

        with self.acquire_rdbms_connection(auto_commit=True) as connection:
            # Delete invitations that have expired after having been sent the
            # maximum allowed.
            connection.execute(
                """
                UPDATE
                    team_membership_invitation
                  SET
                    object_status = %(OBJECT_STATUS_DELETED)s,
                    update_time = current_timestamp
                  WHERE
                    attempt_count >= %(MAXIMUM_SENDING_INVITE_REMINDER_COUNT)s
                    AND update_time <= current_timestamp - %(time_interval)s * '1 day'::interval
                """,
                {
                    'MAXIMUM_SENDING_INVITE_REMINDER_COUNT': TeamService.MAXIMUM_SENDING_INVITE_REMINDER_COUNT,
                    'OBJECT_STATUS_DELETED': ObjectStatus.deleted,
                    'time_interval': time_interval_between_invitation_reminder
                })

            # Retrieve a list of invitation to send to users as a reminder they have
            # been invited to join a team.
            cursor = connection.execute(
                """
                SELECT
                    invitation_id,
                    invitation_nonce,
                    team_id,
                    name AS team_name,
                    team_membership_invitation.account_id,
                    get_account_name(team_membership_invitation.account_id) AS recipient_name,
                    email_address,
                    get_account_name(team_membership_invitation.originator_id) AS sender_name,
                    invitation_url,
                    invitation_email,
                    attempt_count
                  FROM
                    team_membership_invitation
                  INNER JOIN account
                    ON account.account_id = team_membership_invitation.account_id
                  INNER JOIN team
                    USING (team_id)
                  WHERE 
                    team_membership_invitation.object_status = %(OBJECT_STATUS_ENABLED)s
                    AND team_membership_invitation.update_time <= current_timestamp - %(time_interval)s * '1 day'::interval
                  ORDER BY 
                    attempt_count ASC,
                    team_membership_invitation.creation_time ASC
                  OFFSET %(offset)s
                  LIMIT %(limit)s
                """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'limit': limit,
                    'offset': offset,
                    'time_interval': time_interval_between_invitation_reminder
                })

            invitations = [
                row.get_object({
                    'account_id': cast.string_to_uuid,
                    'team_id': cast.string_to_uuid })
                for row in cursor.fetch_all()
            ]

            for invitation in invitations:
                invitation.invitation_code = '%s%s%s' % \
                    (key_util.int_to_key(invitation.invitation_id),
                     TeamService.INVITE_KEY_NONCE_SEPARATOR,
                     invitation.invitation_nonce)

                if invitation.invitation_email is None:
                    if default_invitation_email is None:
                        with open(self.DEFAULT_INVITE_EMAIL_FILE_PATH_NAME) as file:
                            default_invitation_email = file.read()
                    invitation.invitation_email = default_invitation_email

            return invitations

    def set_member_status(
            self,
            team_id,
            account_id,
            object_status,
            connection=None):
        """
        Suspend or reactive a member of an organization.


        :param team_id: Identification of an organization.

        :param account_id: Identification of a member of this organization.

        :param object_status: An item of the enumeration `ObjectStatus`:

            * `disabled`: To suspend the account of this member.

            * `enabled`: To restore the account of this member.

        :param connection: An object `RdbmsConnection` with auto commit.


        :return: An object containing the following attributes:

            * `account_id` (required): Identification of the member's account.

            * `object_status` (required): Current status of the member's account.

            * `update_time` (required): Time of the most recent modification of
              the properties of the member's account.


        :raise IllegalAccessException: If the specified account is not a
            member of the organization.

        :raise InvalidArgumentException: If the argument `object_status` is
            not a valid value.

        :raise InvalidOperationException: If the member's account already in
            the desired status.
        """
        if object_status not in [ObjectStatus.disabled, ObjectStatus.enabled]:
            raise self.InvalidArgumentException("Invalid member account's new status")

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            self.assert_member(account_id, team_id, connection=connection)

            cursor = connection.execute(
                """
                UPDATE
                    team_member
                  SET
                    object_status = %(object_status)s,
                    update_time = current_timestamp
                  WHERE
                    account_id = %(account_id)s
                    AND team_id = %(team_id)s
                    AND object_status <> %(object_status)s
                  RETURNING
                    account_id,
                    object_status,
                    update_time
                """,
                {
                    'account_id': account_id,
                    'object_status': object_status,
                    'team_id': team_id,
                }
            )

            row = cursor.fetch_one()
            if row is None:
                raise self.InvalidOperationException(
                    f"This member is already {'activated' if object_status == ObjectStatus.enabled else 'suspended'}")

            account = row.get_object({
                'account_id': cast.string_to_uuid,
                'object_status': ObjectStatus,
                'update_time': cast.string_to_timestamp,
            })

            return account

    def _get_team_administrator_account_ids(self, team_id):
        """
        Return the list of accounts of users who are the administrators of the
        specified team.


        :param team_id: Identification of a team.


        :return: a list of account identifications of the administrators of
            this team.
        """
        with self.acquire_rdbms_connection(False) as connection:
            cursor = connection.execute("""
                SELECT account_id
                  FROM team_member
                  WHERE team_id = %(team_id)s
                    AND role = 'administrator'
                    AND object_status = %(OBJECT_STATUS_ENABLED)s""",
                { 'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                  'team_id': team_id })

            return [ row.get_value('account_id', cast.string_to_uuid)
                     for row in cursor.fetch_all() ]


    def _get_team_members(self, team_id):
        """
        Return the list of accounts of users who belong to the specified team.


        :param team_id: Identification of a team.


        :return: a list of instances, each instance contains the following
            members:

            * `account_id`: Identification of a member of the team.

            * `is_administrator`: Indicate whether this member is an
               administrator of the team.
        """
        with self.acquire_rdbms_connection(False) as connection:
            cursor = connection.execute("""
                SELECT account_id,
                       role = 'is_administrator'
                  FROM team_member
                  WHERE team_id = %(team_id)s
                    AND object_status = %(OBJECT_STATUS_ENABLED)s""",
                { 'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                  'team_id': team_id })
            return [ row.get_object({ 'account_id': cast.string_to_uuid })
                     for row in cursor.fetch_all() ]


    def accept_invitation(self, app_id, invitation_code, account_id=None):
        """
        Accept on behalf of an user an invitation that an administrator of
        a team sent to this user to join this team.

        @note: a user can accept am invitation that he has refused a first
            time, as long as this request has not be hard-deleted by a
            background task.  This is a supported feature, not a bug.

        :param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.
        :param invitation_code: Invitation_code sent to a user to join a team.
        :param account_id: the identification of the account of the user who
            receives the invitation to join the team.  This information might
            not be available if the user has not registered an account against
            the platform yet, i.e., the user has still a ghost account.

        :raise DeletedObjectException: If the team has been deleted.
        :raise DisabledObjectException: If the team has been disabled.
        :raise IllegalAccessException: If the nonce included in the invitation
            code is invalid, or if the account identification is specified but
            it is not the recipient of the invitation.
        :raise InvalidArgumentException: If the invitation code is of a wrong
            format.
        :raise UndefinedObjectException: If no invitation corresponds to the
            specified code.
        """
        with self.acquire_rdbms_connection(True) as connection:
            try:
                (invitation_id, _, invitation_nonce) = key_util.parse_secured_key(invitation_code)
            except ValueError as exception:
                self.log_debug(str(exception))
                raise self.InvalidArgumentException("Invalid invitation code")

            # Note: do not test whether the invitation has been soft-deleted,
            # i.e., whether the user has declined this invitation a first time, so
            # that he can still accept it.
            cursor = connection.execute(
                """
                DELETE FROM 
                    team_membership_invitation
                  WHERE
                    invitation_id = %(invitation_id)s
                  RETURNING
                    team_id,
                    account_id,
                    role = 'administrator',
                    invitation_nonce
                """,
                {
                    'invitation_id': invitation_id
                })
            row = cursor.fetch_one()
            if row is None:
                raise self.UndefinedObjectException()

            invitation = row.get_object({
                'account_id': cast.string_to_uuid,
                'team_id': cast.string_to_uuid
            })

            if invitation_nonce != invitation.invitation_nonce:
                raise self.IllegalAccessException("The invitation code has been corrupted")

            if account_id is not None and account_id != invitation.account_id:
                raise self.IllegalAccessException('The user is not the recipient of this invitation')

            # Check that the team is still enabled.
            self.get_team(invitation.team_id, check_status=True)

            # Add the user as a new member of the team.
            connection.execute(
                """
                INSERT INTO team_member(
                    team_id,
                    account_id,
                    is_administrator)
                  VALUES (
                    %(team_id)s,
                    %(account_id)s,
                    %(is_administrator)s)
                """,
                {
                    'account_id': invitation.account_id,
                    'is_administrator': invitation.is_administrator,
                    'team_id': invitation.team_id
                })

    def create_team(
            self,
            account_id,
            name,
            connection=None,
            description=None,
            invitation_email=None,
            invitation_url=None,
            is_name_unique=False):
        """
        Create a team on behalf of a user

        This user becomes the agent of this team, the super administrator.  He
        can delete the team.  He can promote any administrator of the team to
        be the new agent of this team.


        :param account_id: Identification of the account of a user who creates
            the team.

        :param name: Name of the team.

        :param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...`.

        :param description: a short textual description of the team, if any
            provided.

        :param invitation_url: Uniform Resource Locator (URL) that is provided
            as a link in the email the platform sends to a user who is invited
            to join the team.  When the user clicks on the link embedded in
            the email, the email reader application issues a HTTP GET request
            to this URL.

        :param invitation_email: Template of the letter to be sent by email to
            a user who is invited to join a team.  If no specific template is
            specified for this team, the platform provides a default
            template located in `./template/invitation_default_email.txt`,
            relative to the path of the team service Python module.

        :param is_name_unique: Indicate whether the name of the team MUST be
            unique among all the teams that have been registered so far to the
             server platform.  Case is not sensitive.


        :raise DeletedObjectException: If the user account has been deleted.

        :raise DisabledObjectException: If the user account has been disabled.

        :raise InvalidIOperationException: If the name of the team passed to
            this function is already registered for an other team.

        :raise UndefinedObjectException: If the specified identification
            doesn't refer to a user account registered against the platform.
        """
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            # Retrieve information about the account that is registering this
            # team, and check whether the current status of this account allows
            # him to register a team.
            AccountService().get_account(account_id, check_status=True, connection=connection)

            # Check whether the team's name is available when its uniqueness is
            # required.
            if is_name_unique and not self.is_name_available(name, connection=connection):
                raise self.InvalidOperationException(f'A team already exist with the name "{name}"')

            # Create the team with the information passed to the function.
            cursor = connection.execute(
                """
                INSERT INTO team(
                    name,
                    description,
                    invitation_url,
                    invitation_email,
                    account_id)
                  VALUES (
                    %(name)s,
                    %(description)s,
                    %(invitation_url)s,
                    %(invitation_email)s,
                    %(account_id)s
                  )
                  RETURNING 
                    creation_time,
                    team_id
                """,
                {
                    'account_id': account_id,
                    'description': description,
                    'invitation_email': invitation_email,
                    'invitation_url': invitation_url,
                    'name': name,
                })

            row = cursor.fetch_one()
            team = row.get_object({
                'creation_time': cast.string_to_timestamp,
                'team_id': cast.string_to_uuid
            })

            # Add the user to the team with a role of administrator.
            connection.execute(
                """
                INSERT INTO team_member(
                    team_id,
                    account_id,
                    role)
                  VALUES (
                    %(team_id)s,
                    %(account_id)s,
                    %(role)s
                  )
                """,
                {
                    'account_id': account_id,
                    'role': MemberRole.administrator,
                    'team_id': team.team_id
                })

            return team

    def cancel_invitation(self, app_id, account_id, invitation_id):
        """
        Cancel an invitation sent to a user to join a team.

        @note: only an administrator of the team is allowed to cancel an
            invitation.

        :param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.
        :param account_id: Identification of the account of an administrator
            of the team.
        :param invitation_id: Identification of the invitation that has been sent
            to a user.

        :raise DeletedObjectException: If the team has been deleted.
        :raise DisabledObjectException: If the team has been disabled.
        :raise IllegalAccessException: If the specified user is not an
            administrator of the team from which the invitation has been issued.
        :raise UndefinedObjectException: If no invitation to join a team
            corresponds to the specified identification.
        """
        with self.acquire_rdbms_connection(True) as connection:
            cursor = connection.execute("""
                UPDATE team_membership_invitation
                  SET object_status = %(OBJECT_STATUS_DELETED)s,
                      update_time = current_timestamp
                  WHERE invitation_id = %(invitation_id)s
                  RETURNING team_id""",
                { 'OBJECT_STATUS_DELETED': ObjectStatus.deleted,
                  'invitation_id': invitation_id })
            row = cursor.fetch_one()
            if row is None:
                raise self.UndefinedObjectException('No invitation corresponds to the specified identification')

            team_id = row.get_value('team_id', cast.string_to_uuid)
            self.assert_administrator(account_id, team_id)

    def decline_invite(self, app_id, invitation_code):
        """
        Decline an invitation on behalf of the user who was invited to join a
        team.

        :param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.
        :param invitation_code: the code of an invitation to join a team,
            composed of the invitation's plain key and a nonce, "number used
            once", i.e., a pseudo-random number to ensure that the key cannot
            be reused in replay attacks.

        :raise DeletedObjectException: If the team has been deleted.
        :raise DisabledObjectException: If the team has been disabled.
        :raise IllegalAccessException: If the nonce of the invitation passed
            to this function doesn't correspond to the real nonce of the
            invitation.
        :raise InvalidArgumentException: If the invitation's secured key is
            of a wrong format.
        :raise UndefinedObjectException: If no invitation corresponds to the
            specified secured key.
        """
        try:
            (invitation_id, _, invitation_nonce) = key_util.parse_secured_key(invitation_code)
        except ValueError as exception:
            self.log_debug(str(exception))
            raise self.InvalidArgumentException('Invalid code invitation')

        with self.acquire_rdbms_connection(True) as connection:
            cursor = connection.execute("""
                SELECT team_id,
                       account_id,
                       invitation_nonce
                  FROM team_membership_invitation
                  WHERE invitation_id = %(invitation_id)s
                    AND object_status = %(OBJECT_STATUS_ENABLED)s""",
                { 'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                  'invitation_id': invitation_id })
            row = cursor.fetch_one()
            if row is None:
                raise self.UndefinedObjectException('No invitation corresponds to the code "%s"' % invitation_code)

            invitation = row.get_object({
                'account_id': cast.string_to_uuid,
                'team_id': cast.string_to_uuid
            })

            if invitation_nonce != invitation.invitation_nonce:
                raise self.IllegalAccessException("The invitation code has been corrupted")

            # Check that the team is still enabled.
            self.get_team(invitation.team_id, check_status=True)

            # Delete the invitation that has been sent to the user.
            connection.execute("""
                UPDATE team_membership_invitation
                  SET object_status = %(OBJECT_STATUS_DELETED)s,
                      update_time = current_timestamp
                  WHERE invitation_id = %(invitation_id)s""",
                { 'OBJECT_STATUS_DELETED': ObjectStatus.deleted,
                  'invitation_id': invitation_id })


    def get_member(self, app_id, account_id, team_id, member_account_id):
        """
        Return the extended information of a member of a team.

        @note: only a member of the team is allowed to get information about a
            member of this team.

        :param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        :param account_id: Identification of the account of a user on behalf
            of whom this function is called.

        :param team_id: Identification of a team.

        :param member_account_id: Identification of the account of the user to
            return extended information related to the specified team.

        :return: an array of instance containing the following members:

            * `account_id`: Identification of the account of a member.

            * `creation_time`: date and time when this user became
              member of the team.

            * `full_name`: complete full name of the user as given by the
              user himself, i.e., untrusted information.

            * `is_administrator`: Indicate whether the user is an administrator
              of this team.

            * `locale`: a `Locale` instance that identifies the preferred
              language of the user, or English by default.

            * `picture_id`: Identification of the user account's picture, if
              any picture defined for this user account.

            * `picture_url`: Uniform Resource Locator (URL) that specifies
              the location of the user account's picture, if any defined.  The
              client application can use this URL and append the query
              parameter `size` to specify a given pixel resolution of the
              user account's picture, such as `thumbnail`, `small`,
              `medium`, `large`.

            * `timezone`: time zone of the default location of the user.  It
              is the difference between the time at this location and UTC
              (Universal Time Coordinated).  UTC is also  known as GMT or
              Greenwich Mean Time or Zulu Time.

            * `update_time`: time when the information of this user account
              has been updated for the last time.

            * `username`: name of the account of the user, if any defined.

        :raise DeletedObjectException: If the team has been deleted.

        :raise DisabledObjectException: If the team has been disabled.

        :raise IllegalAccessException: If the user on behalf of the function
            is called is not a member of the team.

        :raise UndefinedObjectException: If the specified identification
            doesn't refer to a team registered against the platform.
        """
        self.get_team(team_id, check_status=True)
        self.assert_member(account_id, team_id)

        with self.acquire_rdbms_connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    is_administrator,
                    creation_time
                  FROM
                    team_member
                  WHERE 
                    team_id = %(team_id)s
                    AND account_id = %(account_id)s
                    AND object_status = %(OBJECT_STATUS_ENABLED)s
                """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'account_id': member_account_id,
                    'team_id': team_id
                })

            row = cursor.fetch_one()
            if row is None:
                return None

            member = row.get_object({ 'creation_time': cast.string_to_timestamp })

            account = AccountService().get_account(account_id, check_status=True)
            account.creation_time = member.creation_time
            account.is_administrator = member.is_administrator

            return account














    def get_invitations(self, app_id, account_id, team_id,
            offset=0, limit=BaseRdbmsService.DEFAULT_LIMIT):
        """
        Return a list of invitations that have been sent to users to join the
        specified team.

        @note: only an administrator of a team is allowed to get invitations
            sent to users to join this team.

        :param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.
        :param account_id: Identification of the account of a user who must be
            an administrator of the specified team.
        :param team_id: Identification of a team.
        :param offset: require to skip that many invitations before beginning
            to return invitations.
        :param limit: constrain the number of invitations that are returned to
            the specified number.

        :return: an array of instance containing the following members:
            * `account_id`: Identification of the account of a member.
            * `creation_time`: date and time when this user became
              member of the team.
            * `full_name`: complete full name of the user as given by the
              user himself, i.e., untrusted information.
            * `locale`: a `Locale` instance that identifies the preferred
              language of the user, or English by default.
            * `picture_id`: Identification of the user account's picture, if
              any picture defined for this user account.
            * `picture_url`: Uniform Resource Locator (URL) that specifies
              the location of the user account's picture, if any defined.  The
              client application can use this URL and append the query
              parameter `size` to specify a given pixel resolution of the
              user account's picture, such as `thumbnail`, `small`,
              `medium`, `large`.
            * `timezone`: time zone of the default location of the user.  It
              is the difference between the time at this location and UTC
              (Universal Time Coordinated).  UTC is also  known as GMT or
              Greenwich Mean Time or Zulu Time.
            * `update_time`: time when the information of this user account
              has been updated for the last time.
            * `username`: name of the account of the user, if any defined.

        :raise DeletedObjectException: If the team has been deleted.
        :raise DisabledObjectException: If the team has been disabled.
        :raise IllegalAccessException: If the user on behalf of the function
            is called is not an administrator of the team.
        :raise UndefinedObjectException: If the specified identification
            doesn't refer to a team registered against the platform.
        """
        self.get_team(team_id, check_status=True)
        self.assert_administrator(account_id, team_id)

        with self.acquire_rdbms_connection(False) as connection:
            self.assert_administrator(team_id, account_id)

            cursor = connection.execute("""
                SELECT invitation_id,
                       account_id,
                       creation_time
                  FROM team_membership_invitation
                  WHERE team_id = %(team_id)s
                    AND object_status = %(OBJECT_STATUS_ENABLED)s
                  ORDER BY creation_time ASC
                  LIMIT %(limit)s
                  OFFSET %(offset)s""",
                { 'limit': limit if limit <= self.MAXIMUM_LIMIT else self.MAXIMUM_LIMIT,
                  'offset': offset,
                  'team_id': team_id })
            invitations = dict([ (invitation.account_id, invitation)
                    for invitation in [ row.get_object({
                                'account_id': cast.string_to_uuid,
                                'creation_time': cast.string_to_timestamp,
                                'invitation_id': cast.string_to_uuid })
                    for row in cursor.fetch_all() ] ])

            accounts = AccountService().get_accounts(app_id, invitations.keys())
            for account in accounts:
                account.__dict__.update(invitations[account.account_id].__dict__)

            return accounts

    def get_member_role(
            self,
            account_id,
            team_id,
            connection=None,
            enumeration=None):
        """
        Return the role of a user in a team


        :param account_id: Identification of the account of a user

        :param team_id: Identification of a team this user belongs to.

        :param connection: An object `RdbmsConnection`.

        :param enumeration: An enumeration to cast the returned value to.


        :return: Role of the specified member for the given team.


        :raise DeletedObjectException: If the team has been deleted.

        :raise DisabledObjectException: If the team has been disabled.

        :raise InvalidArgumentException: If the specified user is not a
            member of the given team.

        :raise UndefinedObjectException: If the specified identification
            doesn't refer to a team registered against the platform.
        """
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    role
                  FROM 
                    team_member
                  WHERE
                    team_id = %(team_id)s
                    AND account_id = %(account_id)s
                """,
                {
                    'account_id': account_id,
                    'team_id': team_id
                }
            )

            row = cursor.fetch_one()
            if row is None:
                raise self.InvalidArgumentException("The user doesn't belong to the specified team")

            role = row.get_value('role')
            if enumeration:
                role = cast.string_to_enum(role, enumeration)

            return role

    def get_team(
            self,
            team_id,
            check_status=False,
            connection=None,
            include_extended_info=False,
            include_contacts=False):
        """
        Return extended information about the team specified by its
        identification.


        @warning: this function is for internal usage only; it MUST not be
            surfaced to client applications.


        :param team_id: Identification of a team.

        :param check_status: Indicate whether the function must check the
            current status of this team and raise an exception if it is not of
            enabled.

        :param connection: a `RdbmsConnection` instance to be used
            supporting the Python clause `with ...:`.

        :param include_extended_info: request the function to provide extended
            information about this team, such as the Uniform Resource Locator
            (URL) that is provided as a link in the email the platform sends
            to a user who is invited to join the team, the template of the
            letter to send by email.

        :param include_contacts: Indicate whether to include the contacts
            information of this team.


        :return: an instance containing the following members:

            * `team_id`: Identification of the team.

            * `name`: the name of the team.

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

                * `is_primary`: Indicate whether this contact information is
                  the primary.

                * `is_verified`: Indicate whether this contact information
                  has been verified, whether it has been grabbed from a
                  trusted Social Networking Service (SNS), or whether through
                  a challenge/response process.

            * `description`: a short textual description of the team, if any
              provided.

            * `account_id`: Identification of the account of the agent
              administrator for this team.

            * `picture_id`: Identification of the picture that
               represents the team, if any picture defined for this team.

            * `picture_url`: Uniform Resource Locator (URL) that specifies
              the location of the picture representing the team, if any
              defined.  The client application can use this URL and append the
              query parameter `size` to specify a given pixel resolution of
              the team's picture:

              * `thumbnail`

              * `small`

              * `medium`

              * `large`

            * `invitation_url`: Uniform Resource Locator (URL) that is
              provided as a link in the email the platform sends to a user who
              is invited to join the team.  When the user clicks on the link
              embedded in the email, the email reader application issues a
              HTTP GET request to this URL.

            * `invitation_email`: template of the letter to send by email to
              a user who is invited to join the team.  If no specific template
              is defined for this team, the platform provides a default
              template located in `./template/invitation_default_email.txt`,
              relative to the path of the team service Python module.

            * `object_status`: current status of the team.

            * `creation_time`: time when the team has been registered.

            * `update_time`: most recent time when some information, such as
              the name or the description of the team, has been modified.


        :raise DeletedObjectException: If the team has been deleted, while the
            argument `check_status` has been set to `True`.

        :raise DisabledObjectException: If the team has been disabled, while
           the argument `check_status` has been set to `True`.

        :raise UndefinedObjectException: If the specified identification
            doesn't refer to a team registered to the platform.
        """
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    team_id,
                    name,
                    description,
                    account_id,
                    picture_id,
                    invitation_url,
                    invitation_email,
                    object_status,
                    creation_time,
                    update_time
                  FROM
                    team
                  WHERE
                    team_id = %(team_id)s
                """,
                {
                    'team_id': team_id
                })

            row = cursor.fetch_one()
            if row is None:
                raise self.UndefinedObjectException(f"Invalid team identification")

            team = row.get_object({
                'account_id': cast.string_to_uuid,
                'creation_time': cast.string_to_timestamp,
                'object_status': ObjectStatus,
                'picture_id': cast.string_to_uuid,
                'team_id': cast.string_to_uuid,
                'update_time': cast.string_to_timestamp
            })

            if check_status:
                if team.object_status == ObjectStatus.disabled:
                    raise self.DisabledObjectException(f"The team {team_id} has been disabled")
                elif team.object_status == ObjectStatus.deleted:
                    raise self.DeletedObjectException(f"The team {team_id} has been deleted")

            if include_extended_info:
                if team.invitation_email is None:
                    with open(TeamService.DEFAULT_INVITE_EMAIL_FILE_PATH_NAME) as file:
                        team.invitation_email = file.read()
            else:
                del team.invitation_url
                del team.invitation_email

            # Include the contact information of this team.
            if include_contacts:
                cursor = connection.execute(
                    """
                    SELECT 
                        property_name,
                        property_value,
                        is_primary,
                        is_verified
                      FROM
                        team_contact
                      WHERE
                        team_id = %(team_id)s
                        AND object_status = %(OBJECT_STATUS_ENABLED)s
                    """,
                    {
                        'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                        'team_id': team_id
                    }
                )

                team.contacts = [
                    row.get_object({
                        'team_id': cast.string_to_uuid,
                        'property_name': ContactName
                    })
                    for row in cursor.fetch_all()
                ]

            # Build the Uniform Resource Locator (URL) that specifies the location
            # of the picture representing the team.
            team.picture_url = team.picture_id and os.path.join(
                settings.CDN_URL_HOSTNAME,
                self.DEFAULT_CDN_BUCKET_NAME_LOGO,
                str(team.picture_id))

            return team

    def get_team_by_name(
            self,
            name,
            check_status=False,
            extended_info=False):
        """
        Return extended information about the team specified by its name.

        @warning: this function is for internal usage only; it MUST not be
            surfaced to client applications.


        :param name: name of a team.

        :param check_status: Indicate whether the function must check the
            current status of this team and raise an exception if it is not
            of enabled.

        :param extended_info: request the function to provide extended
            information about this team, such as the Uniform Resource Locator
            (URL) that is provided as a link in the email the platform sends
            to a user who is invited to join the team, the template of the
            letter to send by email.


        :return: an instance containing the following members:

            * `team_id`: Identification of the team.
            * `name`: the name of the team.
            * `description`: a short textual description of the team, if any
              provided.
            * `account_id`: Identification of the account of the agent for
              this team.
            * `picture_id`: Identification of the picture that represents
              the team, if any picture defined for this team.
            * `picture_url`: Uniform Resource Locator (URL) that specifies
              the location of the picture representing the team, if any
              defined.  The client application can use this URL and append the
              query parameter `size` to specify a given pixel resolution of
              the team's picture:
               * `thumbnail`
               * `small`
               * `medium`
               * `large`
            * `invitation_url`: Uniform Resource Locator (URL) that is
              provided as a link in the email the platform sends to a user who
              is invited to join the team.  When the user clicks on the link
              embedded in the email, the email reader application issues a
              HTTP GET request to this URL.
            * `invitation_email`: template of the letter to send by email to
              a user who is invited to join the team.  If no specific template
              is defined for this team, the platform provides a default
              template located in `./template/invitation_default_email.txt`,
              relative to the path of the team service Python module.
            * `object_status`: current status of the team, such as:
              * `OBJECT_STATUS_ENABLED`
              * `OBJECT_STATUS_DELETED`
              * `OBJECT_STATUS_DISABLED`
            * `creation_time`: time when the team has been registered.
            * `update_time`: most recent time when some information, such as
              the name or the description of the team, has been modified.

        :raise DeletedObjectException: If the team has been deleted, while the
             argument `check_status` has been set to `True`.
        :raise DisabledObjectException: If the team has been disabled, while
             the argument `check_status` has been set to `True`.
        :raise UndefinedObjectException: If the specified identification
            doesn't refer to a team registered against the
            platform.
        """
        with self.acquire_rdbms_connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    team_id
                  FROM
                    team
                  WHERE
                    lower(name) = lower(%(name)s)
                """,
                {
                    'name': name
                })

            row = cursor.fetch_one()
            if row is None:
                raise self.UndefinedObjectException(f'The team "{ name}" is not registered')

            team_id = row.get_value('team_id', cast.string_to_uuid)

            return self.get_team(
                team_id,
                check_status=check_status,
                include_extended_info=extended_info)

    def get_teams(
            self,
            team_ids,
            sync_time=None,
            include_contacts=False):
        """
        Return up to 100 teams worth of extended information, specified by
        their identification.

        If a requested user is unknown, suspended, or deleted, then that user
        will not be returned in the results list.


        :param team_ids: a list of  of the account of a user.

        :param sync_time: Indicate the earliest time to return a information
            of a team that might have been modified since.  If not specified,
            the function returns information about all the specified teams.

        :param include_contacts: Indicate whether to include the contacts
            information of these teams.


        :return: an array of instances containing the following members:

            * `team_id`: Identification of a team the specified user is member of.

            * `name`: the name of the team.

            * `description`: a short textual description of the team, if any
              provided.

            * `account_id`: Identification of the account of the agent of this
              team.

            * `picture_id`: Identification of the picture that represents the
              team, if any picture defined for this team.

            * `picture_url`: Uniform Resource Locator (URL) that specifies the
              location of the picture representing the team, if any defined.  The
              client application can use this URL and append the query parameter
              `size` to specify a given pixel resolution of the team's picture:

              * `thumbnail`

              * `small`

              * `medium`

              * `large`

            * `creation_time`: date and time when the team has been registered
               to the platform.

            * `update_time`: date and time of the most recent modification of one
              or more properties of this team.
        """
        team_ids = list(set(team_ids))[:TeamService.MAXIMUM_LIMIT]

        with self.acquire_rdbms_connection(False) as connection:
            cursor = connection.execute(
                """
                SELECT
                    team_id,
                    name,
                    description,
                    account_id,
                    picture_id,
                    creation_time,
                    update_time
                  FROM 
                    team
                  WHERE
                    team_id IN (%[team_ids]s)
                    AND object_status = %(OBJECT_STATUS_ENABLED)s
                    AND (%(sync_time)s IS NULL OR update_time >= %(sync_time)s)
                """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'sync_time': sync_time,
                    'team_ids': team_ids
                })

            teams = [
                row.get_object({
                    'account_id': cast.string_to_uuid,
                    'creation_time': cast.string_to_timestamp,
                    'picture_id': cast.string_to_uuid,
                    'team_id': cast.string_to_uuid,
                    'update_time': cast.string_to_timestamp
                })
                for row in cursor.fetch_all()
            ]

            # Build the Uniform Resource Locator (URL) that specifies the location
            # of pictures representing their respective team.
            for team in teams:
                team.picture_url = team.picture_id and os.path.join(
                    settings.CDN_URL_HOSTNAME,
                    self.DEFAULT_CDN_BUCKET_NAME_LOGO,
                    str(team.picture_id))

            # Include the contacts information of the teams.
            if include_contacts:
                teams_dict = dict([
                    (team.team_id, team)
                    for team in teams
                ])

                cursor = connection.execute(
                    """
                    SELECT 
                        team_id,
                        property_name,
                        property_value,
                        is_primary,
                        is_verified
                      FROM
                        team_contact
                      WHERE 
                        team_id IN (%[team_ids]s)
                        AND object_status = %(OBJECT_STATUS_ENABLED)s
                    """,
                    {
                        'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                        'team_ids': teams_dict.keys()
                    })

                row_objects = [
                    row.get_object({
                        'team_id': cast.string_to_uuid,
                        'property_name': ContactName
                    })
                    for row in cursor.fetch_all()
                ]

                teams_contacts = collections.defaultdict(list)
                for row_object in row_objects:
                    teams_contacts[row_object.team_id].append(row_object)
                    del row_object.team_id

                for (team_id, team_contacts) in teams_contacts.iteritems():
                    teams_dict[team_id].contacts = team_contacts

            return teams

    def invite_users(self, app_id, account_id, team_id, account_ids):
        """
        Invite a list of users to join the specified team.  The platform will
        eventually send them an invitation, either by an email or an in-app
        notification.  Their membership is pending until they accept or
        decline the invitation.

        The function filters out email addresses of users who are already
        members of the team and email addresses of users who have been already
        invited but who have not yet accepted.

        @note: only an administrator of the team is allowed to invitation users to
            join a team.

        @note: the function silently creates ghost accounts for users who have
            not an email address registered against the platform yet.  The
            locale that is used to reference the preferred language of such
            users is the same than for the administrator of the team.

        @note: when a user has been requested to join the team and he declined
            the invitation, it will take a day or so before an administrator
            can send him a new request.  When a user declines an invitation,
            the status of this invitation is marked as deleted but the invite
            still exists, meaning that such a user will be filtered out too.
            A background task is responsible for hard-deleting after a day or
            so invitations that have been declined.

        :param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        :param account_id: Identification of the account of the user who is
            inviting others to join the team.  This user MUST be an
            administrator of this team.

        :param team_id: Identification of the team to invitation the specified
            users to join.

        :param account_ids: a list of account identifications or/and valid
            email addresses of users who are invited to join the specified
            team.

        :return: the list of email addresses of new members who have been
            added to the team; users who were already members of the team
            are filtered out.

        :raise DeletedObjectException: If the team has been deleted.

        :raise DisabledObjectException: If the team has been disabled.

        :raise IllegalAccessException: If the user on behalf of the new member
            is added to the team is not an administrator of this team.

        :raise InvalidArgumentException: If some email addresses are of a
            wrong format, i.e., not compliant with RFC 2822, or if some
            account identifications are invalid.

        :raise InvalidOperationException: If no URL callback for accepting
            or declining invitation invitation has been defined for this team.

        :raise UndefinedObjectException: If the specified identification
            doesn't refer to a team registered against the platform.
        """
        # Check that the user references passed to the function correspond
        # either email addresses or account identifications.
        invalid_account_ids = [ _account_id for _account_id in account_ids
                if not AccountService.REGEX_PATTERN_EMAIL_ADDRESS.match(_account_id) and
                   not string_util.is_uuid(_account_id) ]
        if len(invalid_account_ids) > 0:
            raise self.InvalidArgumentException('Invalid email addresses or account identifications',
                    payload=invalid_account_ids)

        # Check the status of the team, the status and the role of the account
        # on behalf of whom the specified user is invited to join the team.
        team = self.get_team(team_id, check_status=True, include_extended_info=True)
        if team.invitation_url is None:
            raise self.InvalidOperationException('No URL callback for accepting or declining invitation has been defined for this team')

        account = AccountService().get_account(account_id, check_status=True)
        self.assert_administrator(account_id, team_id)

        with self.acquire_rdbms_connection(True) as connection:
            email_addresses = [ email_address for email_address in account_ids
                     if AccountService.REGEX_PATTERN_EMAIL_ADDRESS.match(email_address)]
            if len(email_addresses) > 0:
                # Retrieve accounts corresponding to the specified email addresses.
                # @note: Do not filter out account that are deleted, otherwise the
                # function will try to create ghost account with their email address.
                accounts = AccountService().get_accounts_by_contact_information(
                        [ (AccountService.VCardPropertyName.EMAIL, email_address)
                            for email_address in email_addresses ],
                        verified_only=False, ignore_deleted=True)

                # Create ghost accounts for users whose email addresses are not yet
                # registered against the platform.
                if len(accounts) < len(email_addresses):
                    def __register_ghost_account(app_id, email_address, locale=None):
                        account = AccountService().sign_up(app_id, email_address,
                            full_name=email_address.split('@')[0],
                            account_type=AccountService.AccountType.ghost,
                            locale=locale,
                            bypass_recaptcha=True)
                        account.email_address = email_address
                        return account

                    accounts.extend([ __register_ghost_account(app_id, email_address, account.locale)
                        for email_address in set(email_addresses) - set([ account.email_address for account in accounts ]) ])

            # Add the accounts specified by their identification.
            accounts += AccountService().get_accounts(app_id,
                    [ _account_id for _account_id in account_ids
                        if string_util.is_uuid(_account_id) ])

            # Remove from the list of users those who are already members of the
            # team and those who have been sent am invitation to which they didn't
            # answer yet.  Issue an invitation for the others and generate a
            # nonce, a pseudo-random number, to ensure that the invitation cannot
            # be reused in replay attacks.
            cursor = connection.execute("""
                SELECT account_id,
                       nextval('seq_team_membership_invitation_id') AS invitation_id
                  FROM account
                  WHERE account_id IN (%[account_ids]s)
                    AND object_status = %(OBJECT_STATUS_ENABLED)s
                    AND NOT EXISTS (
                      SELECT true
                        FROM team_member
                        WHERE team_member.team_id = %(team_id)s
                          AND team_member.account_id = account.account_id)
                    AND NOT EXISTS (
                      SELECT true
                        FROM team_membership_invitation
                        WHERE team_membership_invitation.team_id = %(team_id)s
                          AND team_membership_invitation.account_id = account.account_id)""",
                { 'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                  'account_ids': [ account.account_id for account in accounts ],
                  'team_id': team_id })
            invitations = [ row.get_object({ 'account_id': cast.string_to_uuid }) for row in cursor.fetch_all() ]
            if len(invitations) == 0:
                return []

            for invitation in invitations:
                (_, nonce, _) = key_util.generate_secured_key(invitation.invitation_id)
                invitation.invitation_nonce = nonce

            # Remove any previous invitations that would have been sent to these
            # users, and that would have been soft-deleted.
            connection.execute("""
                DELETE FROM team_membership_invitation
                  WHERE team_id = %(team_id)s
                    AND account_id IN (%[account_ids]s)
                    AND object_status = %(OBJECT_STATUS_DELETED)s""",
                { 'OBJECT_STATUS_DELETED': ObjectStatus.deleted,
                  'account_ids': [ invitation.account_id for invitation in invitations ],
                  'team_id': team_id })

            cursor = connection.execute("""
                INSERT INTO team_membership_invitation(
                                invitation_id,
                                invitation_nonce,
                                team_id,
                                account_id,
                                originator_id)
                  SELECT invitation_id,
                         invitation_nonce,
                         %(team_id)s,
                         account_id::uuid,
                         %(originator_id)s
                    FROM (VALUES %[values]s) AS invite(account_id, invitation_id, invitation_nonce)""",
                { 'originator_id': account_id,
                  'team_id': team_id,
                  'values': [ (invitation.account_id, invitation.invitation_id, invitation.invitation_nonce)
                          for invitation in invitations ] })

        # Return the email addresses of users who need to receive an
        # invitation to join the team.
        account_dict = dict([ (account.account_id, account) for account in accounts ])
        return [ account_dict[invitation.account_id].email_address
                for invitation in invitations ]


    def is_administrator(self, account_id, team_id):
        """
        Indicate whether the specified user is an administrator of a given
        team.


        :param team_id: Identification of a team.

        :param account_id: Identification of the account of the user to check
            his administrator role for the specified team.


        :return: `True` if the specified user is an administrator of the
            given team; `False` otherwise.


        :raise DeletedObjectException: If the team has been deleted.

        :raise DisabledObjectException: If the team has been disabled.

        :raise UndefinedObjectException: If the specified identification
            doesn't refer to a team registered against the platform.
        """
        self.get_team(team_id, check_status=True)

        with self.acquire_rdbms_connection(False) as connection:
            cursor = connection.execute("""
                SELECT true
                  FROM team_member
                  WHERE team_id = %(team_id)s
                    AND account_id = %(account_id)s
                    AND is_administrator = true""",
                { 'account_id': account_id,
                  'team_id': team_id })
            return cursor.get_row_count() > 0


    def is_member(self, account_id, team_id):
        """
        Indicate whether the specified user belongs to a given team.


        :param account_id: Identification of the account of the user to check
            his membership to the specified team.

        :param team_id: Identification of a team or a collection of
            identifications of team.


        :return: `True` if the specified user belongs to the given team;
            `False` otherwise.


        :raise DeletedObjectException: If the team has been deleted.

        :raise DisabledObjectException: If the team has been disabled.

        :raise UndefinedObjectException: If the specified identification
            doesn't refer to a team registered against the platform.
        """
        if isinstance(team_id, (list, set, tuple)):

            team_ids = team_id
        else:
            self.get_team(team_id, check_status=True)
            team_ids = [ team_id ]

        with self.acquire_rdbms_connection(False) as connection:
            cursor = connection.execute("""
                SELECT true
                  FROM team_member
                  WHERE team_id IN (%[team_ids]s)
                    AND account_id = %(account_id)s""",
                { 'account_id': account_id,
                  'team_ids': team_ids })
            return cursor.get_row_count() > 0

    def is_name_available(self, name, connection=None):
        """
        Indicate whether the specified name is available


        :param name: The name of a team.

        :param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...`.


        :return: `True` if the given name is not already used by a team;
            `False` if a team has been already given this name.
        """
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT
                    true
                  FROM
                    team
                  WHERE
                    lower(name) = lower(%(name)s)
                """,
                {
                    'name': name
                })

            is_available = cursor.get_row_count() == 0
            return is_available

    def promote_agent(self, app_id, account_id, team_id, promoted_account_id):
        """
        Promote an administrator as the new agent of the team.

        @note: only the current agent of this team can promote another
            administrator of the team to become the agent of this team.

        :param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.
        :param account_id: Identification of the account of the user who
            promotes the second user as the new agent.  This first user MUST
            be the current agent of the team.
        :param team_id: Identification of the team to promote the specified
            account as the new agent for this team.
        :param promoted_account_id: Identification of the account of the user
            who is promoted as the new master administrator.  This user MUST
            have the role of administrator.

        :raise IllegalAccessException: If the account of the user on behalf of
            the function is called is not the agent of the team.
        :raise InvalidOperationException: If the promoted user account is
            already the agent of the team, or if the specified user account
            that is promoted ad the new agent of the team is not an
            administrator of the team.
        :raise UndefinedObjectException: If the specified team is not
            registered.
        """
        # Check the prerequisites.
        team = self.get_team(team_id, check_status=True)
        account = AccountService().get_account(account_id, check_status=True)
        if account_id != team.account_id:
            raise self.IllegalAccessException('The specified account is not the agent of the team')

        if account_id == promoted_account_id:
            raise self.InvalidOperationException('The promoted account is already the agent of the team')

        try:
            self.assert_administrator(promoted_account_id, team_id)
        except self.IllegalAccessException:
            raise self.InvalidOperationException('The promoted account has to be an administrator of the team')

        # Promote the specified account as the new agent of the team.
        with self.acquire_rdbms_connection(True) as connection:
            connection.execute("""
                UPDATE team
                  SET account_id = %(promoted_account_id)s,
                      update_time = current_timestamp
                  WHERE team_id = %(team_id)s""",
                { 'promoted_account_id': promoted_account_id,
                  'team_id': team.team_id })

    def remove_member(
            self,
            account_id,
            team_id,
            connection=None,
            hard_delete=False):
        """
        Remove the specified member from the given team


        :param account_id: Identification of the account of a member.

        :param team_id: Identification of the team.

        :param account_id: Identification of a user account.

        :param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...`.

        :param hard_delete: Indicate whether to do a hard-delete of this
            account, i.e, completely removing its record. By default, the
            function performs a soft-delete, marking this account has
            deleted.


        :raise DeletedObjectException: If the team has been deleted.

        :raise DisabledObjectException: If the team has been disabled.

        :raise InvalidOperationException: If the specified user account is not
            a member of the team or if the specified user account is the agent
            of the team -- his role cannot be removed expect by using the
            method `promote_agent`.

        :raise UndefinedObjectException: If the team doesn't exist.
        """
        team = self.get_team(team_id, check_status=True)

        if not self.is_member(account_id, team_id):
            raise self.InvalidArgumentException("This user is not a member of this team")

        if account_id == team.account_id:
            raise self.InvalidOperationException("Cannot delete the agent of a team")

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            if hard_delete:
                connection.execute(
                    """
                    DELETE FROM
                        team_member
                      WHERE
                        account_id = %(account_id)s
                        AND team_id = %(team_id)s
                    """,
                    {
                        'account_id': account_id,
                        'team_id': team_id,
                    })
            else:
                connection.execute("""
                    UPDATE 
                        team_member
                      SET
                        object_status = %(OBJECT_STATUS_DELETED)s,
                        update_time = current_timestamp
                      WHERE
                        account_id = %(account_id)s
                        AND team_id = %(team_id)s
                    """,
                    {
                        'OBJECT_STATUS_DELETED': ObjectStatus.deleted,
                        'account_id': account_id,
                        'team_id': team_id,
                    })

    def search_teams(
            self,
            app_id,
            account_id,
            keywords,
            limit=BaseRdbmsService.DEFAULT_LIMIT,
            offset=0):
        """
        Return a list of teams which names match, even partially, the
        specified keywords.

        :param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        :param account_id: Identification of the account of a user.

        :param keywords: a list of keywords.

        :param limit: constrain the number of teams that are returned to the
            specified number.

        :param offset: require to skip that many teams before beginning to
            return teams.

        :return: an instance containing the following members:

            * `team_id`: Identification of the team.

            * `name`: the name of the team.

            * `description`: a short textual description of the team, if any
              provided.

            * `account_id`: Identification of the account of the agent for
              this team.

            * `picture_id`: Identification of the picture that represents
              the team, if any picture defined for this team.

            * `picture_url`: Uniform Resource Locator (URL) that specifies
              the location of the picture representing the team, if any
              defined.  The client application can use this URL and append the
              query parameter `size` to specify a given pixel resolution of
              the team's picture:

               * `thumbnail`

               * `small`

               * `medium`

               * `large`

            * `creation_time`: time when the team has been registered.

            * `update_time`: most recent time when some information, such as
              the name or the description of the team, has been modified.
        """
        with self.acquire_rdbms_connection(False) as connection:
            cursor = connection.execute("""
                SELECT team_id,
                       name,
                       description,
                       account_id,
                       picture_id,
                       object_status,
                       creation_time,
                       update_time
                  FROM team
                  WHERE lower(name) SIMILAR TO %(keywords)s
                    AND object_status = %(OBJECT_STATUS_ENABLED)s
                  ORDER BY creation_time ASC
                  LIMIT %(limit)s
                  OFFSET %(offset)s""",
                { 'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                  'keywords': '%%(%s)%%' % '|'.join(
                        [ keyword.lower() for keyword in keywords ]),
                  'limit': limit,
                  'offset': offset })

            teams = [ row.get_object({
                        'creation_time': cast.string_to_timestamp,
                        'picture_id': cast.string_to_uuid,
                        'team_id': cast.string_to_uuid,
                        'update_time': cast.string_to_timestamp })
                    for row in cursor.fetch_all() ]

            for team in teams:
                team.picture_url = team.picture_id and os.path.join(settings.CDN_URL_HOSTNAME,
                                                                    self.DEFAULT_CDN_BUCKET_NAME_LOGO, str(team.picture_id))

            return teams


    # def send_invitations(self, app_id, account_id):
    #     """
    #     Send emails or in-app notifications to users who have been invited to
    #     join a team.
    #
    #     @warning: this function MUST no be surfaced to any public API, but it
    #               is intended to be used by background task running on the
    #               platform.
    #
    #     :param app_id: Identification of the client application such as a Web,
    #            a desktop, or a mobile application, that accesses the service.
    #     :param account_id: Identification of the account of an administrator of
    #            the platform or a botnet on behalf of whom this function is run.
    #
    #     :return a list of instances containing the following members:
    #             * `invitation_id`: Identification number of the membership invite
    #                that has been sent to this user on behalf of the
    #                administrator who added him as a member of the team.
    #             * `invitation_nonce`: "number used once", a pseudo-random number
    #                issued when generating the invitation key to ensure that this
    #                key cannot be reused in replay attacks.
    #             * `team_id`: Identification of the team this user is invited
    #               to join.
    #             * `team_name`: name of the team this user is invited to
    #               join.
    #             * `account_id`: Identification of the account of the user
    #               who is invited to join the team.
    #             * `recipient_name`: name of the user who is invited to join
    #               the team.
    #             * `email_address`: email address of the user who is invited
    #               to join the team.
    #             * `sender_name`: name of the administrator of the team who
    #               invited the user to join this team.
    #             * `invitation_url`: Uniform Resource Locator (URL) that is
    #               provided as a link in the email the platform sends to a
    #               user who is invited to join the team.  When the user clicks
    #               on the link embedded in the email, the email reader
    #               application issues a HTTP GET request to this URL.
    #             * `invitation_email`: template of the letter to send by email to
    #               the user who is invited to join the team.  If no specific
    #               template is defined for this team, the platform provides a
    #               default template.
    #             * `attempt_count`: number of times the platform notified the
    #                user from the membership invitation.  After a certain number
    #                of time, the membership invitation may may be canceled
    #
    #     :raise IllegalAccessException: If the specified user account is nor an
    #            administrator of the platform, not a botnet.
    #     """
    #     if AccountService().get_account(account_id).account_type \
    #             not in [AccountService.AccountType.administrator, AccountService.AccountType.botnet]:
    #         raise self.IllegalAccessException('The specified user MUST be an administrator or a botnet of the platform')
    #
    #     invitations = self._get_invitations();
    #
    #     for invitation in invitations:
    #         # Substitute variables defined in the message with their values, and
    #         # any placeholders that would be defined in these values, such as the
    #         # request secured key placeholder defined in the variable
    #         # `invitation_url`.
    #         message_content = (invitation.invitation_email % invitation.__dict__ ) % invitation.__dict__
    #         email_util.send_email(
    #                 settings.SMTP_SERVER_HOSTNAME, settings.SMTP_SERVER_PORT_NUMBER,
    #                 settings.SMTP_ACCOUNT_USERNAME, settings.SMTP_ACCOUNT_PASSWORD,
    #                 invitation.email_address,
    #                 settings.PLATFORM_BOTNET_EMAIL_ADDRESS,
    #                 'You have been invited to join the organization %s' % invitation.team_name,
    #                 message_content)
    #
    #         with self.acquire_rdbms_connection(True) as connection:
    #             connection.execute("""
    #                 UPDATE team_membership_invitation
    #                   SET attempt_count = attempt_count,
    #                       update_time = current_timestamp
    #                   WHERE invitation_id = %(invitation_id)s""",
    #                 { 'invitation_id': invitation.invitation_id })
    #
    #     return invitations

    def request_membership(
            self,
            account_id,
            team_id,
            connection=None):
        """
        Submit a request on behalf of a user to join a team

        This membership request has to be approved by an administrator of the
        team.


        :param account_id: Identification of the account of a user who
            requests to join a team.

        :param team_id: Identification of the team that the user requests to
            join.

        :param connection: An object `RdbmsConnection` supporting the Python clause `with ...`.


        :raise DeletedObjectException: If the team has been deleted.

        :raise DisabledObjectException: If the team has been disabled.

        :raise UndefinedObjectException: If the team doesn't exist.
        """
        if self.is_member(account_id, team_id):  # This method checks whether the team exists.
            self.log_warning(f"The user {account_id} is already member of the team {team_id}")
            return

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            connection.execute(
                """
                INSERT INTO 
                  team_membership_request (
                    team_id,
                    account_id,
                    app_id
                  )
                  VALUES (
                    %(team_id)s,
                    %(account_id)s
                  )
                  ON CONFLICT DO NOTHING
                """,
                {
                    'account_id': account_id,
                    'team_id': team_id
                })

    def upload_logo(
            self,
            team_id,
            account_id,
            logo_file,
            connection=None,
            image_file_format=DEFAULT_LOGO_IMAGE_FILE_FORMAT,
            image_quality=DEFAULT_LOGO_IMAGE_QUALITY,
            image_minimal_size=DEFAULT_LOGO_IMAGE_MINIMAL_SIZE):
        """
        Upload the new logo image of a team


        :param team_id: Identification of a team.

        :param account_id: Identification of the account of an administrator
            of the team who is uploading an image as the logo of his team.

        :param logo_file: An object `HttpRequest.HttpRequestUploadedFile`.

        :param connection: An object `RdbmsConnection` supporting the Python
            clause `with ...:`.

        :param image image_file_format: Image file format to store the image
            of the team's logo {@link https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html}.

        :param image_quality: Quality to store the image of the team's logo
            with, on a scale from `1` (worst) to `95` (best).  Values above
            `95` should be avoided; `100` disables portions of the JPEG
            compression algorithm, and results in large files with hardly any
            gain in image quality.

        :param image_minimal_size: A tuple `width, height` representing the
            minimal size of the image of a team's logo.


        :return: An object containing the following members:

            * `file_name` (required): Original local file name as the `filename`
              parameter of the `Content-Disposition` header.

            * `picture_id` (required): Identification of the new image of the team's
              logo.

            * `picture_url` (required): Uniform Resource Locator (URL) that
              specifies the location of the new image of the team's logo.

            * `update_time` (required): Time of the most recent modification of
              the properties of the team.


        :raise DeletedObjectException: If the team has been deleted.

        :raise DisabledObjectException: If the team has been disabled.

        :raise IllegalAccessException: If the user on behalf of whom the
            function is called is not an administrator of the team.

        :raise InvalidArgumentException: If the format of the image is not
            supported, or if the size of the image is too small.

        :raise UndefinedObjectException: If the team doesn't exist.
        """
        # Only an administrator is allowed to change the logo of the team.
        self.assert_member_role(account_id, team_id, MemberRole.administrator)

        # Retrieve the pixel resolution of the photo image, and check whether
        # it respects the minimal size required.
        image = self.__load_image_from_bytes(logo_file.data)
        self.__validate_image_size(image, image_minimal_size)
        image_width, image_height = image.size

        # Determine the signature and the size of the data of the uploaded photo
        # image.
        image_file_checksum = hashlib.md5(logo_file.data).hexdigest()
        image_file_size = len(logo_file.data)

        # Generate the identification of the photo.
        picture_id = uuid.uuid1()

        # Set this image as the new logo of this team.  The function checks
        # whether this same image has not been already set for this team (same
        # image data checksum and same image binary size).
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            cursor = connection.execute(
                """
                UPDATE
                    team
                  SET
                    image_height = %(image_height)s,
                    image_file_checksum = %(image_file_checksum)s,
                    image_file_size = %(image_file_size)s,
                    image_width = %(image_width)s,
                    picture_id = %(picture_id)s,
                    update_time = current_timestamp
                  WHERE
                    team_id = %(team_id)s
                    AND (image_file_checksum IS NULL OR image_file_checksum <> %(image_file_checksum)s)
                    AND (image_file_size IS NULL OR image_file_size <> %(image_file_size)s)
                  RETURNING
                    picture_id,
                    team_id,
                    update_time
                """,
                {
                    'image_height': image_height,
                    'image_file_checksum': image_file_checksum,
                    'image_file_size': image_file_size,
                    'image_width': image_width,
                    'picture_id': picture_id,
                    'team_id': team_id,
                })

            row = cursor.fetch_one()
            if row is None:
                raise self.InvalidOperationException("This logo has been already set for this team")

            # Retrieve the properties of the team's logo.
            logo = row.get_object({
                'picture_id': cast.string_to_uuid,
                'team_id': cast.string_to_uuid,
                'update_time': cast.string_to_timestamp,
            })

            # Add the URL link to access this picture and the original file name
            # that was uploaded.
            logo.picture_url = self.build_picture_url(logo.picture_id)
            logo.file_name = logo_file.file_name

            # Store the photo image file in the temporary directory of the local
            # Network File System (NFS).  This file will be read by background task
            # for additional processing.
            self.__store_logo_image_file(
                picture_id,
                image,
                image_file_format=image_file_format,
                image_quality=image_quality)

        return logo








    def update_member(self, app_id, account_id, team_id, member_account_id, is_administrator):
        """
        Update the role of a member of a given team.

        @note: the user account on behalf of whom the function is called MUST
            be an administrator of the team.

        :param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.
        :param account_id: Identification of the account of the user who is
            updating the role of the member.  This first user MUST have a
            role of administrator.
        :param team_id: Identification of the team for which the role of the
            specified member is updated.
        :param member_account_id: Identification of the account of the user
            whose role is updated.
        :param is_administrator_id: Indicate whether the member is an
            administrator of the team.

        :raise DeletedObjectException: If the team has been deleted.
        :raise DisabledObjectException: If the team has been disabled.
        :raise IllegalAccessException: If the user on behalf of the role of
            the specified member is updated is not an administrator of the
            team.
        :raise InvalidOperationException: If the specified user account is not
            a member of the team, if his current role is already this passed
            to the function, or if the specified user account is the agent of
            the team (his role cannot be changed except by using the method
           `promote_agent`).
        :raise UndefinedObjectException: If the specified identification
            doesn't refer to a team registered against the platform.
        """
        team = self.get_team(team_id, check_status=True)
        self.assert_member_role(account_id, team_id, roles=MemberRole.administrator)

        if team.account_id == member_account_id:
            raise self.InvalidOperationException('The role of the agent of this team cannot be changed except by promoting another administrator')

        with self.acquire_rdbms_connection(True) as connection:
            cursor = connection.execute("""
                UPDATE team_member
                  SET is_administrator = %(is_administrator)s,
                      update_time = current_timestamp
                   WHERE team_id = %(team_id)s
                     AND account_id = %(account_id)s
                   RETURNING true""",
                { 'account_id': member_account_id,
                  'is_administrator': is_administrator,
                  'team_id': team_id })
            if cursor.get_row_count() == 0:
                raise self.InvalidOperationException('The specified user account is not a member of the team')

    def withdraw_membership(
            self,
            app_id,
            account_id,
            team_id):
        """
        Withdraw the membership of a user from a team on behalf of this user.


        :param app_id: Identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        :param account_id: Identification of the account of the user who is
            withdrawing his membership from a team.

        :param team_id: Identification of a team the user is withdrawing his
            membership from.


        :raise DeletedObjectException: If the team has been deleted.

        :raise DisabledObjectException: If the team has been disabled.

        :raise InvalidOperationException: If the specified user is the agent
            of the team, of if he is not a member of the team.

        :raise UndefinedObjectException: If the specified identification
            doesn't refer to a team registered against the platform.
        """
        team = self.get_team(team_id, check_status=True)

        with self.acquire_rdbms_connection(True) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    true
                  FROM 
                    team
                  WHERE 
                    team_id = %(team_id)s
                    AND account_id = %(account_id)s
                """,
                {
                    'account_id': account_id,
                    'team_id': team_id
                }
            )
            if cursor.get_row_count() > 0:
                raise self.InvalidOperationException(
                    "The specified user is the agent of this team; he cannot withdraw his membership")

            cursor = connection.execute(
                """
                DELETE FROM 
                    team_member
                  SET 
                    object_status = %(OBJECT_STATUS_DELETED)s,
                    update_time = current_timestamp
                  WHERE
                    team_id = %(team_id)s
                    AND account_id = %(account_id)s
                  RETURNING true
                """,
                {
                    'account_id': account_id,
                    'team_id': team_id
                }
            )
            if cursor.get_row_count() == 0:
                raise self.InvalidOperationException(
                    "The specified user account is not a member of the team")
