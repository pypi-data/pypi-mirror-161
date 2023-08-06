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
from majormode.perseus.model.obj import Object
from majormode.perseus.service.base_http_handler import HttpRequestHandler
from majormode.perseus.service.base_http_handler import http_request
from majormode.perseus.service.status.status_service import StatusService

import settings
import socket


class StatusServiceHttpRequestHandler(HttpRequestHandler):
    @http_request(r'^/ping$',
                  http_method=HttpMethod.GET,
                  authentication_required=False,
                  signature_required=False)
    def ping(self, request):
        """
        Provide a simple mechanism to help developers or other remote services
        ensure that their software is interacting correctly with the web
        services infrastructure, to measure the round-trip time for requests
        sent from the local host to the Web services server.
        """
        return Object(node='{}:{}'.format(
            socket.gethostbyname(socket.gethostname()),
            settings.DEFAULT_SERVER_PORT))

    @http_request(r'^/status$',
                  http_method=HttpMethod.GET,
                  authentication_required=True,
                  signature_required=True)
    def status(self, request):
        return StatusService().check_status()
