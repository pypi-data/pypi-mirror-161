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

import urllib.request

from majormode.perseus.constant.http import HttpMethod


class GoogleCloudMessagingRequest(urllib.request.Request):
    """
    Extension of ``urllib.request.Request`` class to support the explicit
    specification of a HTTP method.
    """
    def __init__(self, *args, **kwargs):
        http_method = kwargs.pop('http_method', None)
        self._method = None if http_method is None else str(http_method)
        urllib.request.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return self._method if self._method is not None \
            else super(GoogleCloudMessagingRequest.Request, self).get_method()

    def __str__(self):
        curl_expression =  'curl -X%s ' % str(self._method)

        if len(self.headers) > 0:
            curl_expression += ' '.join(['--header "%s: %s"' % (name, value)
                    for (name, value) in self.headers.iteritems() ])

        curl_expression += ' %s' % self.get_full_url()

        if self._method == str(HttpMethod.POST) and len(self.data) > 0:
            curl_expression += " -d '%s'" % self.data

        return curl_expression
