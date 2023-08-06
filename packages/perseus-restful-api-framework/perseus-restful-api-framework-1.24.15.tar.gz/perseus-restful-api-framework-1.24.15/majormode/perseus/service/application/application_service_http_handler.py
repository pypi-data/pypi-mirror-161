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
from majormode.perseus.service.application.application_service import ApplicationService


class ApplicationServiceHttpRequestHandler(HttpRequestHandler):
    @http_request(r'^/applications$',
                  http_method=HttpMethod.GET,
                  authentication_required=True,
                  signature_required=True)
    def get_applications(self, request):
        return ApplicationService().get_applications(request.app_id, request.account_id)


    @http_request(r'^/application$',
                  http_method=HttpMethod.POST,
                  authentication_required=True,
                  signature_required=True)
    def register_application(self, request):
        name = request.get_argument(
            'name',
            data_type=HttpRequest.ArgumentDataType.string)

        stage = request.get_argument(
            'stage',
            data_type=HttpRequest.ArgumentDataType.enumeration,
            enumeration=ApplicationService.ApplicationStage,
            default_value=ApplicationService.ApplicationStage.sandbox)

        platform = request.get_argument(
            'platform',
            data_type=HttpRequest.ArgumentDataType.enumeration,
            enumeration=ApplicationService.ApplicationPlatform)

        return ApplicationService().register_application(
            request.account_id, name, platform,
            stage=stage)

    @http_request(r'^/application/(app_id:uuid)$',
                  http_method=HttpMethod.PUT,
                  authentication_required=True,
                  signature_required=True)
    def update_application(self, request, app_id):
        return ApplicationService().update_application(request.app_id, request.account_id, app_id, request.body)
