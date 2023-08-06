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

from majormode.perseus.constant.http import HttpMethod
from majormode.perseus.service.base_http_handler import HttpRequest
from majormode.perseus.service.base_http_handler import HttpRequestHandler
from majormode.perseus.service.base_http_handler import http_request
from majormode.perseus.service.team.team_service import TeamService


class TeamServiceHttpRequestHandler(HttpRequestHandler):
    @http_request(r'^/team/invitation/(invitation_code)$',
                  http_method=HttpMethod.PUT,
                  authentication_required=False)
    def accept_or_decline_invitation(self, request, invitation_code):
        does_accept = request.get_argument('accept',
                argument_passing=HttpRequest.ArgumentPassing.query_string,
                data_type=HttpRequest.ArgumentDataType.boolean,
                is_required=True)
        return TeamService().accept_invitation(request.app_id, invitation_code, account_id=request.account_id) if does_accept \
                else TeamService().decline_invitation(request.app_id, invitation_code, account_id=request.account_id)

    @http_request(r'^/team/invitation/(invitation_id:uuid)$',
                  http_method=HttpMethod.DELETE,
                  authentication_required=True)
    def cancel_invitation(self, request, invitation_id):
        return TeamService().cancel_invitation(request.app_id, request.account_id, invitation_id)

    @http_request(r'^/team$',
                  http_method=HttpMethod.POST,
                  authentication_required=True)
    def create_team(self, request):
        name = request.get_argument('name',
                data_type=HttpRequest.ArgumentDataType.string,
                is_required=True)
        description = request.get_argument('description',
                data_type=HttpRequest.ArgumentDataType.string,
                is_required=False)
        invitation_url = request.get_argument('invitation_url',
                data_type=HttpRequest.ArgumentDataType.string,
                is_required=False)
        invitation_email = request.get_argument('invitation_email',
                data_type=HttpRequest.ArgumentDataType.string,
                is_required=False)
        return TeamService().create_team(request.app_id, request.account_id, name,
                description=description,
                invitation_url=invitation_url,
                invitation_email=invitation_email)

    @http_request(r'^/team/(team_id:uuid)/invitation$',
                  http_method=HttpMethod.GET,
                  authentication_required=True)
    def get_invitations(self, request, team_id):
        offset = request.get_argument('offset',
                data_type=HttpRequest.ArgumentDataType.integer,
                is_required=False,
                default_value=0)
        limit = request.get_argument('limit',
                data_type=HttpRequest.ArgumentDataType.integer,
                is_required=False,
                default_value=TeamService.DEFAULT_LIMIT)
        return TeamService().get_invitations(request.app_id, request.account_id, team_id,
                offset=offset, limit=limit)

    @http_request(r'^/team/(team_id:uuid)/member/(account_id:uuid)$',
                  http_method=HttpMethod.GET,
                  authentication_required=True)
    def get_member(self, request, team_id, account_id):
        return TeamService().get_member(request.app_id, request.account_id, team_id, account_id)

    # @http_request(r'^/team/(team_id:uuid)/member$',
    #               http_method=HttpMethod.GET,
    #               authentication_required=True)
    # def get_members(self, request, team_id):
    #     offset = request.get_argument('offset',
    #             data_type=HttpRequest.ArgumentDataType.integer,
    #             is_required=False,
    #             default_value=0)
    #     limit = request.get_argument('limit',
    #             data_type=HttpRequest.ArgumentDataType.integer,
    #             is_required=False,
    #             default_value=TeamService.DEFAULT_LIMIT)
    #     return TeamService().get_members(request.app_id, request.account_id, team_id,
    #             offset=offset, limit=limit)

    @http_request(r'^/team$',
                  http_method=HttpMethod.GET,
                  authentication_required=False)
    def get_teams(self, request):
        keywords = request.get_argument('keywords',
                data_type=HttpRequest.ArgumentDataType.list,
                item_data_type=HttpRequest.ArgumentDataType.string,
                is_required=False)

        limit = request.get_argument('limit',
                data_type=HttpRequest.ArgumentDataType.integer,
                is_required=False,
                default_value=TeamService.DEFAULT_LIMIT)

        offset = request.get_argument('offset',
                data_type=HttpRequest.ArgumentDataType.integer,
                is_required=False,
                default_value=0)

        return TeamService().search_teams(request.app_id, request.account_id, keywords,
                limit=limit, offset=offset) if keywords \
            else TeamService().get_account_teams(request.app_id, request.account_id,
                limit=limit, offset=offset)

    @http_request(r'^/team/(team_id:uuid)/invitation$',
                  http_method=HttpMethod.POST,
                  authentication_required=True)
    def invite_users(self, request, team_id):
        if not isinstance(request.body, list):
            raise TeamService.InvalidArgumentException('Require a list of users identified either by their account identifications, either their email address')
        return TeamService().invite_users(request.app_id, request.account_id, team_id, request.body)

    @http_request(r'^/team/(team:uuid)/agent/(account_id:uuid)$',
                  http_method=HttpMethod.PUT,
                  authentication_required=True)
    def promote_agent(self, request, team_id, account_id):
        return TeamService().promote_agent(request.app_id, request.account_id, team_id, account_id)

    @http_request(r'^/team/(team_id:uuid)/member/(account_id:uuid)$',
                  http_method=HttpMethod.DELETE,
                  authentication_required=True)
    def revoke_member(self, request, team_id, account_id):
        return TeamService().revoke_member(request.app_id, request.account_id, team_id, account_id)

    @http_request(r'^/team/(team_id:uuid)/join$',
                  http_method=HttpMethod.POST,
                  authentication_required=True)
    def submit_join_request(self, request, team_id):
        return TeamService().request_membership(request.app_id, request.account_id, team_id)

    @http_request(r'^/team/(team_id:uuid)/member/(account_id:uuid)/role$',
                  http_method=HttpMethod.PUT,
                  authentication_required=True)
    def update_member_role(self, request, team_id, account_id):
        is_administrator = request.get_argument('is_administrator',
                data_type=HttpRequest.ArgumentDataType.boolean)
        return TeamService().update_member_role(request.app_id, request.account_id,
                team_id, account_id, is_administrator)

    @http_request(r'^/team/(team_id:uuid)/membership$',
                  http_method=HttpMethod.DELETE,
                  authentication_required=True)
    def withdraw_membership(self, request, team_id):
        return TeamService().withdraw_membership(request.app_id, request.account_id, team_id)
