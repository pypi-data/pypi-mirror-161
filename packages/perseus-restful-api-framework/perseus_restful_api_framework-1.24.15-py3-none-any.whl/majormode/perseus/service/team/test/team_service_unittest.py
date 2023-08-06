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

from __future__ import with_statement

from majormode.perseus.service.account.account_service import AccountService
from majormode.perseus.service.account.test.account_service_unittest import AccountServiceTestCase
from majormode.perseus.service.team.team_service import TeamService
from majormode.perseus.unittest.base_unittest import BaseApiKeyTestCase

import unittest
import uuid

class TeamServiceTestCase(BaseApiKeyTestCase):
    FAKE_INVITE_URL = 'http://www.example.com/team/invite/%(invite_code)s'

    def test_add_team(self):
        TeamService().add_team(self.unittest_app_id, self.unittest_account_id,
            'test_%s' % uuid.uuid1().hex)

    def test_add_duplicated_team(self):
        name = 'test_%s' % uuid.uuid1().hex
        TeamService().add_team(self.unittest_app_id, self.unittest_account_id, name)
        self.assertRaises(TeamService.NameAlreadyUsedException,
            TeamService().add_team,
            self.unittest_app_id, self.unittest_account_id, name)

    def test_get_teams(self):
        TeamService().add_team(self.unittest_app_id, self.unittest_account_id,
            'test_%s' % uuid.uuid1().hex)
        TeamService().get_teams(self.unittest_app_id, self.unittest_account_id)

    def test_invite_users(self):
        team = TeamService().add_team(self.unittest_app_id, self.unittest_account_id,
            'test_%s' % uuid.uuid1().hex, invite_url=self.FAKE_INVITE_URL)
        account = AccountServiceTestCase.generate_account(self.unittest_app_id)
        TeamService().invite_users(self.unittest_app_id, self.unittest_account_id,
            team.team_id, [ account.email_address ])

    def test_invite_duplicated_master_members(self):
        team = TeamService().add_team(self.unittest_app_id, self.unittest_account_id,
            'test_%s' % uuid.uuid1().hex, invite_url=self.FAKE_INVITE_URL)

        account = AccountService().get_account(self.unittest_account_id)
        TeamService().invite_users(self.unittest_app_id, self.unittest_account_id,
            team.team_id, [ account.email_address ])

    def test_invite_duplicated_members(self):
        team = TeamService().add_team(self.unittest_app_id, self.unittest_account_id,
            'test_%s' % uuid.uuid1().hex, invite_url=self.FAKE_INVITE_URL)

        account = AccountServiceTestCase.generate_account(self.unittest_app_id)
        TeamService().invite_users(self.unittest_app_id, self.unittest_account_id,
            team.team_id, [ account.email_address ])
        TeamService().invite_users(self.unittest_app_id, self.unittest_account_id,
            team.team_id, [ account.email_address ])

    def test_accept_invite(self):
        team = TeamService().add_team(self.unittest_app_id, self.unittest_account_id,
            'test_%s' % uuid.uuid1().hex, invite_url=self.FAKE_INVITE_URL)
        account = AccountServiceTestCase.generate_account(self.unittest_app_id)
        TeamService().invite_users(self.unittest_app_id, self.unittest_account_id,
            team.team_id, [ account.email_address ])
        invite_secured_key = TeamService()._get_invite_secured_key(team.team_id, account.account_id)
        TeamService().accept_invite(self.unittest_app_id, invite_secured_key)

    def test_decline_invite(self):
        team = TeamService().add_team(self.unittest_app_id, self.unittest_account_id,
            'test_%s' % uuid.uuid1().hex, invite_url=self.FAKE_INVITE_URL)
        account = AccountServiceTestCase.generate_account(self.unittest_app_id)
        TeamService().invite_users(self.unittest_app_id, self.unittest_account_id,
            team.team_id, [ account.email_address ])
        invite_secured_key = TeamService()._get_invite_secured_key(team.team_id, account.account_id)
        TeamService().decline_invite(self.unittest_app_id, invite_secured_key)

    def test_revoke_member(self):
        team = TeamService().add_team(self.unittest_app_id, self.unittest_account_id,
            'test_%s' % uuid.uuid1().hex, invite_url=self.FAKE_INVITE_URL)
        account = AccountServiceTestCase.generate_account(self.unittest_app_id)
        TeamService().invite_users(self.unittest_app_id, self.unittest_account_id,
            team.team_id, [ account.email_address ])
        invite_secured_key = TeamService()._get_invite_secured_key(team.team_id, account.account_id)
        TeamService().accept_invite(self.unittest_app_id, invite_secured_key, account.account_id)

        TeamService().revoke_member(self.unittest_app_id, self.unittest_account_id,
            team.team_id, account.account_id)
        self.assertRaises(TeamService.InvalidOperationException, TeamService().revoke_member,
            self.unittest_app_id, self.unittest_account_id,
            team.team_id, account.account_id)

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TeamServiceTestCase))
    return test_suite

if __name__ == '__main__':
    unittest.main()
