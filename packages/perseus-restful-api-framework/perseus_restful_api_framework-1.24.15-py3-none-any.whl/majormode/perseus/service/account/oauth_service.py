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

from majormode.perseus.service.account.account_service import AccountService
from majormode.perseus.service.base_rdbms_service import BaseRdbmsService
from majormode.perseus.utils import cast


class OAuthService(BaseRdbmsService):
    def get_account_with_oauth(self, sns_name, sns_user_id, # sns_app_id
            check_status=False,
            connection=None,
            include_contacts=False):
        """
        Return the account of a user that matches the specified user
        registered on a 3rd party Social Networking Service.


        @param sns_name: code name of the 3rd party Social Networking Service
            such as ``facebook``, ``google``, etc.

        @param sns_user_id: dentification of the user on the 3rd party Social
            Networking Service.

        @param check_status: indicate whether the function MUST check the
            current status of this user account and raise an exception if is
            not of enabled.

        @param connection: a ``RdbmsConnection`` instance to be used
            supporting the Python clause ``with ...:``.

        @param include_contacts: indicate whether to include the contacts
            information of this user account.


        @return: an instance returned by ``AccountService.get_account``.


        @raise DeletedObjectException: if the user account has been deleted,
            while the argument ``check_status`` has been set to ``True``.

        @raise DisabledObjectException: if the user account has been disabled,
            while the argument ``check_status`` has been set to ``True``.

        @raise InvalidOperationException: if this user on the given Social
            Networking Service has linked several accounts on the platform.
            This SHOULD not be possible unless the code of the platform has a
            bug.

        @raise UndefinedObjectException: if the specified email address
            doesn't refer to a user account registered against the platform.
        """
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute("""
                SELECT DISTINCT account_id
                  FROM account_oauth
                  WHERE sns_name = %(sns_name)s
                    AND sns_user_id = %(sns_user_id)s
                    AND object_status = %(OBJECT_STATUS_ENABLED)s
                  FROM account_oauth
                  WHERE sns_name = %(sns_name)s
                    AND sns_user_id = %(sns_user_id)s""",
                { 'object_status': ObjectStatus.enabled,
                  'sns_name_': sns_name.strip().lower(),
                  'sns_user_id': sns_user_id })

            row_count = cursor.get_row_count()

            if row_count == 0:
                raise self.UndefinedObjectException('No account registered with the specified Social Networking Service',
                        payload={ 'sns_name': sns_name, 'sns_user_id': sns_user_id })

            if row_count > 1:
                raise self.InvalidOperationException('This SNS user has been linked to multiple accounts',
                        payload={ 'sns_name': sns_name, 'sns_user_id': sns_user_id })

            account_id = row.fetch_one().gat_value('account_id', cast.string_to_uuid)

            return AccountService().get_account(account_id,
                    check_status=check_status,
                    include_contacts=include_contacts,
                    connection=connection)





    def sign_up_with_oauth(self, sns_name, access_token, consumer_key,  consumer_secret,
            auto_sign_in=True,
            locale=None):

        user_info = self.__facebook_get_user_info(access_token)

        if not hasattr(user_info, 'contact'):
            raise self.InvalidOperationException(
                'The platform MUST be given access to the contact information of the user')

        account_session = AccountService().sign_up(
                account_type=AccountType.sns,
                contact=user_info.contact,
                fullname=user_info.name,
                locale=locale,
                auto_sign_in=auto_sign_in,
                has_been_verified=True)




        return account_session



        # # Check whether this user has already linked his Social Networking
        # # Service account with an account registered to the platform.
        # try:
        #     account = OAuthService().get_account_with_oauth(sns_name,
        #                                                     user_info.user_id,
        #                                                     check_status=False,
        #                                                     include_contacts=False)
        #
        # #
        # except OAuthService.UndefinedObjectException:
        #     try:
        #         account = AccountService().get_account_with_contact(
        #             user_info.contact,
        #             check_status=False,
        #             include_pending=True,
        #             is_verified=False)
        #
        #     except AccountService.UndefinedObjectException:





