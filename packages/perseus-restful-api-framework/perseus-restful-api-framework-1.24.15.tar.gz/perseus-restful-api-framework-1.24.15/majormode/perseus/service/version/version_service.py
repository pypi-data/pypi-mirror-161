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

from majormode.perseus.model.version import Version
from majormode.perseus.service.base_service import BaseService

import settings


class VersionService(BaseService):
    """
    This service surfaces the current version of the API deployed on the
    requested environment stage.  This enables a check of the client
    application against the latest version of the API to ensure
    compatibility.  If there is a discrepancy between the two, the client
    application should be prompted to update accordingly.

    The client application verifies compatibility with the latest API
    version through comparing its sequence identifier, which follows the
    form of ``major.minor.patch-build``.  These four variables represent
    the degree of modifications to the API, and will increment based on
    the nature of new developments.
    """
    def get_version(self, app_id):
        """
        Return a ``Version`` instance providing a string representing the
        version of the platform API currently deployed on the environment
        stage that is queried.

        @param app_id: identification of the client application such as a Web,
               a desktop, or a mobile application, that accesses the service.

        @return: a ``Version`` instance.
        """
        return Version(settings.API_VERSION)
