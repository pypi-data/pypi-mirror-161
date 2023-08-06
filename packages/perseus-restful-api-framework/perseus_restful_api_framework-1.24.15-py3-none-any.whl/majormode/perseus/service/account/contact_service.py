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
import json
import random
import uuid

from majormode.perseus.constant.account import AccountType
from majormode.perseus.constant.obj import ObjectStatus
from majormode.perseus.constant.contact import ContactName
from majormode.perseus.model import obj
from majormode.perseus.model.contact import Contact
from majormode.perseus.model.locale import DEFAULT_LOCALE
from majormode.perseus.model.locale import Locale
from majormode.perseus.model.obj import Object
from majormode.perseus.utils.date_util import ISO8601DateTime

from majormode.perseus.service.base_rdbms_service import BaseRdbmsService
from majormode.perseus.service.base_service import BaseService
from majormode.perseus.utils import cast, rdbms


class ContactService(BaseRdbmsService):
    class ContactAlreadyInUseException(BaseService.BaseServiceException):
        """
        Signal that the specified contact information is already associated
        with an another user account of the platform.
        """
        pass

    class UnverifiedContactException(BaseService.BaseServiceException):
        """
        Signal that the contact information provided by the user has not been
        verified yet and it CANNOT be used for the ongoing procedure.
        """
        pass

    # Define the minimal allowed duration of time expressed in seconds
    # between two consecutive requests to verify a same contact information.
    MINIMAL_TIME_BETWEEN_CONTACT_VERIFICATION_REQUEST = 60 * 5

    # Maximum number of digits that composed a verification code used to
    # validate a contact information.
    VERIFICATION_CODE_MAXIMUM_DIGIT_COUNT = 9

    def __cleanse_contact_references(
            self,
            account_id,
            contact,
            connection=None):
        """
        Remove the specified contact information from any other user account
        but the one passed to this function.

        The function also cancels any verification requests  of this contact
        information that would be still ongoing.


        :param account_id: identification of the account of the user who has
            confirmed the given contact information.

        :param contact: an instance `Contact` of the contact information that
            the user has confirmed, and which references to it need to be
            removed from any other user account and ongoing verification
            request.

        :param connection: An object `RdbmsConnection`  with auto commit.
        """
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            # Remove this contact information from any other user account.
            cursor = connection.execute("""
                DELETE FROM 
                    account_contact
                  WHERE
                    property_name = %(property_name)s
                    AND property_value = %(property_value)s
                    AND account_id <> %(account_id)s
                  RETURNING
                    account_id""",
                {
                    'account_id': account_id,
                    'property_name': contact.property_name,
                    'property_value': contact.property_value
                })

            account_ids = [
                row.get_value('account_id', cast.string_to_uuid)
                for row in cursor.fetch_all()
            ]

            # Soft-delete accounts that this contact information has been removed
            # from and that have no contact information anymore.
            if account_ids:
                connection.execute(
                    """
                    UPDATE
                        account
                      SET 
                        object_status = %(OBJECT_STATUS_DISABLED)s
                      WHERE
                        account_id IN (%(account_ids)s)
                        AND NOT EXISTS(
                          SELECT
                              true
                            FROM
                              account_contact
                            WHERE
                             account_contact.account_id = account.account_id)
                    """,
                    {
                        'OBJECT_STATUS_DISABLED': ObjectStatus.disabled,
                        'account_ids': account_ids,
                    })

            # Delete any other verification requests of this contact information.
            connection.execute(
                """
                DELETE FROM 
                    account_contact_verification
                  WHERE
                    property_name = %(property_name)s
                    AND property_value = %(property_value)s""",
                {
                    'property_name': contact.property_name,
                    'property_value': contact.property_value,
                })

    def __enable_account_contact(
            self,
            account_id: uuid.UUID,
            contact: Contact,
            connection: rdbms.RdbmsConnection = None):
        """
        Enable the contact information of the specified user


        :param account_id: The identification of the account of a user.

        :param contact: The contact information to be enabled.

        :param connection: An object `RdbmsConnection` with auto commit.

        """
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            cursor = connection.execute(
                """
                UPDATE 
                    account_contact
                  SET 
                    is_verified = true,
                    update_time = current_timestamp
                  WHERE
                    account_id = %(account_id)s
                    AND property_name = %(property_name)s
                    AND property_value = %(property_value)s
                  RETURNING
                    is_primary
                  """,
                {
                    'account_id': account_id,
                    'property_name': contact.property_name,
                    'property_value': contact.property_value
                })

            is_primary = cursor.fetch_one().get_value('is_primary')

            # Set this contact information as primary if the user doesn't have any
            # primary contact information.
            if not is_primary:
                cursor = connection.execute(
                    """
                    SELECT EXISTS(
                      SELECT
                          true
                        FROM
                          account_contact
                        WHERE
                          account_id = %(account_id)s
                          AND property_name = %(property_name)s
                          AND is_primary)
                    """,
                    {
                        'account_id': account_id,
                        'property_name': contact.property_name
                    })

                if cursor.get_row_count() == 0:
                    self.set_primary_contact(account_id, contact, connection=connection)

    @staticmethod
    def __generate_nonce(digit_count):
        """
        Generate a string composed of the requested number of digits


        :param digit_count: Number of digit to generate.


        :return: A string composed of the request number of digits.
        """
        return ''.join([
            str(random.randint(0, 9))
            for _ in range(digit_count)
        ])

    def __get_contact_verification_request(
            self,
            connection: rdbms.RdbmsConnection = None,
            contact: Contact = None,
            verification_code: str = None,
            request_id: uuid.UUID = None):
        """

        :param connection:
        :param contact:
        :param verification_code:
        :param request_id: The identification of the verification request.


        :return:


        :raise DisabledObjectException: If the verification request has
            expired.

        :raise UndefinedObjectException: If the verification request doesn't
            exist.
        """
        with self.acquire_rdbms_connection(connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    action_type,
                    attempt_count,
                    context,
                    creation_time,
                    expiration_time,
                    last_attempt_time,
                    object_status,
                    request_count,
                    request_id,
                    update_time
                  FROM
                    account_contact_verification
                  WHERE
                    (%(request_id)s IS NOT NULL AND request_id = %(request_id)s)
                    OR (%(verification_code)s IS NOT NULL 
                        AND verification_code = %(verification_code)s
                        AND property_name = %(property_name)s
                        AND property_value = %(property_value)s)
                """,
                {
                    'property_name': contact.property_name,
                    'property_value': contact.property_value,
                    'request_id': request_id,
                    'verification_code': verification_code,
                })

            row = cursor.fetch_one()
            request = row and row.get_object({
                'creation_time': cast.string_to_timestamp,
                'expiration_time': cast.string_to_timestamp,
                'last_attempt_time': cast.string_to_timestamp,
                'object_status': ObjectStatus,
                'request_id': cast.string_to_uuid,
                'update_time': cast.string_to_timestamp,
            })

            if request is None or request.object_status == ObjectStatus.deleted:
                raise self.UndefinedObjectException(f"The verification request doesn't exist")

            # Delete this request if it has expired.
            if request.expiration_time and ISO8601DateTime.now() >= request.expiration_time:
                self.__update_contact_verification_request(request.request_id, ObjectStatus.disabled)
                request.object_status = ObjectStatus.disabled

            if request.object_status == ObjectStatus.disabled:
                raise self.DisabledObjectException(f"The verification request has expired")

            return request

    def __update_contact_verification_request(
            self,
            request_id,
            connection=None,
            object_status=None):
        """
        Update a contact verification request status


        :param request_id: Identification of a contact verification request.

        :param connection: An object `RdbmsConnection` with auto commit.

        :param object_status: An item of the enumeration `ObjectStatus`

            * `deleted`:  The request has been fulfilled.

            * `disabled`: The request has expired.
        """
        if object_status not in (ObjectStatus.deleted, ObjectStatus.disabled):
            raise ValueError("Wrong value of the argument 'object_status'")

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            connection.execute(
                """
                UPDATE 
                    account_contact_verification
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

    def is_contact_available(
            self,
            contact,
            account_id=None,
            connection=None):
        """
        Indicate whether the specified contact information is available and
        verified.

        In the case the contact information would have been already registered
        by a user, indicate whether this contact information has been verified.


        :param contact: An object `Contact`.

        :param account_id: Identification of the account of the user on behalf
            whom this function is called.

        :param connection: An instance `RdbmsConnection` to be used
            supporting the Python clause `with ...:`.


        :return: A tuple containing the following values:

            * `is_available`: `True` if the specified contact information is not
              yet registered by any accounts, or if it has been registered by the
              account on behalf of whom this function is called; `False` otherwise.

            * `is_verified`: `True` if the specified contact information has been
               verified; `False` otherwise.
        """
        with self.acquire_rdbms_connection(connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    is_verified,
                    account_id
                  FROM 
                    account_contact
                  WHERE 
                    property_name = %(property_name)s
                    AND property_value = %(property_value)s
                    AND object_status = %(OBJECT_STATUS_ENABLED)s
                """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'property_name': contact.property_name,
                    'property_value': contact.property_value,
                })
            row = cursor.fetch_one()

            # Check whether this contact information is associated to any accounts.
            if row is None:
                return True, False

            # Retrieve the verification status of this contact information and the
            # account identification of the user who has registered it .
            contact = row.get_object({'account_id': cast.string_to_uuid})

            # If `account_id` has been passed to this function, check whether this
            # user has registered this contact information, in which case this
            # contact information is declared available even if already verified.
            return False if account_id is None else account_id == contact.account_id, contact.is_verified

    def validate_contact_verification_request(
            self,
            connection: rdbms.RdbmsConnection = None,
            contact: Contact = None,
            verification_code: str = None,
            request_id: uuid.UUID = None):
        """
        Indicate whether the specified contact verification request exists.


        :param connection: An object `RdbmsConnection`.

        :param contact: The contact information that the user is verifying.
            The argument `activation_code` MUST be also passed to this
            function.

        :param request_id: identification of the contact verification request.

        :param verification_code: A pseudo-random number (nonce) that was
            generated and sent to the user to verify his contact information.
            The argument `contact` MUST be also passed to this function.


        :return: `True` if the specified identification corresponds to a
            contact verification request registered to the platform;
            `False` otherwise.


        :raise DisabledObjectException: If the contact verification request
            has expired.

        :raise IllegalAccessException: If the verification code is not valid.

        :raise UndefinedObjectException: If the verification code doesn't
            exist.  It may be an expired request that has been deleted.
        """
        request = self.__get_contact_verification_request(
            contact=contact,
            verification_code=verification_code)

        return request

    def request_contact_verification(
            self,
            contact,
            account_id=None,
            connection=None,
            context=None,
            language=DEFAULT_LOCALE,
            verification_code_length=None):
        """
        Request the initiation of the process to verify the specified contact
        information.

        A background task running on the server platform is responsible for
        sending the verification request to the contact address the user has
        provided.  This message contains more likely a HTML link that will
        redirect the user to a web page responsible for confirming this
        contact information (cf. function `confirm_contact`).


        :note: The function ignores any consecutive call for a same contact
            information within a minimal duration of time, to avoid spamming
            the user.

        :note: If a verification request was already generated on behalf of
            another user, the function will silently disable the association
            between this request and this particular user account.  The client
            application MUST request the user who will confirm this contact
            information will have to authenticate in order to add this contact
            information to his account.


        :warning: The function DOESN'T return the identification of the
            verification request so that this identification CANNOT be passed
            to the client application.  Indeed!


        :param contact: An instance `Contact`.

        :param account_id: Identification of the account of the user who
            requests to get his contact information verified.  This argument
            can be `None` when this contact information needs to be verified
            prior to the user account to be created.

        :param connection: A `RdbmsConnection` instance to be used  supporting
            the Python clause `with ...:`.

        :param context: A JSON expression corresponding to the context in
            this contact information has been added and needs to be verified.

        :param language: An object `Locale` referencing the language in which
            to generate the contact information verification request.

        :param verification_code_length: Number of digits to generate the
            verification code.


        :raise IllegalAccessException: If a verification of this contact
            information has been already requested for another account.
        """
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            # Check whether a verification request for this contact information is
            # ongoing.
            cursor = connection.execute(
                """
                SELECT 
                    request_id,
                    account_id,
                    EXTRACT(EPOCH FROM current_timestamp - update_time) AS elapsed_time
                  FROM 
                    account_contact_verification
                  WHERE
                    property_name = %(property_name)s
                    AND property_value = %(property_value)s
                """,
                {
                    'property_name': contact.property_name,
                    'property_value': contact.property_value
                })

            row = cursor.fetch_one()
            request = row and row.get_object({
                'account_id': cast.string_to_uuid,
                'request_id': cast.string_to_uuid
            })

            # Generate a verification request for this contact information if none
            # has been generated so far.
            if request is None:
                verification_code = self.__generate_nonce(
                    min(verification_code_length, self.VERIFICATION_CODE_MAXIMUM_DIGIT_COUNT))

                connection.execute(
                    """
                    INSERT INTO account_contact_verification(
                        account_id,
                        context,
                        language,
                        property_name,
                        property_value,
                        verification_code
                      )
                      VALUES (
                        %(account_id)s,
                        %(context)s,
                        %(language)s,
                        %(property_name)s,
                        %(property_value)s,
                        %(verification_code)s
                      )
                    """,
                    {
                        'account_id': account_id,
                        'context': json.dumps(obj.stringify(context, trimmable=True)),
                        'language': language,
                        'property_name': contact.property_name,
                        'property_value': contact.property_value,
                        'verification_code': verification_code,
                    })

            else:
                # If a verification request was already generated on behalf of another
                # user, we disable the association between this request and a
                # particular user account.  The user who will confirm this contact
                # information will have to authenticate to add this contact information
                # to his account.
                if request.account_id and account_id and request.account_id != account_id:
                    connection.execute(
                        """
                        UPDATE 
                            account_contact_verification
                          SET
                            account_id = NULL,
                            update_time = current_timestamp
                          WHERE
                            request_id = %(request_id)s
                        """,
                        {
                            'request_id': request.request_id
                        })

                # Ignore successive calls for sending a new message to the user that
                # would be requested with a minimal duration of time, to avoid
                # spamming the user.
                if request.elapsed_time > self.MINIMAL_TIME_BETWEEN_CONTACT_VERIFICATION_REQUEST:
                    connection.execute(
                        """
                        UPDATE 
                            account_contact_verification
                          SET
                            request_count = request_count + 1,
                            update_time = current_timestamp
                          WHERE
                            request_id = %(request_id)s
                          """,
                        {
                            'request_id': request.request_id
                        })


















    @staticmethod
    def __group_contacts_by_property_name(contacts):
        """
        Return a dictionary of contacts group by their name.


        :param contacts: A list of objects `Contact`.


        :return: A dictionary where the key corresponds to an item of
            `ContactName` and the value a list of contacts that correspond
            to this contact type.


        :raise AssertError: If a contact information is duplicated.
        """
        contacts_by_property_name = collections.defaultdict(list)

        for contact in contacts:
            assert contact.property_value not in [
                _contact.property_value
                for _contact in contacts_by_property_name[contact.property_name]
            ], \
                'Duplicated contact information'
            contacts_by_property_name[contact.property_name].append(contact)

        return contacts_by_property_name

    @classmethod
    def __subtract_contacts(cls, from_contacts, with_contacts):
        """
        Return a new list of contacts in the first list that are not in the
        second list.


        :note: the function also automatically sets the attribute `is_primary`
            of contact instances to `False` when a contact of the same name is
            in the second list and its attribute `is_primary` is `True`.


        :param from_contacts: a list of contacts to subtract contacts that are
            in the second list.

        :param with_contacts: a list of contacts to be removed from the first
            list of contacts.


        :return: a list with contacts in the first list that are not in the
            second list.
        """
        contact_set1 = cls.__group_contacts_by_property_name(from_contacts)
        contact_set2 = cls.__group_contacts_by_property_name(with_contacts)

        contacts = []

        for contact_name in contact_set1:
            # Check whether a contact of this name has been already set as primary
            # in the second list of contacts.  If so, every contact of this name in
            # the first list must be set as not primary.
            is_primary_contact_already_defined = any([_contact.is_primary for _contact in contact_set2[contact_name]])

            # Retrieve the list of contacts from the first list that don't exist in
            # the second list.
            contacts.extend([
                Contact(
                    contact.property_name,
                    contact.property_value,
                    not is_primary_contact_already_defined and contact.is_primary,
                    contact.is_verified)
                for contact in contact_set1[contact_name]
                if not any([
                    True
                    for _contact in contact_set2[contact_name]
                    if contact.property_value == _contact.property_value
                ])
            ])

        return contacts

    def add_contact(
            self,
            account_id,
            contact,
            connection=None,
            context=None,
            has_been_verified=False,
            language=DEFAULT_LOCALE,
            to_be_verified=False,
            verification_code_length=None):
        """
        Add a given contact information to the specified user account as long
        as this contact information has not been verified by another user.

        If this contact information has been verified, the function will
        silently disable this contact information from account of any user who
        would have added it to their account, and cancel any request that
        would have been generated to verify this contact information.


        :param account_id: identification of the account of the user who adds
            his contact information.

        :param contact: An object `Contact`.

        :param connection: An object `RdbmsConnection` with auto commit.

        :param context: A JSON expression corresponding to the context
            in which this contact has been added and need to be verified.
            This parameter is only used if the parameter `to_be_verified` is
            set to `True`.

        :param has_been_verified: Indicate whether this contact information
            has been verified through a challenge/response process.  This
            parameter is intended to be set by the function `confirm_contact`
            only.

        :param language: An object `Locale` representing the language in which
            to write the email verification request in.

        :param to_be_verified: Indicate whether the platform needs to send a
            request to the user to verify his contact information.  This
            argument cannot be set to `True` if the argument `has_been_verified`
            has been set to `True`.

        :param verification_code_length: Number of digits to generate the
            verification code.

        :raise ContactAlreadyUsedException: if one of the contacts has been
            already registered and verified by another user.

        :raise InvalidArgumentException: if this contact information is stated
            as verified while no challenge process has been passed.
        """
        from majormode.perseus.service.account.account_service import AccountService

        assert not (has_been_verified and to_be_verified), "Conflicted values"

        # Check whether this contact has been already added to this account.
        account = AccountService().get_account(
            account_id,
            check_status=True,
            connection=connection,
            include_contacts=True)

        if contact in account.contacts:
            return

        # Check whether this contact would been added to another user account
        # and whether it would have been verified.
        (is_available, is_verified) = self.is_contact_available(contact, connection=connection)
        if not is_available and is_verified:
            raise self.ContactAlreadyInUseException("Another user has already verified this contact information")

        # Check whether this contact information can been stated verified.
        if contact.is_verified and not has_been_verified and account.account_type not in [
            AccountType.botnet,
            AccountType.sns,
            AccountType.test
        ]:
            raise self.InvalidArgumentException(
                "A contact information cannot be said verified without passing a challenge process")

        # Add this contact information to the specified user account, and
        # generate a verification request if required.
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            # If verified, disable this contact information from any other user
            # account, and cancel any request that would have been generated to
            # verify this contact information.
            if contact.is_verified:
                connection.execute(
                    """
                    UPDATE
                        account_contact
                      SET
                        object_status = %(OBJECT_STATUS_DISABLED)s
                      WHERE
                        property_name = %(property_name)s
                        AND property_value = %(property_value)s
                        """,
                    {
                        'OBJECT_STATUS_DISABLED': ObjectStatus.disabled,
                        'property_name': contact.property_name,
                        'property_value': contact.property_value
                    })

                connection.execute(
                    """
                    DELETE FROM 
                        account_contact_verification
                      WHERE
                        property_name = %(property_name)s
                        AND property_value = %(property_value)s""",
                    {
                        'property_name': contact.property_name,
                        'property_value': contact.property_value
                    })

            # Set this contact information as the primary if it has been verified
            # and it his user doesn't have any other contact information than this
            # one.
            if contact.is_verified and not contact.is_primary and not account.contacts:
                contact.is_primary = True

            # Add this contact information to the specified user account.
            connection.execute(
                """
                INSERT INTO account_contact(
                    account_id,
                    property_name,
                    property_value,
                    is_primary,
                    is_verified)
                  VALUES (
                    %(account_id)s,
                    %(property_name)s,
                    %(property_value)s,
                    %(is_primary)s,
                    %(is_verified)s
                  )
                """,
                {
                    'account_id': account.account_id,
                    'is_primary': contact.is_primary or False,
                    'property_name': contact.property_name,
                    'property_value': contact.property_value,
                    'is_verified': contact.is_verified or False,
                }
            )

            # If this contact information needs to be verified, generate a
            # verification request that will be sent to the user.
            if to_be_verified and account.account_type == AccountType.standard:
                self.request_contact_verification(
                    contact,
                    account_id=account_id,
                    connection=connection,
                    context=context,
                    language=language,
                    verification_code_length=verification_code_length)

    def confirm_contact(
            self,
            connection: rdbms.RdbmsConnection = None,
            verification_code: str = None,
            app_id: uuid.UUID = None,
            contact: Contact = None,
            request_id: uuid.UUID = None):
        """
        Enable a contact information that a user has confirmed through a
        challenge/response verification process


        There are two methods to complete a contact verification process:

        1. Either to provide the identification of the contact verification
           request `request_id`

        2. Either to provide the activation code that was generated with the
           contact verification request, and to provide the contact that was
           requested to be verified (the activation code might not be unique
           among all the contacts that are requested to be verified).

        If the user doesn't have any account, the function will automatically
        create an account for him and associate this contact information to
        his account.

        The function silently deletes any other verification requests that
        would have been initiated by other users for this same contact
        information.  The function also automatically soft-deletes any user
        account that would be only linked to this contact information.

        If the user doesn't have any primary contact information defined of
        this type, the function will automatically set this contact
        information as the primary.


        :warning: this function MUST NOT be directly surfaced to any client
            application, but SHOULD be used by the server controller of a
            client application.


        :param app_id: identification of the client application such as a Web,
            a desktop, or a mobile application, that accesses the service.

        :param connection: An object `RdbmsConnection` with auto commit.

        :param contact: The contact information that the user is verifying.
            The argument `verification_code` MUST be also passed to this
            function.

        :param request_id: identification of the verification request that has
            been sent to the user.

        :param verification_code: A pseudo-random number (nonce) that was
            generated and sent to the user to verify his contact information.
            The argument `contact` MUST be also passed to this function.


        :return: The function returns an instance `contact` or a tuple of
            instances `contact, session` depending on whether the parameter
            `auto_sign_in` has been set to, respectively `False`, or
            `True`:

             * `contact`: an instance containing the following the members:

                * `account_id` (required): identification of the account of the user
                  who has confirmed this contact information.

                * `locale` (optional): an instance `Locale` representing the
                  preferred language that this user has selected when he has added
                  this contact information to his account, or, if not defined at this
                  time, when he has confirmed this contact information or, if still
                  not defined at this time, the default locale.

                * `name` (required): item of the enumeration `ContactName`.

                * `value`: value of this contact information.

            * `session`: an instance containing the following members;

                * `creation_time` (optional): time when this account has been
                  registered.  This information should be stored by the client
                  application to manage its cache of accounts.

                * `expiration_time` (optional): time when the login session will
                  expire.  This information is provided if the client application
                  requires the platform to automatically sign-in the user (cf.
                  parameter `auto_sigin`).

                * `object_status` (optional): current status of this user account.

                * `session_id` (optional): identification of the login session of
                  the user.  This information is provided if the client application
                  requires the platform to automatically sign-in the user (cf.
                  parameter `auto_sign_in`).


        :raise DeletedObjectException: if the user account has been deleted
            while the argument `check_status` has been set to `True`.

        :raise DisabledObjectException: if the user account has been disabled
            while the argument `check_status` has been set to `True`.

        :raise UndefinedObjectException: if the specified identification
            doesn't refer to a user account registered against the platform.
        """
        if request_id is None and verification_code is None:
            raise self.InvalidArgumentException("Either a request ID or an activation code MUST be passed")

        if verification_code and not contact:
            raise self.InvalidArgumentException("A contact information MUST be passed")

        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            cursor = connection.execute(
                """
                DELETE FROM
                    account_contact_verification
                  WHERE
                    (%(request_id)s IS NOT NULL AND request_id = %(request_id)s)
                    OR (%(verification_code)s IS NOT NULL 
                        AND verification_code = %(verification_code)s
                        AND property_name = %(property_name)s
                        AND property_value = %(property_value)s)
                  RETURNING
                    account_id,
                    language,
                    property_name, 
                    property_value
                """,
                {
                    'verification_code': verification_code,
                    'property_name': contact.property_name,
                    'property_value': contact.property_value,
                    'request_id': request_id,
                })

            row = cursor.fetch_one()

            request = row and row.get_object({
                'account_id': cast.string_to_uuid,
                'language': Locale,
                'property_name': ContactName,
            })

            if request is None:
                raise self.UndefinedObjectException("The contact verification request doesn't exist")

            contact = Contact(request.property_name, request.property_value, is_verified=True)

            # Remove reference to this contact information from any other user
            # account.  Cancel any verification request of this contact
            # information.
            self.__cleanse_contact_references(request.account_id, contact, connection=connection)

            # If this request was linked to a particular user account, enable his
            # contact information.
            if request.account_id:
                self.__enable_account_contact(request.account_id, contact, connection=connection)

            return Object(
                account_id=request.account_id,
                contact=contact,
                language=request.language)

    def find_account(self, contact, connection=None):
        """
        Return the account that matches a contact.


        :param contact: An object `Contact`.

        :param connection: An object `RdbmsConnection`.


        :return: `None` if no account matches the specified contact, or an
            object containing the following attributes:

            * `account_id` (required): Identification of the account.

            * `is_primary` (required): Indicate whether this contact information is
              the primary one for the given property.

            * `is_verified` (required): Indicate whether this contact information
              has been verified.

            * `object_status` (required): Current status of this contact information.
        """
        with self.acquire_rdbms_connection(auto_commit=False, connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT
                    account_id,
                    is_primary,
                    is_verified,
                    object_status
                  FROM
                    account_contact
                  WHERE
                    property_name = %(property_name)s
                    AND property_value = %(property_value)s
                """,
                {
                    'property_name': contact.property_name,
                    'property_value': contact.property_value,
                }
            )

            row = cursor.fetch_one()
            account = row and row.get_object({
                'account_id': cast.string_to_uuid,
                'object_status': ObjectStatus
            })

            return account

    def get_contact_verification_request(self, contact):
        """
        Return the request send to a user to verify his contact information.


        :note: this function MUST not be surfaced to client applications.


        :param contact: an instance `Contact`.


        :return: an instance containing the following members:

            * `account_id` (optional): identification of the account of the user
              who requested to verify his contact information, if he was logged in
              when he provided his contact information.

            * `elapsed_time` (required): elapsed time in second between since
              this contact verification request has been generated.

            * `request_id` (required): identification of the contact verification
              request.
        """
        with self.acquire_rdbms_connection(auto_commit=False) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    request_id,
                    account_id,
                    EXTRACT(EPOCH FROM current_timestamp - update_time) AS elapsed_time
                  FROM
                    account_contact_verification
                  WHERE
                    property_name = %(property_name)s
                    AND property_value = %(property_value)s
                """,
                {
                    'property_name': contact.property_name,
                    'property_value': contact.property_value
                })
            row = cursor.fetch_one()

            if row is None:
                raise self.UndefinedObjectException(
                    "No verification request corresponds to the specified contact")

            return row.get_object({
                'account_id': cast.string_to_uuid,
                'request_id': cast.string_to_uuid
            })

    def get_contacts(
            self,
            account_id,
            connection=None,
            property_name=None):
        """
        Return the list of contact information of an account


        :param account_id: Identification of a user account.

        :param connection: An object `RdbmsConnection`.

        :param property_name: An item of the enumeration `ContactName` to
            filter the list of contact information of the user.


        :return: A list of `Contact` objects.
        """
        with self.acquire_rdbms_connection(connection=connection) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    property_name,
                    property_value,
                    is_primary,
                    is_verified
                  FROM
                    account_contact
                  WHERE
                    account_id = %(account_id)s
                    AND object_status = %(OBJECT_STATUS_ENABLED)s
                    AND (%(property_name)s IS NULL OR property_name = %(property_name)s) 
                """,
                {
                    'OBJECT_STATUS_ENABLED': ObjectStatus.enabled,
                    'account_id': account_id,
                    'property_name': property_name,
                })

            contacts = [
                Contact.from_object(row.get_object())
                for row in cursor.fetch_all()
            ]

            return contacts

    def set_primary_contact(
            self,
            account_id,
            contact,
            add_if_not_exists=False,
            connection=None):
        """
        Set the primary contact information of a users

        This new or the existing contact information MUST have been verified.

        The function sets all the contact information of the same type as
        alternates.


        :param account_id: The identification of the account of a user.

        :param contact: An object `Contact` of the contact information of
            the user to set as primary.  The attribute `is_verified` of this
            object MUST be `True`.

        :param add_if_not_exists: Indicate whether to add this contact
            information if it doesn't not exist.

        :param connection: An object `RdbmsConnection` with auto commit.


        :raise InvalidOperationException: If the contact information has not
            been verified yet.

        :raise UndefinedObjectException: If this contact information has not
            been associated to this user account.
        """
        if not contact.is_verified:
            raise self.InvalidArgumentException("The contact information MUST have been verified")

        # Check whether this contact information is already associated to this
        # user.  If not, possibly add this contact information to the user; if
        # already associated to another user, this would raise an exception.
        contacts = self.get_contacts(
            account_id,
            connection=connection,
            property_name=contact.property_name)

        existing_contact = [_ for _ in contacts if _.property_value == contact.property_value]
        if len(existing_contact) == 0:
            if not add_if_not_exists:
                raise self.UndefinedObjectException('This contact information is not associated to this user account')

            self.add_contact(
                account_id,
                contact,
                connection=connection,
                has_been_verified=contact.is_verified)
        else:
            existing_contact = existing_contact[0]

            # Ignore this request if this contact information is already set as the
            # primary contact for this user.
            if existing_contact.property_value == contact.property_value and existing_contact.is_primary:
                return

            # Check whether the contact information already associated to the user
            # has been verified (requirement for primary contact).
            if not existing_contact.is_verified:
                raise self.InvalidOperationException(
                    "A contact information that was not verified cannot be set as primary")

        # Update all the contact information of this type for this user account,
        # setting this particular contact information as the primary, and the
        # other as alternates (if they are not already alternates).
        with self.acquire_rdbms_connection(auto_commit=True, connection=connection) as connection:
            connection.execute(
                """
                UPDATE 
                    account_contact
                  SET
                    is_primary = (property_value = %(property_value)s),
                    update_time = current_timestamp
                  WHERE
                    account_id = %(account_id)s
                    AND property_name = %(property_name)s
                    AND is_primary <> (property_value = %(property_value)s)
                """,
                {
                    'account_id': account_id,
                    'property_name': contact.property_name,
                    'property_value': contact.property_value,
                })
