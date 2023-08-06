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

from majormode.perseus.agent.base import BaseAgent
from majormode.perseus.utils import email_util


class EmailSenderAgent(BaseAgent):
    def __init__(self, smtp_connection_properties):
        """
        Build an agent responsible for sending e-mail to an SMTP server.


        :param smtp_connection_properties: An object `SmtpConnection Properties`.
        """
        self.smtp_connection_properties = smtp_connection_properties

    def send_email(
            self,
            email,
            file_path_names=None,
            unsubscribe_mailto_link=None,
            unsubscribe_url=None):
        """
        Send an email to recipients.


        :param email: An object `Mail` electronic mail to be sent to recipient(s).

        :param file_path_names: A list of complete fully qualified path name
            (FQPN) of the files to attach to this message.

        :param unsubscribe_mailto_link: An email address to directly
            unsubscribe the recipient who requests to be removed from the
            mailing list (https://tools.ietf.org/html/rfc2369.html).

            In addition to the email address, other information can be provided.
            In fact, any standard mail header fields can be added to the mailto
            link.  The most commonly used of these are "subject", "cc", and "body"
            (which is not a true header field, but allows you to specify a short
            content message for the new email). Each field and its value is
            specified as a query term (https://tools.ietf.org/html/rfc6068).

        :param unsubscribe_url: A link that will take the subscriber to a
            landing page to process the unsubscribe request.  This can be a
            subscription center, or the subscriber is removed from the list
            right away and gets sent to a landing page that confirms the
            unsubscribe.
        """
        email_util.send_email(
            self.smtp_connection_properties.hostname,
            self.smtp_connection_properties.username,
            self.smtp_connection_properties.password,
            email.author_name,
            email.author_email_address,
            email.recipient_email_addresses,
            email.subject,
            email.content,
            file_path_names=file_path_names,
            port_number=self.smtp_connection_properties.port_number,
            unsubscribe_mailto_link=unsubscribe_mailto_link,
            unsubscribe_url=unsubscribe_url)
