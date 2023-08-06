# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Majormode.  All rights reserved.
#
# This software is the confidential and proprietary information of
# Majormode or one of its subsidiaries.  You shall not disclose this
# confidential information and shall use it only in accordance with
# the terms of the license agreement or other applicable agreement you
# entered into with Majormode.
#
# MAJORMODE MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE
# SUITABILITY OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.  MAJORMODE
# SHALL NOT BE LIABLE FOR ANY LOSSES OR DAMAGES SUFFERED BY LICENSEE
# AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS
# DERIVATIVES.
#
# @version $Revision: 344 $

from __future__ import with_statement

from majormode.perseus.model.version import Version
from majormode.perseus.service.version.version_service import VersionService
from majormode.perseus.unittest.base_unittest import BaseApiKeyTestCase

import random
import settings
import sys
import unittest

class VersionServiceTestCase(BaseApiKeyTestCase):
    @staticmethod
    def __version_generator__():
        while True:
            major = random.randint(0, sys.maxint)
            minor = random.randint(0, sys.maxint)
            patch = random.randint(0, sys.maxint)
            yield Version('%s.%s.%s' % (major, minor, patch))

    def setup(self):
        super(VersionServiceTestCase, self).__init__()
        random.seed()

    def test_version_wellformed(self):
        """
        Test the well-formed string representations of version.
        """
        Version('0.0.0')
        Version('1.0.0')
        Version('1.2.0')
        Version('1.2.3')
        _ = [ self.__version_generator__().next() for _ in xrange(100) ]

    def test_versions_malformed(self):
        """
        Test the malformed string representations of version.
        """
        self.assertRaises(Version.InvalidVersionFormatException, Version, 'a.b.c', True)
        self.assertRaises(Version.InvalidVersionFormatException, Version, '1.b.c', True)
        self.assertRaises(Version.InvalidVersionFormatException, Version, '1.2.c', True)

        self.assertRaises(Version.InvalidVersionFormatException, Version, '-1.-1.-1', True)
        self.assertRaises(Version.InvalidVersionFormatException, Version, '-1.-1.3', True)
        self.assertRaises(Version.InvalidVersionFormatException, Version, '-1.2.3', True)

        self.assertRaises(Version.InvalidVersionFormatException, Version, '1a.2.3', True)
        self.assertRaises(Version.InvalidVersionFormatException, Version, '1.2b.3', True)
        self.assertRaises(Version.InvalidVersionFormatException, Version, '1.2.3c', True)

    def test_version_comparisons(self):
        """
        Test common comparison operations of version objects.
        """
        self.assertEqual(Version('0.0.0'), Version('0.0.0'))
        self.assertEqual(Version('1.0.0'), Version('1.0.0'))
        self.assertEqual(Version('1.2.0'), Version('1.2.0'))
        self.assertEqual(Version('1.2.3'), Version('1.2.3'))

        self.assertGreater(Version('1.2.3'), Version('1.2.2'))
        self.assertLess(Version('1.2.2'), Version('1.2.3'))
        self.assertGreater(Version('1.2.3'), Version('1.1.4'))
        self.assertLess(Version('1.1.4'), Version('1.2.3'))
        self.assertGreater(Version('2.2.3'), Version('2.1.4'))

        generator = self.__version_generator__()
        for (a, b) in [ (generator.next(), generator.next()) for _ in xrange(100) ]:
            if a.major > b.major:
                self.assertGreater(a, b)
            elif a.major < b.major:
                self.assertLess(a, b)
            elif a.minor > b.minor:
                self.assertGreater(a, b)
            elif a.minor < b.minor:
                self.assertLess(a, b)
            elif a.patch > b.patch:
                self.assertGreater(a, b)
            elif a.patch < b.patch:
                self.assertLess(a, b)
            else:
                self.assertEqual(a, b)

    def test_api_version(self):
        """
        Get the version of the platform API currently deployed.
        """
        self.assertEqual(VersionService().get_version(self.unittest_app_id),
                         Version(settings.API_VERSION))

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(VersionServiceTestCase))
    return test_suite

if __name__ == '__main__':
    unittest.main()
