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
from majormode.perseus.unittest.base_unittest import BaseApiKeyTestCase

import hashlib
import settings
import unittest
import uuid

class AccountServiceTestCase(BaseApiKeyTestCase):
    @staticmethod
    def generate_account(app_id=settings.PLATFORM_UNITTEST_APP_ID,
            account_type=AccountService.AccountType.test):
        nonce = uuid.uuid1().hex
        account = AccountService().sign_up(app_id, 'test_%s@example.com' % nonce,
            fullname='Test %s' % nonce,
            password=nonce[:16],
            account_type=account_type)
        return AccountService().get_account(account.account_id)

    @staticmethod
    def generate_accounts(app_id, size, reused=False):
        if reused == False:
            accounts = [ AccountServiceTestCase.generate_account(app_id) for _ in range(size) ]
        else:
            accounts = []
            for i in range(size):
                email_address = 'test_%s@example.com' % i
                try:
                    account = AccountService().get_account_by_contact_information(
                        (AccountService.VCardPropertyName.EMAIL, email_address))
                except AccountService.UndefinedObjectException:
                    account = AccountService().sign_up(app_id, email_address,
                        fullname='Test %s' % i,
                        password=uuid.uuid1().hex[:16],
                        account_type=AccountService.AccountType.test)
                accounts.append(account)

        return accounts

    @staticmethod
    def generate_credentials():
        nonce = uuid.uuid1().hex
        return ('Test %s' % nonce,
                'test_%s@example.com' % nonce,
                nonce[:16])

    def test_sign_up_with_invalid_credentials(self):
        """
        Test the method ``sign_up`` providing invalid credentials, i.e.,
        several combinations of email address and password that don't respect
        the requirements.
        """
        INVALID_CREDENTIALS = [
            # Email address doesn't respect requirements.
            ('Joe Bar', '%s@examplecom', 'K57p2N6p', 'email address must include top-level domain (TLD)'),
            ('Joe Bar', '%s@example.', 'K57p2N6p', 'email address must include valid top-level domain (TLD)'),
            ('Joe Bar', '%s@.com', 'K57p2N6p', 'email address must include a subdomain name'),

            # Password doesn't respect requirements.
            ('Joe Bar', '%s@example.com', 'bar', 'password must be longer that 6 characters'),
            ('Joe Bar', '%s@example.com', '1234567890123456789', 'password must shorter than 18 characters'),
        ]

        for (fullname, email_address, password, failure_reason) in INVALID_CREDENTIALS:
            email_address = email_address % uuid.uuid1().hex
            try:
                account = AccountService().sign_up(self.unittest_account_id, email_address,
                    fullname=fullname, password=password,
                    account_type=AccountService.AccountType.test)
                self.assertTrue(False, failure_reason)
            except AccountService.InvalidArgumentException:
                pass

    def test_sign_up_with_valid_credentials(self):
        (fullname, email_address, password) = self.generate_credentials()
        account = AccountService().sign_up(self.unittest_account_id, email_address,
            fullname=fullname, password=password,
            account_type=AccountService.AccountType.test)

    def test_sign_up_with_duplicate_email_address(self):
        (fullname, email_address, password) = self.generate_credentials()
        account = AccountService().sign_up(self.unittest_account_id, email_address,
            fullname=fullname, password=password,
            account_type=AccountService.AccountType.test)
        self.assertRaises(AccountService.EmailAddressAlreadyRegisteredException, AccountService().sign_up,
                self.unittest_app_id, email_address,
                fullname=fullname, password=password,
                account_type=AccountService.AccountType.test)

    def test_sign_in_with_invalid_credentials(self):
        (fullname, email_address, password) = self.generate_credentials()
        AccountService().sign_up(self.unittest_app_id, email_address,
            fullname=fullname, password=password,
            account_type=AccountService.AccountType.test)
        self.assertRaises(AccountService.AuthenticationFailureException, AccountService().sign_in,
            self.unittest_app_id, email_address, hashlib.md5(password).hexdigest())

    def test_sign_in_with_valid_credentials(self):
        (fullname, email_address, password) = self.generate_credentials()
        account = AccountService().sign_up(self.unittest_account_id, email_address,
            fullname=fullname, password=password,
            account_type=AccountService.AccountType.test)
        AccountService().sign_in(self.unittest_app_id, email_address, password)

    def test_sign_out(self):
        (fullname, email_address, password) = self.generate_credentials()
        account = AccountService().sign_up(self.unittest_account_id, email_address,
            fullname=fullname, password=password,
            account_type=AccountService.AccountType.test)
        session = AccountService().sign_in(self.unittest_app_id, email_address, password)
        AccountService().sign_out(self.unittest_app_id, account.account_id, session.session_id)

    def test_sign_out_with_invalid_session(self):
        (fullname, email_address, password) = self.generate_credentials()
        account = AccountService().sign_up(self.unittest_account_id, email_address,
            fullname=fullname, password=password,
            account_type=AccountService.AccountType.test)
        AccountService().sign_in(self.unittest_app_id, email_address, password)
        self.assertRaises(AccountService.IllegalAccessException, AccountService().sign_out,
            self.unittest_app_id, account.account_id, uuid.uuid1().hex)

    def test_sign_out_with_invalid_account(self):
        (fullname, email_address, password) = self.generate_credentials()
        account = AccountService().sign_up(self.unittest_account_id, email_address,
            fullname=fullname, password=password,
            account_type=AccountService.AccountType.test)
        session = AccountService().sign_in(self.unittest_app_id, email_address, password)
        self.assertRaises(AccountService.UndefinedObjectException, AccountService().sign_out,
            self.unittest_app_id,uuid.uuid1().hex, session.session_id)

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(AccountServiceTestCase))
    return test_suite

if __name__ == '__main__':
    unittest.main()
