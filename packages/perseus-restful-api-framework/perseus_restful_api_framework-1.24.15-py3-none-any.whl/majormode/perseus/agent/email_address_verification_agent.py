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

import contextlib
import json
import logging
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import traceback

from majormode.perseus.agent.email_sender_agent import EmailSenderAgent
from majormode.perseus.constant.contact import ContactName
from majormode.perseus.model.locale import DEFAULT_LOCALE
from majormode.perseus.model.locale import Locale
from majormode.perseus.utils import cast
from majormode.perseus.utils import rdbms


class EmailAddressVerificationAgent(EmailSenderAgent):
    # Regular expression matching the pattern of a placeholder where its
    # name needs to be replaced by its corresponding value.
    #
    # Placeholder names are surrounded by "::" and "::".  Placeholder names
    # must consist of any letter (A-Z), any digit (0-9), an underscore, or
    # a dot.  Placeholder names must start with a letter.
    REGEX_PLACEHOLDER_NAME = re.compile(r'::((?i)[a-z][a-z0-9_.]*)::')

    MAXIMUM_BATCH_SIZE = 1000

    def __init__(
            self,
            smtp_connection_properties,
            rdbms_connection_properties,
            template_url,
            verbose=False):
        super().__init__(smtp_connection_properties)

        self.rdbms_connection_properties = rdbms_connection_properties
        self.template_url = template_url
        self.verbose = verbose

    @classmethod
    def expand_placeholders_value(cls, content, placeholders, ignore_unused_placeholders=False):
        """
        Replace the placeholders defined in the given content with their
        corresponding values.


        :param content: The content with placeholders {{placeholder}} to be
            replaced with their corresponding values.

        :param placeholders: A dictionary where the key corresponds to the
            name of a placeholder, the value corresponding to the value of the
            placeholder.

        :param ignore_unused_placeholders: Indicate whether to ignore
            placeholders that would have been defined but that would have not
            been declared in the given content.


        :return: The content where the placeholders have been replaced with
            their corresponding values.
        """
        # Find the list of placeholder names that have been used in the given
        # document but that have not been defined with a corresponding value.
        used_placeholders = set([
            (match.group(0), match.group(1))
            for match in cls.REGEX_PLACEHOLDER_NAME.finditer(content)
        ])

        used_placeholder_names = [name for (_, name) in used_placeholders]

        if used_placeholders:
            undefined_placeholder_names = [
                name
                for name in used_placeholder_names
                if name not in placeholders
            ]

            assert len(undefined_placeholder_names) == 0, \
                "The following placeholders are declared but have not been defined: " \
                f"{','.join(undefined_placeholder_names)}"

        # Find the list of placeholder names that have been defined but have not
        # been used in the given document.
        if placeholders:
            unused_placeholder_names = [
                name
                for name in placeholders
                if name not in used_placeholder_names
            ]

            if len(unused_placeholder_names) > 0:
                warning_message = "The following placeholders are defined but have not been declared: " \
                    f"{','.join(unused_placeholder_names)}"
                assert ignore_unused_placeholders, warning_message
                logging.warning(warning_message)

        # Replace the placeholders referred in the content by their
        # corresponding value.
        for (placeholder_expression, placeholder_name) in used_placeholders:
            content = content.replace(placeholder_expression, placeholders[placeholder_name])

        return content

    def fetch_html_template(
            self,
            locale=None,
            maximum_attempt_count=3,
            sleep_duration_between_attempts=10):
        """
        Fetch the HTML template from its URL.


        @note: the function doesn't handle cached version of HTML template.
            The function fetches the HTML template URL each the function is
            called.  The reason is the HTML template may be changed and
            caching the HTML template would result in returning a deprecated
            version.


        :param locale: an instance `Locale` that indicates the language of
            the HTML template to fetch should be written in.  If this HTML
            template is available for the specified language, the function
            returns the HTML template written is the closest language to the
            one specified, or the default language.

        :param maximum_attempt_count: maximal number of failed attempts to
            fetch the HTML template URL before the function raises an
            exception.

        :param sleep_duration_between_attempts: indicate the time in seconds
            during which the current thread is suspended when an attempt to
            fetch the HTML template URL fails, before attempting again.


        :return: the content of the HTML template in the specified language,
            or the closest language if the HTML template is not available in
            the specified language.


        :raise Exception: if all the attempts in fetching the HTML template
            URL have failed.
        """
        attempt_count = 0

        while True:
            try:
                opener = urllib.request.build_opener()

                opener.addheaders = [
                    ('User-Agent', 'Mozilla/5.0'),
                    ('Accept-Language', (locale or DEFAULT_LOCALE).to_http_string())
                ]

                with contextlib.closing(opener.open(self.template_url)) as handle:
                    return handle.read().decode()

            except urllib.error.URLError:
                logging.debug(traceback.print_exc())
                logging.error(f"An HTTP error occurred while fetching the URL {self.template_url}")

                attempt_count += 1
                if attempt_count > maximum_attempt_count:
                    raise Exception("All the attempts in fetching the specified URL have failed")

                time.sleep(sleep_duration_between_attempts)

    def fetch_requests(
            self,
            limit=None):
        """
        Return a list of unverified email addresses that their respective
        users are requested to confirm.


        :param limit: maximum number of email address verification requests to
            be returned.


        :return: a list of instance containing the following members:

            * `account_id` (required): identification of the account of the user
              who provided  his email address.

            * `email_address` (required): email_address of the user.

            * `context` (optional): A JSON expression corresponding to the context
              in which this contact has been added and needs to be verified.

            * `creation_time` (required): time when the user provided this email
              address.

            * `locale` (optional): an instance `Locale` referring to the preferred
              language of the user.

            * `request_id` (required): identification of the contact information
              request.
        """
        with rdbms.RdbmsConnection.acquire_connection(
                self.rdbms_connection_properties,
                auto_commit=False) as connection:
            cursor = connection.execute(
                """
                SELECT 
                    request_id,
                    account_id,
                    value AS email_address,
                    locale,
                    context,
                    request_count,
                    attempt_count,
                    creation_time,
                    update_time,
                    attempt_time
                  FROM 
                    account_contact_verification
                  WHERE 
                    (attempt_time IS NULL OR current_timestamp - attempt_time >= '1 day'::interval)
                    AND name = %(name)s
                  ORDER BY 
                    attempt_time ASC NULLS FIRST
                  LIMIT %(limit)s
                """,
                {
                    'limit': min(limit or self.MAXIMUM_BATCH_SIZE, self.MAXIMUM_BATCH_SIZE),
                    'name': ContactName.EMAIL
                })

            requests = [
                row.get_object({
                    'account_id': cast.string_to_uuid,
                    'attempt_time': cast.string_to_timestamp,
                    'context': cast.string_to_json,
                    'creation_time': cast.string_to_timestamp,
                    'locale': Locale,
                    'request_id': cast.string_to_uuid,
                    'update_time': cast.string_to_timestamp
                })
                for row in cursor.fetch_all()
            ]

            return requests

    @staticmethod
    def get_subject(content):
        """
        Return the subject of the HTML email taken from the title of the HTML
        template.


        :return: the subject of the HTML email template.


        :raise AssertError: If the content of the HTML email template has not
            been read, of if this HTML has no title defined.
        """
        start_offset = content.find('<title>')
        assert start_offset > 0, "The HTML template has no title defined"
        start_offset = content.find('>', start_offset) + 1

        end_offset = content.find('</title>', start_offset)
        assert end_offset > 0, "The HTML template has no title end tag."

        return content[start_offset:end_offset]

    def update_request(self, request):
        """
        Update the attributes of the specified email address verification
        request that has been successfully processed.


        :param request: An instance containing the following attributes:

            * `request_id` (required): identification of the request.
        """
        with rdbms.RdbmsConnection.acquire_connection(self.rdbms_connection_properties, auto_commit=True) as connection:
            connection.execute(
                """
                UPDATE account_contact_verification
                  SET attempt_count = attempt_count + 1,
                      update_time = current_timestamp,
                      attempt_time = current_timestamp
                  WHERE request_id = %(request_id)s
                """,
                {
                    'request_id': request.request_id
                })
