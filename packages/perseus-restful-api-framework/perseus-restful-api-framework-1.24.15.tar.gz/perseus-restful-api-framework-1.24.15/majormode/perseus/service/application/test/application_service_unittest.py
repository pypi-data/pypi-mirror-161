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
from majormode.perseus.service.account.test.account_service_unittest import AccountServiceTestCase
from majormode.perseus.service.application.application_service import ApplicationService
from majormode.perseus.unittest.base_unittest import BaseApiKeyTestCase

import hashlib
import hmac
import settings
import unittest
import uuid


class ApplicationServiceTestCase(BaseApiKeyTestCase):
    @staticmethod
    def register_application(account_id):
        """
        Register a new application with a random unique name.

        @param account_id: identification of the account of the user who
               registers this application.

        @return: an instance containing the following members:
                 * ``app_id``: identification of the client application.
                 * ``api_key``:  a unique string that identifies the API key.
                 * ``secret_key``:  a string that must be kept secret, which
                   is used to authenticate the API key.
                 * ``creation_time``: time when the API key has been
                   registered.
       """
        return ApplicationService().register_application(
            account_id,
            'test_%s' % uuid.uuid1().hex,
            ApplicationService.ApplicationPlatform.web)

    """
    Unit testing of the API key service.
    """
    def test_generate_api_key_with_invalid_account(self):
        """
        Generate a random identification of a user's account and try to
        register a new API key, which operation has to raise the exception
        ``UndefinedObjectException``.
        """
        self.assertRaises(AccountService.UndefinedObjectException,
            ApplicationService().register_application,
            uuid.uuid1().hex, 'test', 'mobile')

    def test_generate_api_key_with_duplicate_title(self):
        """
        Register two API keys with the same title, which operation has to
        raise the exception ``ApplicationTitleAlreadyRegisteredException``.
        """
        application_name = uuid.uuid1().hex
        ApplicationService().register_application(self.unittest_account_id, application_name, 'mobile')
        self.assertRaises(ApplicationService.ApplicationNameAlreadyRegisteredException,
            ApplicationService().register_application,
            self.unittest_account_id, application_name, ApplicationService.ApplicationPlatform.mobile)

    def test_assert_invalid_request_signature(self):
        """
        Register an API key and check a virtual API HTTP request providing the
        wrong signature, which operation has to raise the exception
        ``IncorrectSignatureException``.
        """
        application_name = uuid.uuid1().hex
        application = ApplicationService().register_application(self.unittest_account_id, application_name,
            ApplicationService.ApplicationPlatform.mobile)

        api_url = '/resource/01234567890'
        api_sig = hmac.new(str(application.secret_key), msg=api_url, digestmod=hashlib.sha1).hexdigest()
        self.assertRaises(ApplicationService.IncorrectSignatureException,
                          ApplicationService().validate_signature,
                          application.api_key, api_url, None, hashlib.md5(api_sig).hexdigest())

    def test_assert_valid_request_signature(self):
        """
        Register an API key and check a virtual API HTTP request providing the
        correct signature, which operation should succeed.
        """
        application_name = uuid.uuid1().hex
        application = ApplicationService().register_application(self.unittest_account_id, application_name, 'mobile')

        api_url = '/resource/01234567890'
        api_sig = hmac.new(str(application.secret_key), msg=api_url, digestmod=hashlib.sha1).hexdigest()
        ApplicationService().validate_signature(application.api_key, api_url, None, api_sig)

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(ApplicationServiceTestCase))
    return test_suite

if __name__ == '__main__':
    unittest.main()
