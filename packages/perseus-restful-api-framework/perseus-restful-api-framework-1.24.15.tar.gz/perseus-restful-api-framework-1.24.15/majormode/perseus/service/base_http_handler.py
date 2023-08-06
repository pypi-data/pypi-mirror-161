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

import datetime
import functools
import inspect
import json
import logging
import re
import socket
import sys
import time
import traceback
import types
import urllib
import urllib.parse
import uuid
import zlib

from majormode.perseus.constant import regex
from majormode.perseus.constant.http import HttpMethod
from majormode.perseus.constant.http import HttpScheme
from majormode.perseus.constant.http import REGEX_PATTERN_USER_AGENT
from majormode.perseus.constant.stage import EnvironmentStage
from majormode.perseus.model import obj
from majormode.perseus.model.app import ClientApplication
from majormode.perseus.model.obj import Object
from majormode.perseus.model.enum import Enum
from majormode.perseus.model.locale import Locale
from majormode.perseus.model.version import Version
from majormode.perseus.service.application.application_service import ApplicationService
from majormode.perseus.service.account.session_service import SessionService
from majormode.perseus.utils import cast
from majormode.perseus.utils import string_util

import settings


class HttpRequestLog:
    """
    Represent logging information about a HTTP request that a client
    application sent to the RESTful API server application.
    """
    def __init__(
            self,
            request,
            response,
            execution_duration,
            dispatch_duration,
            exception=None):
        """
        Build a `HttpRequestLog` instance providing detailed information
        about the processing of a HTTP request that a client application sent
        to the platform.


        :param request: A `HttpRequest` instance.

        :param response: A `HttpResponse` instance.

        :param execution_duration: The time spent in processing the client's
            HTTP request.

        :param dispatch_duration: The time spent in sending the result to the
            client.

        :param exception: A possible exception that the processing of this
            HTTP request may have raised.
        """
        self.log_id = uuid.uuid1().hex
        self.app_id = str(request.app_id) if hasattr(request, 'app_id') else None
        self.api_version = settings.API_VERSION
        self.host_ip_address = socket.gethostbyname(socket.gethostname())
        self.client_ip_address = request.client_ip_address
        self.http_method = str(request.http_method)
        self.uri = request.uri
        self.arguments = request.arguments
        self.headers = request.headers
        self.request_size = 0 if request.body is None else len(request.body)
        self.response_size = len(str(response))
        self.execution_duration = (execution_duration.seconds * 1000) + (execution_duration.microseconds / 1000)
        self.dispatch_duration = (dispatch_duration.seconds * 1000) + (dispatch_duration.microseconds / 1000)
        self.request_time = time.strftime('%Y-%m-%dT%H:%M:%S.000+00', time.gmtime())

        if settings.LOGGING_LEVEL == logging.DEBUG:
            self.request_content = request.body if len(request.uploaded_files) == 0 else '<<files>>',

        if exception is not None:
            self.exception_class = type(exception).__name__
            self.exception_message = str(exception)
            self.exception_traceback = traceback.format_exc()

        self._tag = self.__class__.__name__


class HttpRequest:
    class HttpRequestException(Exception):
        """
        Base class of exception that the HTTP request handler may raise to
        indicate some unexpected conditions.
        """
        def __init__(self, message=None, payload=None):
            """
            Build a new instance of an exception that indicates an unexpected
            condition while handling a client's request.


            :param message: A humanly-readable message that describes this
                exception instance.

            :param payload: A JSON expression that provides detailed information
                about this exception instance.
            """
            super().__init__(message)
            self.payload = payload

    class DeprecatedApiException(HttpRequestException):
        """
        Signal that the client application has specified a deprecated version
        of the RESTful API while the Python handler of the given HTTP request
        requires a compatible version (cf. parameter `compatibility_required`
        of the decorator `@http_request `).
        """

    class InvalidArgumentException(HttpRequestException):
        """
        Signal that the client application has passed an argument of the wrong
        type or of the wrong value, within the HTTP request to process, as the
        HTTP handler requests (cf. parameter `data_type` of arguments accepted
        by the corresponding HTTP handler).
        """

    class InvalidMessageBodyException(HttpRequestException):
        """
        Indicate that the message body of the HTTP request is not a valid JSON
        expression.
        """

    class MissingArgumentException(HttpRequestException):
        """
        Signal that the application hasn't passed a required argument with the
        HTTP request to process.
        """

    class MissingHeaderException(HttpRequestException):
        """
        Signal that the application hasn't provided a HTTP header required by
        the HTTP request processor.
        """

    class HttpRequestUploadedFile:
        """
        Represent a file that has been uploaded.
        """
        def __init__(self, field_name, file_name, content_type, data):
            """
            Build a new instance of this class.


            :param field_name: Original field name in the form that has been sent
                to the platform to upload a file (cf. multipart MIME data
                stream "multipart/form-data").

            :param file_name: Name of the file as defined in the HTTP request that
                the client application sent to the platform.

            :param content_type: Specify the nature of the data in the content of
                the file that has been uploaded to the platform entity, by
                giving type and subtype identifiers, and by providing auxiliary
                information that may be required for certain types.

            :param data: Content of the file that has been uploaded.
            """
            self._field_name = field_name
            self._file_name = file_name
            self._content_type = content_type
            self._data = data

        @property
        def data(self):
            return self._data

        @property
        def content_type(self):
            return self._content_type

        @property
        def field_name(self):
            return self._field_name

        @property
        def file_name(self):
            return self._file_name

    class ArgumentObject:
        """

        """
        @staticmethod
        def _get_argument(
                payload,
                argument_name,
                data_type=None,
                default_value=None,
                enumeration=None,
                is_required=True,
                item_data_type=None,
                object_class=None):
            """
            Return the value of an argument contained in the JSON expression


            :param payload: A JSON expression.

            :param argument_name: Name of the argument to return the value.

            :param default_value: default value to return if the argument was
                optional and not defined within the HTTP request.

            :param enumeration: An enumeration inheriting from `Enum`, when the
                argument `data_type` is `ArgumentDataType.enumeration`.

            :param is_required: Indicate whether this argument is mandatory, i.e.
                it MUST be provided in the HTTP request, and if not provided, the
                function will raise the exception `MissingArgumentException`.

            :param item_data_type: When the argument to return the value is of
                data type `ArgumentType.list`, the caller can specify the data
                type of the items that this list contains.

            :param object_class: Python class to be used to instantiate a new
                object from the JSON value of the given argument when the
                specified data type of this argument is `object`.  This Python
                class MUST implement a static method `from json` that returns an
                instance of this class providing a JSON expression.


            :return: The casted value of the argument.


            :raise MissingArgumentException: If the JSON expression doesn't
                contain the specified argument while this argument is required.
            """
            if not isinstance(payload, dict):
                raise ValueError("The argument 'payload' MUST be a dictionary")

            if is_required and argument_name not in payload:
                raise HttpRequest.MissingArgumentException(f'Required argument "{argument_name}" is not passed')

            argument_value = payload.get(argument_name) or default_value

            casted_argument_value = HttpRequest.cast_value(
                argument_name,
                argument_value,
                argument_passing=HttpRequest.ArgumentPassing.message_body,
                data_type=data_type or HttpRequest.ArgumentDataType.string,
                enumeration=enumeration,
                item_data_type=item_data_type or HttpRequest.ArgumentDataType.string,
                object_class=object_class)

            return casted_argument_value

        @staticmethod
        def from_json(payload):
            """
            Build an object with a JSON expression


            :param payload: A JSON expression.


            :return: An object built from the JSON expression
            """
            raise NotImplementedError()

    ArgumentDataType = Enum(
        'boolean',
        'date',
        'decimal',
        'dictionary',
        'email_address',
        'enumeration',
        'hexadecimal',
        'integer',
        'ipv4',
        'list',
        'locale',  # RFC 4646
        'macaddr',
        'natural_number',  # Positive integers including zero
        'object',
        'regex',
        'string',
        'time',
        'timestamp',
        'uri',
        'uuid',
        'version'
    )

    ArgumentPassing = Enum(
        'query_string',
        'message_body'
    )

    # Regular expression that matches a valid User-Agent HTTP header.
    REGEX_USER_AGENT = re.compile(REGEX_PATTERN_USER_AGENT)

    def __init__(
            self,
            http_method,
            uri,
            arguments,
            headers,
            remote_ip,
            body=None,
            uploaded_files=None):
        """
        Build an instance `HttpRequest` representing the HTTP request that a
        client application sent to the platform.


        :note: The method `_prepare_` MUST be called to complete the
            instantiation of this object.


        :param http_method: An instance `HttpMethod` that indicates the HTTP
            method of this request.

        :param uri: Uniform Resource Identifier that names a resource of the
            platform the HTTP request requires to gain access to.

        :param arguments: A dictionary of key/value pairs representing the
            arguments passed in the query string of the HTTP request.

        :param headers: A dictionary of key/value pairs representing the
            headers of the HTTP request.

        :param remote_ip: The Internet Protocol address of the client
            application that initiates this HTTP request.

        :param body: Content of the message body of the HTTP request when the
            HTTP method is `POST` or `PUT`.

        :param uploaded_files: A list of instances `HttpRequestUploadedFile`
            mapping the files that the client application has uploaded to
            the platform along the HTTP request.
        """
        if http_method not in HttpMethod:
            raise Exception(f'Unsupported HTTP method {http_method}')

        self.http_method = http_method
        self.uri = uri
        self.arguments = arguments
        self.headers = headers
        self.uploaded_files = uploaded_files or []

        # Retrieve the IP address of the client application that sent this HTTP
        # request.
        x_forwarded_for = headers.get('X-Forwarded-For')
        self.client_ip_address = cast.string_to_ipv4(
            x_forwarded_for.split(',')[0] if x_forwarded_for else headers.get('X-Real-Ip', remote_ip))

        self.request_time = time.strftime('%Y-%m-%dT%H:%M:%S.000+00', time.gmtime())

        # Check whether the client application sends compressed request using
        # "gzip" method.
        #
        # To decompress gzipped data with zlib, the windowBits parameter must
        # be 16 + MAX_WBITS (cf. function `deflateInit2`;
        # http://www.zlib.net/manual.html]::
        #
        #   windowBits can also be greater than 15 for optional gzip encoding.
        #   Add 16 to windowBits to write a simple gzip header and trailer
        #   around the compressed data instead of a zlib wrapper."
        #
        # Note: other technique but somewhat slower:
        #
        #    import StringIO
        #    file_object = StringIO.StringIO(self.request.body)
        #    gzipper = gzip.GzipFile(fileobj=file_object)
        #    data = gzipper.read()gzip
        #
        #
        # @note: We keep the body message even for HTTP method other than POST
        #     and PUT.  There are HTTP requests with method GET that need to
        #     pass sensitive data to check a resource's status (e.g., password
        #     reset request, providing a nonce).  HTTP request's query string
        #     is not encrypted, and therefore passing sensitive data in the
        #     query would allow man-in-the-middle (MITM) attack.
        self.raw_body = None if body is None or len(body) == 0 \
            else zlib.decompress(body, 16 + zlib.MAX_WBITS) if headers.get('Content-Encoding') == 'gzip' \
            else body

        content_type = self.headers.get('Content-Type')
        if content_type:
            content_type_parts = [part.strip() for part in content_type.split(';')]
            media_type, encoding = content_type_parts if len(content_type_parts) == 2 else (content_type_parts[0], None)

        self.body = None if self.raw_body is None \
            else json.loads(self.raw_body) if content_type and media_type == 'application/json' \
            else self.raw_body

    # def _prepare(self):
    #     """
    #     Complete the instantiation of the HTTP request object.  This method
    #     MUST be called once the `HttpRequest` instance has been built.
    #
    #     This function is responsible for uncompressing gzip content of the
    #     HTTP request message body when the HTTP method is `PUT` or `POST`
    #     and the content encoding has been indicated as of `gzip`.
    #
    #     This function is responsible for converting the string content (cf.
    #     member `body`) of the HTTP request's message body into a JSON object
    #     when the content type has been indicated as of `application/json`.
    #
    #     :raise Exception: if decompression issue occurs or if JSON string
    #            representation is not conform to the JSON specification.
    #     """
    #     # Check whether the client application sends compressed request using
    #     # "gzip" method.
    #     #
    #     # To decompress gzipped data with zlib, the windowBits parameter must
    #     # be 16 + MAX_WBITS (cf. function `deflateInit2`;
    #     # http://www.zlib.net/manual.html]::
    #     #
    #     #   windowBits can also be greater than 15 for optional gzip encoding.
    #     #   Add 16 to windowBits to write a simple gzip header and trailer
    #     #   around the compressed data instead of a zlib wrapper."
    #     #
    #     # Note: other technique but somewhat slower:
    #     #
    #     #    import StringIO
    #     #    file_object = StringIO.StringIO(self.request.body)
    #     #    gzipper = gzip.GzipFile(fileobj=file_object)
    #     #    data = gzipper.read()gzip
    #     self.body = None if self.body is None or len(self.body) == 0 \
    #         else zlib.decompress(self.body, 16 + zlib.MAX_WBITS) if self.headers.get('Content-Encoding') == 'gzip' \
    #         else self.body
    #
    #     if self.body is not None and self.headers.get('Content-Type') == 'application/json':
    #         self.body = json.loads(self.body)
    #
    #     return self

    @staticmethod
    def cast_value(
            argument_name,
            argument_value,
            argument_passing,
            data_type=ArgumentDataType.string,
            enumeration=None,
            item_data_type=ArgumentDataType.string,
            object_class=None):
        """
        Convert a string to the specified data type.


        :param argument_name: The name of the argument which value is casted.
            This parameter is only required for debugging purpose.

        :param argument_value: The string to be converted to the specified
            data type.

        :param argument_passing: An item of `HttpRequest.ArgumentPassing`
            that indicates whether the argument value has been passed within
            the query parameters of the request or in the message body.  This
            parameter is only used to parse list of values.

        :param data_type: An item of `HttpRequest.ArgumentDataType` that
            indicates the data type to cast the string to.

        :param enumeration: A Python class inheriting from `Enum` which
            the string MUST be an item of, when the argument `data_type` is
            `ArgumentDataType.string`.

        :param object_class: A Python class to instantiate a new object from
            the JSON string representation, when the argument `data_type` is
            `object`.  This Python class MUST implement a static method
            `from_json` that returns an instance of this class providing a
            JSON expression.

            If this argument is not defined, while the argument `data_type` is
            `object`, the function uses the class `Object` to instantiate a
            new object from the JSON string representation

        :param item_data_type: An item of `ArgumentDataType` that specifies
            the data type to cast each item of the list passed as argument,
            when `data_type` is `ArgumentDataType.list`.


        :return: The value converted from the string with the specified data
            type.


        :raise InvalidArgumentException: If `data_type` is
            `ArgumentDataType.enumeration` but the argument `enumeration` has
            not be passed to this function.

        :raise ValueError: If `argument_value` is not a valid string
            representation of the type specified in `data_type`.
        """
        if data_type == HttpRequest.ArgumentDataType.boolean:
            return cast.string_to_boolean(argument_value, strict=True)

        if data_type == HttpRequest.ArgumentDataType.date:
            return cast.string_to_date(argument_value)

        if data_type == HttpRequest.ArgumentDataType.decimal:
            return float(argument_value)

        if data_type == HttpRequest.ArgumentDataType.email_address:
            if not string_util.is_email_address(argument_value):
                raise ValueError(f"Invalid email address '{argument_value}'")
            return argument_value

        if data_type == HttpRequest.ArgumentDataType.enumeration:
            if enumeration is None:
                raise HttpRequest.InvalidArgumentException(f'Unspecified Python enumeration for parameter "{argument_name}"')
            return cast.string_to_enum(argument_value, enumeration)

        if data_type == HttpRequest.ArgumentDataType.integer:
            return cast.string_to_integer(argument_value, strict=False)

        if data_type == HttpRequest.ArgumentDataType.natural_number:
            return cast.string_to_natural_number(argument_value, strict=False)

        if data_type == HttpRequest.ArgumentDataType.ipv4:
            return cast.string_to_ipv4(argument_value, strict=False)

        if data_type == HttpRequest.ArgumentDataType.list:
            element_values = argument_value if argument_passing == HttpRequest.ArgumentPassing.message_body \
                else json.loads(argument_value) if item_data_type == HttpRequest.ArgumentDataType.object \
                else [
                    urllib.parse.unquote(element.strip())
                    for element in argument_value.split(',')
                    if len(element) > 0]

            # Convert each element of the list to the require data type.
            casted_elements = [
                HttpRequest.cast_value(
                    f'{argument_name}.element',  # Debugging purpose only
                    element_value,
                    argument_passing,  # Same argument passing
                    data_type=item_data_type,
                    enumeration=enumeration,
                    object_class=object_class)
                for element_value in element_values
            ]

            return casted_elements

        if data_type == HttpRequest.ArgumentDataType.locale:
            return cast.string_to_locale(argument_value, strict=False)

        if data_type == HttpRequest.ArgumentDataType.macaddr:
            return cast.string_to_macaddr(argument_value)

        if data_type == HttpRequest.ArgumentDataType.object:
            return (object_class or obj.Object).from_json(argument_value)

        if data_type == HttpRequest.ArgumentDataType.time:
            return cast.string_to_time(argument_value)

        if data_type == HttpRequest.ArgumentDataType.timestamp:
            return cast.string_to_timestamp(argument_value)

        if data_type == HttpRequest.ArgumentDataType.uuid:
            return cast.string_to_uuid(argument_value)

        if data_type == HttpRequest.ArgumentDataType.version:
            return Version(argument_value)

        return argument_value

    def get_argument(
            self,
            name,
            argument_passing=None,
            data_type=ArgumentDataType.string,
            default_value=None,
            enumeration=None,
            is_required=True,
            item_data_type=ArgumentDataType.string,
            object_class=None):
        """
        Return the value of the HTTP request argument specified by its name.


        :param name: name of the argument to return its value.

        :param argument_passing: An item of `ArgumentPassing` that indicates
            how this argument is passed with the HTTP request, within the
            query string or the message body.  The default argument passing
            depends on the HTTP method of the request:

            * `DELETE`: query string

            * `GET`: query string

            * `POST`: message body

            * `PUT`: message body

            When the value of the argument is passed in the message body, the
            function expects the message body to be a JSON dictionary, and the
            argument's name to be a root key of this dictionary.

        :param data_type: data type of the value of this argument as one
            defined in the enumeration `HttpRequest.ArgumentDataType`.  The
            function might performs some check to ensure that the value of this
            argument corresponds to the specified data type.

        :param default_value: default value to return if the argument was
            optional and not defined within the HTTP request.

        :param enumeration: An enumeration inheriting from `Enum`, when the
            argument `data_type` is `ArgumentDataType.enumeration`.

        :param is_required: Indicate whether this argument is mandatory, i.e.
            it MUST be provided in the HTTP request, and if not provided, the
            function will raise the exception `MissingArgumentException`.

        :param item_data_type: When the argument to return the value is of
            data type `ArgumentType.list`, the caller can specify the data
            type of the items that this list contains.

        :param object_class: Python class to be used to instantiate a new
            object from the JSON value of the given argument when the
            specified data type of this argument is `object`.  This Python
            class MUST implement a static method `from json` that returns an
            instance of this class providing a JSON expression.


        :return: the value of the specified argument as passed with the HTTP
            request.


        :raise InvalidMessageBodyException: if the HTTP method is `POST` or
            `PUT`, but the message body of this request is either empty or it
            is not a valid JSON expression.

        :raise MissingArgumentException: if no argument corresponds to the
            specified name while this argument is required.
        """
        # Determine the argument passing when not specified, depending on the
        # HTTP method.
        if argument_passing is None:
            # Check whether the client application requests the RESTful API server
            # to override the method specified in the request by whether passing the
            # HTTP header `X-HTTP-Method-Override`, whether passing the argument
            # `_method` (a convention becoming increasingly common in other
            # frameworks).
            overriding_http_method = self.get_header(
                'X-HTTP-Method-Override',
                data_type=HttpRequest.ArgumentDataType.enumeration,
                enumeration=HttpMethod,
                is_required=False) \
                    or cast.string_to_enum(
                        self.arguments.get('_method'),
                        HttpMethod,
                        strict=False)

            argument_passing = HttpRequest.ArgumentPassing.message_body \
                if overriding_http_method or self.http_method in (HttpMethod.POST, HttpMethod.PUT) \
                else HttpRequest.ArgumentPassing.query_string

        # Retrieve the value of the argument from either the query string or
        # the message body, depending on the argument passing.
        is_argument_defined = False

        if argument_passing == HttpRequest.ArgumentPassing.query_string:
            if name in self.arguments:
                is_argument_defined = True
                value = self.arguments.get(name)

                # Strings may be UTF-8 encoded bytes escaped with URL quoting.
                if value and data_type == self.ArgumentDataType.string:
                    value = urllib.parse.unquote(value)

        elif self.body:
            if not isinstance(self.body, dict):
                raise HttpRequest.InvalidMessageBodyException()

            is_argument_defined = name in self.body
            if is_argument_defined:
                value = self.body.get(name)

        # Check whether this argument is required while the client application
        # didn't pass this argument with the HTTP request.
        if is_required and not is_argument_defined:
            get_logger().debug(f'Required argument "{name} is not passed')
            raise HttpRequest.MissingArgumentException(f'Required argument "{name}" is not passed')

        # Use the default value is the client application didn't pass the
        # argument in the HTTP request, of if the value of this argument is
        # null.
        return default_value if not is_argument_defined or value is None else \
            HttpRequest.cast_value(
                name,
                value,
                argument_passing,
                data_type=data_type,
                item_data_type=item_data_type,
                object_class=object_class,
                enumeration=enumeration)

    def get_header(
            self,
            field_name,
            data_type=ArgumentDataType.string,
            default_value=None,
            enumeration=None,
            is_required=True,
            item_data_type=ArgumentDataType.string):
        """
        Return the field value of the HTTP header specified by its field name.

        :param field_name: name of the HTTP header's field.

        :param data_type: data type of the value of this argument as one
           defined in the enumeration `HttpRequest.ArgumentDataType`.  The
           function performs some checks to ensure that the value of this
           argument corresponds to the specified data type.

        :param default_value: default value to return if the header was
           optional and not defined within the HTTP request.

        :param enumeration: An enumeration inheriting from `Enum`, when the
            argument `data_type` is `ArgumentDataType.enumeration`.

        :param is_required: Indicate whether this header is mandatory, i.e.
            it MUST be provided in the HTTP request, and if not provided, the
            function will raise the exception `MissingHeaderException`.

        :param item_data_type: When the header to return the value is of
            data type `ArgumentType.list`, the caller can specify the data
            type of the items that this list contains.


        :return: the value of the HTTP header's field.


        :raise MissingHeaderException: the specified field name doesn't
               correspond to any HTTP header defined in this request.
        """
        if field_name not in self.headers:
            if is_required:
                get_logger().debug(f'Required HTTP header "{field_name}"" is not passed')
                raise HttpRequest.MissingHeaderException(f'Required HTTP header "{field_name}" is not passed')
            else:
                return default_value

        return HttpRequest.cast_value(
            field_name,
            self.headers[field_name],
            None,
            data_type=data_type,
            enumeration=enumeration,
            item_data_type=item_data_type)


class HttpMethodSpec:
    """
    Specification of a HTTP method that handles a Uniform Resource
    Identifier (URI) pattern for a given HTTP method (alias an endpoint).
    """
    class HttpMethodSpecException(Exception):
        """
        Signal a bad declaration of the handler of a Uniform Resource
        Identifier endpoint.
        """

    class AlreadyDeclaredURLBitException(HttpMethodSpecException):
        """
        Signal that a URL bit has been declared more than one time in the the
        Uniform Resource Identifier (URI) pattern of a HTTP method handler.
        """
        def __init__(
                self,
                parameter_name,
                uri_pattern,
                handler_module_name,
                handler_class_name,
                handler_method):
            super().__init__(
                f'URL bit "{parameter_name}" declared twice in the endpoint URL "{uri_pattern}" '
                f'({handler_module_name}.{handler_class_name}.{handler_method.__name__})')

    class UnsupportedURLBitDataTypeException(HttpMethodSpecException):
        """
        Signal that an URL bit, declared in the Uniform Resource Identifier
        (URI) pattern of a RESTful API endpoint, is defined with an
        unsupported data type.
        """
        def __init__(
                self,
                parameter_name,
                parameter_type,
                uri_pattern,
                handler_module_name,
                handler_class_name,
                handler_method):
            super().__init__(
                f'Unknown or unsupported data type "{parameter_type}" of the URL bit "{parameter_name}" '
                f'declared in the endpoint URL "{uri_pattern}" '
                f'({handler_module_name}.{handler_class_name}.{handler_method.__name__})')

    # Regular expression that matches an in-line parameter (alias URL bit)
    # defined in a Uniform Resource Identifier (URI) of a RESTful API
    # endpoint.
    #
    # An URL bit is defined of a name and a possible data type, separated
    # by a colon character ":", the whole expression between parentheses.
    #
    # For examples:
    #
    # * (username)
    # * (age:int)
    # * (account_id:uuid)
    REGEX_URL_BIT_PARAMETER = re.compile(r'\(([a-z_]+)(:([a-z_]+)){0,1}\)')

    # Regular expression patterns that matches different parameter types.
    PARAMETER_TYPE_REGEX_PATTERNS = {
        HttpRequest.ArgumentDataType.integer: regex.REGEX_PATTERN_INTEGER,
        HttpRequest.ArgumentDataType.ipv4: regex.REGEX_PATTERN_IPV4,
        HttpRequest.ArgumentDataType.list: r'(([^/,]+,)*|[^/,]+)+',
        HttpRequest.ArgumentDataType.natural_number: regex.REGEX_PATTERN_NATURAL_NUMBER,
        HttpRequest.ArgumentDataType.string: r'[^/]+',
        HttpRequest.ArgumentDataType.uuid: regex.REGEX_PATTERN_UUID,
    }

    def __init__(
            self,
            http_method,
            uri_pattern,
            handler_module_name,
            handler_class_name,
            handler_method):
        """
        Build a new instance of `HttpMethodSpec`.


        :param http_method: One of the supported HTTP 1.1 common methods as
           defined in the enumeration `HttpMethod` of the class `HttpRequest`:

           * `HttpMethod.DELETE`

           * `HttpMethod.GET`

           * `HttpMethod.POST`

           * `HttpMethod.PUT`


        :param uri_pattern: Uniform Resource Identifier (URI) pattern (i.e.,
            a regular expression) that the wrapped method is responsible to
            handle.

        :param handler_module_name: Name of the Python module that contains
            the code of the HTTP request handler.

        :param handler_class_name: Name of the Python class that implements
            the HTTP request handler.

        :param handler_method: The Python function that handles the URI
            pattern.  This function MUST be a method of a class inheriting
            from `HttpRequestHandler`; because, at the time a function is
            defined, it is just a plain function, i.e., it is not bound to any
            class, therefore this requirement cannot be programmatically
            checked.


        :raise AlreadyDeclaredURLBitException: if an URL bit is declared more
            than one time in the specified Uniform Resource Identifier (URI)
            pattern.

        :raise AssertError: If the argument `http_method` is not an item of
            the enumeration `HttpMethod`.

        :raise UnsupportedURLBitDataTypeException: If an in-line parameter
            (i.e., URL bits), declared in the Uniform Resource Identifier (URI)
            pattern, has a data type that is not supported.
        """
        assert http_method in HttpMethod, 'Invalid HTTP method specified'

        self.http_method = http_method

        # Rewrite the specified URI of the RESTful API endpoint to a regular
        # expression where the data type of each declared URL bit has been
        # converted to a matching regular expression.
        self.uri_pattern, self.url_bits = self._rewrite_uri_pattern_with_regex(
            uri_pattern,
            handler_module_name,
            handler_class_name,
            handler_method)

        self.uri_pattern_regex = re.compile(self.uri_pattern)

        self.handler_module_name = handler_module_name
        self.handler_class_name = handler_class_name
        self.handler_method = handler_method

        self.handler_module = None  # Lazy evaluation
        self.handler_class = None  # Lazy evaluation

    @classmethod
    def _rewrite_uri_pattern_with_regex(
            cls,
            uri_pattern,
            handler_module_name,
            handler_class_name,
            handler_method):
        """
        Rewrite the Uniform Resource Identifier (URI) pattern of a RESTful API
        endpoint, where the declared type of each URL bit has been converted
        to the matching regular expression.


        :param uri_pattern: Uniform Resource Identifier (URI) pattern (i.e.,
            a regular expression) that the wrapped method is responsible to
            handle.

        :param handler_module_name: Name of the Python module that contains
            the code of the HTTP request handler.

        :param handler_class_name: Name of the Python class that implements
            the HTTP request handler.

        :param handler_method: The Python function that handles the URI
            pattern.  This function MUST be a method of a class inheriting
            from `HttpRequestHandler`; because, at the time a function is
            defined, it is just a plain function, i.e., it is not bound to any
            class, therefore this requirement cannot be programmatically
            checked.


        :return: the URI pattern with URL bits declared as named groups with
            their respective data type converted to regular expressions, and a
            dictionary of the URL bits and their respective data type (item of
            `HttpRequest.ArgumentDataType`).
        """
        # Retrieve each in-line parameters (i.e., URL bits), and store their
        # type into a dictionary.  Then rewrite the specified URI pattern with
        # named group and the regular expression corresponding to each parameter
        # type.
        url_bits = dict()

        uri_pattern_with_url_bit_named_groups = []
        end_index = 0

        for match in cls.REGEX_URL_BIT_PARAMETER.finditer(uri_pattern):
            parameter_name, _, parameter_type_str = match.groups()

            # Convert the string representation of the parameter data type to an
            # item of the enumeration `ArgumentDataType`.
            try:
                parameter_type = cast.string_to_enum(
                        parameter_type_str,
                        HttpRequest.ArgumentDataType,
                        default_value=HttpRequest.ArgumentDataType.string,
                        strict=False)

            except ValueError:  # Not an item of `HttpRequest.ArgumentDataType`
                exception = cls.UnsupportedURLBitDataTypeException(
                    parameter_name,
                    parameter_type_str,
                    uri_pattern,
                    handler_module_name,
                    handler_class_name,
                    handler_method)

                get_logger().debug(str(exception))
                raise exception

            # Check whether the specified parameter type is supported for URL bit
            # parameter.
            if parameter_type not in cls.PARAMETER_TYPE_REGEX_PATTERNS:
                exception = cls.UnsupportedURLBitDataTypeException(
                    parameter_name,
                    parameter_type_str,
                    uri_pattern,
                    handler_module_name,
                    handler_class_name,
                    handler_method)

                get_logger().debug(str(exception))
                raise exception

            # Check whether this URL bit parameter has been already declared, and
            # if not, store its declaration.
            if parameter_name in url_bits:
                raise cls.AlreadyDeclaredURLBitException(
                    parameter_name,
                    uri_pattern,
                    handler_module_name,
                    handler_class_name,
                    handler_method)

            url_bits[parameter_name] = parameter_type

            # Add the part of the Uniform Resource Identifier (URI) pattern between
            # the previous and the current URL bit declarations.
            start_index = match.start(0)
            uri_pattern_with_url_bit_named_groups.append(uri_pattern[end_index:start_index])

            # Add the current URL bit in the form of a regular expression named
            # group.
            parameter_type_regex = cls.PARAMETER_TYPE_REGEX_PATTERNS[parameter_type]
            uri_pattern_with_url_bit_named_groups.append(f'(?P<{parameter_name}>{parameter_type_regex})')

            end_index = match.end(0)

        # Add the last part of the Uniform Resource Identifier (URI) pattern
        # remaining after the last URL bit declaration.
        uri_pattern_with_url_bit_named_groups.append(uri_pattern[end_index:])

        return ''.join(uri_pattern_with_url_bit_named_groups), url_bits

    def __eq__(self, other):
        """
        Indicate whether this instance is equivalent to another.


        :param other: Another instance of the class `HttpMethodSpec`.


        :return: `True` if the two instances are equivalent; `False` otherwise.
        """
        return isinstance(other, HttpMethodSpec) and \
            self.http_method == other.http_method and \
            self.uri_pattern == other.uri_pattern

    def __hash__(self):
        """
        Return the hash value of the HTTP endpoint method.


        :return: An integer corresponding to the hash value of the HTTP
            endpoint method.
        """
        return hash((self.http_method, self.uri_pattern))

    def process(self, request):
        """
        Call the handler of a Uniform Resource Identifier (URI) endpoint
        providing a HTTP request sent by a client application


        :param request: An instance of `HttpRequest`.


        :return: The result returned by the handler that processed this
            request.
        """
        # Load the Python module of the handler if not already done.
        if self.handler_module is None:
            self.handler_module = sys.modules[self.handler_module_name]
            self.handler_class = getattr(self.handler_module, self.handler_class_name)

        # Build a new instance of the handler's class and access the Python
        # method of this handler.
        handler_class_instance = self.handler_class()
        handler_method = getattr(handler_class_instance, self.handler_method.__name__)

        # Retrieve the path and the query string of the URI endpoint.
        request_path = urllib.parse.urlsplit(request.uri)[2]

        # Build the Python keyworded arguments to pass to the handler's method,
        # if any URL bits declared in the URI endpoint.
        kwargs = {} if len(self.url_bits) == 0 else \
            dict([
                (
                    name,
                    HttpRequest.cast_value(name, value, None, data_type=self.url_bits[name])
                )
                for name, value in self.uri_pattern_regex.match(request_path).groupdict().items()
            ])

        # Execute the handler method passing:
        #
        # * the instance of the handler class as `self`.
        # * the instance `request` as the first always required argument
        # * the keyworded arguments corresponding to URL bit values.
        request._execution_start_time = datetime.datetime.now()
        response = HttpResponse(handler_method(request, **kwargs))
        request._execution_end_time = datetime.datetime.now()

        return response


class HttpRequestHandler:
    """
    Base class of the HTTP request handler that each RESTful API class
    MUST inherit from.
    """
    # Class member that contains all the `HttpMethodSpec` instances that
    # the RESTful API application has successfully loaded.
    #
    # The key corresponds to the hash of `HttpMethodSpec` instance while
    # the value corresponds to the instance itself.  The key is mostly used
    # by the code responsible for adding declared RESTful methods from
    # Python modules, and making sure that two or more methods are declared
    # for the same endpoint (HTTP method and URI(.
    handlers = dict()


class HttpResponse:
    """
    Represent the response to a HTTP request that has been processed by
    the method of RESTful API service.

    It embeds an object that is serialized to a JSON form to be returned
    to the client application that sent the HTTP request.
    """
    class HttpResponseException:
        """
        Base class of exception that the processor of HTTP request raises when
        an exceptional condition occurred while processing this HTTP request.
        """
        def __init__(self, exception):
            """
            Build a new instance `HttpResponseException` providing the inner
            exception raised by the handler method of a RESTful API service that
            processed the HTTP request.


            :param exception: The inner exception raised by the handler method of
                a RESTful API service that processed the HTTP request.
            """
            self.error = exception.__class__.__name__
            self.message = str(exception)
            self.payload = getattr(exception, 'payload', None)

    def __init__(self, result=None):
        """
        Build a new instance `HttpResponse` corresponding to the result of a
        HTTP request returned by the RESTful API service method that has
        processed this request.


        :param result: result returned by the RESTful API service method that
            has processed a HTTP request.
        """
        # Convert the result to an empty dictionary if the result is null, or
        # a dictionary with a unique entry `data` if the result is not a
        # Python built-in collections, nor an object having `__dict__` attribute.
        self._result = dict() if result is None \
            else result if (isinstance(result, (list, set, tuple)) or hasattr(result, '__dict__')) \
            else dict(data=result)

    def __str__(self):
        """
        Return a string representation of the JSON expression of the result
        returned by the RESTful API service method that has processed a HTTP
        request.


        :return: A string representation of the JSON expression of the result.
        """
        return json.dumps(obj.stringify(self._result, trimmable=True))

    @staticmethod
    def from_exception(exception):
        """
        Build a HTTP response from an exception that occurred while processing
        a HTTP request.


        :param exception: An exception raised by the RESTful API service
            method that has processed a HTTP request that failed.


        :return: An instance `HttpResponse` that embeds an instance
            `HttpResponseException` built with the inner exception raised by
            the RESTful API service method that has processed a HTTP request.
        """
        return HttpResponse(HttpResponse.HttpResponseException(exception))

    @property
    def result(self):
        return self._result


def get_logger():
    """
    Return the logger specified in the settings of the RESTful API
    application's settings.


    :return: an instance `Logger`.
    """
    return logging.getLogger(getattr(settings, 'LOGGER_NAME'))


def http_request(
        uri_pattern,
        http_method=HttpMethod.GET,
        authentication_required=False,
        compatibility_required=False,
        json_data=True,
        sensitive_data=False,
        signature_required=True):
    """
    Decorator used to declare a method of HTTP request handler responsible
    for processing a Uniform Resource Identifier (URI) endpoint defined
    with a specific HTTP method (e.g., `GET`).

    This decoration extends the behavior of the wrapped method, both at
    compile time and run time:

    * At compile time, this decorator registers the wrapped method as the
      handler for the specified Uniform Resource Identifier (URI) pattern
      corresponding to a regular expression and a HTTP method such as
      `GET`, `POST`, `PUT`, and `DELETE`.  It checks that no other
      URI pattern has been register for the specified HTTP method.

    * At run time, this decorator performs around processing of the HTTP
    request for which the wrapped method is invoked.  For instance:

      * Ensure that the HTTP request has been correctly signed (cf.
        argument `signature_enabled`)

      * Ensure that the HTTP request transports the identification of the
        session of a user on behalf of the wrapped method is called (cf.
        argument `authentication_required`)

      * Check that the client application is compatible with the version
        of the server platform's API this client application is
        communicating with.


    :param uri_pattern: Uniform Resource Identifier (URI) pattern,
        corresponding to a regular expression, the wrapped method is
        responsible to handle.

    :param http_method: An item of the enumeration `HttpMethod`.  The
        selected HTTP method indicates the desired action to be performed
        on the resource identified by the URI.  What this resource
        represents depends on the implementation of the method wrapped.

    :param authentication_required: Indicate whether the wrapped method
        requires the user, on behalf of whom the HTTP request is sent, to
        be authenticated or not.  If `True`, the client application MUST
        provide the HTTP header field `X-Authentication`, passing the
        identification of the login session of this user.

    :param compatibility_required: Indicate whether the wrapped method
        requires the client application to be strictly compatible with
        the version of the RESTful API application's.  If `True`, the
        client application MUST provide the HTTP header field
        `X-API-Version` which value MUST comply with a version number
        using a standard tuple of integers: `major.minor.patch`.

    :param json_data: Indicate whether the message body of HTTP methods
        such as `POST` and `PUT` MUST be a string representation of a
        JSON expression.

    :param sensitive_data: Indicate whether sensitive data could be
        transmitted back and forth among the HTTP request or its response
        between the client application and the RESTful API application.

        Sensitive data correspond to a class of data, including personal,
        financial, legal information, which should be carefully handled,
        such as, for instance:

        * user account password
        * Personal Identification Number (PIN)
        * Social Security number (SSN)
        * credit card number or banking information
        * passport number
        * tax information
        * credit reports

        If `True`, the RESTful API application framework doesn't trace
        any data that are transmitted by the client application or
        returned by the RESTful API application, for environment stages
        other than development, integration, and test.

    :param signature_required: indicate whether the wrapped method
        requires the HTTP request to be signed with the Secret Key tied
        with the Consumer Key of the client application that sent this
        request.  If `True`, the client application MUST provide the
        HTTP header fields `X-API-Key` and `X-API-Sig`.


    :return: A function that decorates the given method.


    :raise Exception: If some unexpected conditions occurred while
        decorating the HTTP request handler, such as the URI pattern has
        been already registered with another method, or some options
        passed to this decorator have incoherent values, etc.
    """
    # Check that the method decorated is bounded to a class that inherits
    # from `HttpRequestHandler`.
    #
    # @note: it does seem possible to get the class of the method that is
    # decorated such as:
    #
    #     class_name = inspect.getouterframes(inspect.currentframe())[1][3]
    #     current_module = sys.modules[globals()['__name__']]
    #     _class_ = getattr(current_module, class_name)
    #     if not issubclass(_class_, HttpRequestHandler):
    #        raise Exception('The decorator %s MUST be used for a method of an instance of %s' %\
    #            (inspect.getframeinfo(inspect.currentframe()).function, HttpRequestHandler.__name__))
    #
    # When the decorator is evaluated, the class of the method is not
    # yet defined.
    #
    #     class MyHttpRequestHandler(HttpRequestHandler):
    #         @http_request_handler(uri='^foo$')
    #         def foo(self):
    #             pass
    #
    # meaning that the code:
    #
    #      _class_ = getattr(current_module, class_name)
    #
    # will raise an error as the specified class is not yet bounded to the
    # module.

    # Determine the name of the class of the method that is decorated, which
    # is a bit tricky as a function only becomes a method at runtime.  At
    # the time a function is defined, it is just a plain function, it is not
    # bound to any class.  However, when the decorator is called, even
    # though the function is not yet bound to the class, it is possible to
    # inspect the stack and discover the string name of the class that is
    # calling the decorator.
    class_name = inspect.getouterframes(inspect.currentframe())[1][3]

    def wrapper(method):
        http_method_spec = HttpMethodSpec(http_method, uri_pattern, method.__module__, class_name, method)

        # Check that the specified HTTP method for the given Uniform Resource
        # Identifier (URI) has not been defined for another HTTP request handler.
        existing_http_method_spec = HttpRequestHandler.handlers.get(hash(http_method_spec))
        if existing_http_method_spec:
            logger = get_logger()
            logger.error(f'Multiple handler declarations for endpoint "{http_method} {uri_pattern}":')
            logger.error('- Existing endpoint: {}.{}.{}'.format(
                existing_http_method_spec.handler_module_name,
                existing_http_method_spec.handler_class_name,
                existing_http_method_spec.handler_method.__name__))
            logger.error('- New endpoint: {}.{}.{}'.format(method.__module__, class_name, method.__name__))
            raise Exception(f'The endpoint {http_method} {uri_pattern} is already registered')

        # Check coherence of the options passed to the decorator.
        if authentication_required and not signature_required:
            logger = get_logger()
            logger.error('Method {}.{}.{} requires authentication without signature'.format(
                method.__module__, class_name, method.__name__))
            raise Exception('Signature MUST be requested when authentication is required')

        # Register the specified class method to handle the specified HTTP
        # method for the given Uniform Resource Identifier (URI).
        HttpRequestHandler.handlers[hash(http_method_spec)] = http_method_spec

        @functools.wraps(method)
        def decorated(self, request, *args, **kwargs):
            # Retrieve the identification of the RESTful API application that the
            # HTTP request is sent to. Check the signature of the HTTP request when
            # required.
            request.app_id = get_request_application_id(request, signature_required)

            # Retrieve the version of the RESTful API that the client application
            # has integrated, and detailed information about this client
            # application if identified.
            request.client_api_version, request.client_application = get_client_application_info(
                request, compatibility_required)

            # Retrieve the login session of the user on behalf of whom the HTTP
            # request is sent to the RESTful API server.
            session = get_account_session(request, request.app_id, authentication_required)
#            request.account_id = session and session.account_id
            request.session = session

            # The content type of HTTP POST and HTTP PUT requests MUST be of
            # "application/json", unless the HTTP request corresponds to file(s)
            # upload, in which case the content type of the HTTP request MUST be of
            # "multipart/form-data; (...)".
            if json_data and request.http_method in (HttpMethod.POST, HttpMethod.PUT):
                content_type = request.headers.get('Content-Type')
                expected_content_type = 'multipart/form-data' if len(request.uploaded_files) > 0 else 'application/json'
                if content_type is None or content_type.split(';')[0] != expected_content_type:
                    raise Exception(f'The content type of this HTTP request is expected to be "{expected_content_type}"')

            # Execute the method responsible for handling the HTTP request.
            return method(self, request, *args, **kwargs)

        return decorated

    return wrapper


def get_account_session(request, app_id, authentication_required):
    """
    Return the login session of the user on behalf whom a HTTP request is
    sent to the RESTful API server.


    :param request: An instance `HttpRequest`.

    :param app_id: Identification of the client application.

    :param authentication_required: Indicate whether the wrapped method
        requires the user, on behalf of whom the HTTP request is sent, to
        be authenticated or not.  If `True`, the client application MUST
        provide the HTTP header field `X-Authentication`, passing the
        identification of the login session of this user.


    :return: An instance `Session` if the user is authenticated against
        the RESTful API server, `None` otherwise.


    :raise ExpiredSessionException: if the account session of the user has
        expired.  The user needs to login again.

    :raise MissingHeaderException: If the request requires the user, on
        behalf of whom the HTTP request is sent, to be authenticated while
        the client application didn't pass the HTTP header
        `X-Authentication`.
    """
    session_id = request.get_header(
        'X-Authentication',
        data_type=HttpRequest.ArgumentDataType.uuid,
        is_required=authentication_required)

    # Retrieve the user session of the user if it exists and is not expired.
    return session_id and SessionService().get_session(app_id, session_id)


def get_client_application_info(request, compatibility_required):
    """
    Return the version of the RESTful API integrated in the client
    application that sent a HTTP request to the RESTful API server.


    :param request: An instance `HttpRequest`.

    :param compatibility_required: Indicate whether the wrapped method
        requires the client application to be strictly compatible with
        the version of the RESTful API application's.  If `True`, the
        client application MUST provide the HTTP header field
        `X-API-Version` which value MUST comply with a version number
        using a standard tuple of integers: `major.minor.patch`.


    :return: A named tuple `(client_api_version, client_application)`
        where:

        * `client_api_version`: An instance `Version` that represents the
          version of the RESTful API integrated in the client application.

        * `client_application`: An instance `ClientApplication` that
          represents information about the client application that sent the
          HTTP request, or `None` if the application is not identified.


    :raise HttpRequest.DeprecatedApiException: If API version
        compatibility is required while the client application has
        integrated a version of the RESTful API older than the one
        currently deployed.
    """
    # When the API version compatibility is required, check the presence of
    # the HTTP header `X-API-Version` and check whether its value is above
    # the version of the RESTful API currently deployed.
    client_api_version = request.get_header(
        'X-API-Version',
        data_type=HttpRequest.ArgumentDataType.version,
        is_required=compatibility_required)

    if compatibility_required:
        if settings.API_VERSION > client_api_version:
            raise HttpRequest.DeprecatedApiException(
                f'Client application deprecated API version {request.api_version} ({settings.API_VERSION} required)')

    # If a User-Agent HTTP header is provided, decompose each component.
    user_agent = request.get_header('User-Agent', is_required=False)
    match = user_agent and HttpRequest.REGEX_USER_AGENT.match(user_agent)

    return client_api_version, match and ClientApplication(
        match.group(1),  # Product name
        Version(match.group(2)),  # Product version
        match.group(3),  # OS name
        Version(match.group(4)),  # OS version
        match.group(5))  # Device model


def get_request_application_id(request, signature_required):
    """
    Return the identification of the client application that sent the
    HTTP request.


    :param request: An instance `HttpRequest`.

    :param signature_required: indicate whether the wrapped method
        requires the HTTP request to be signed with the Secret Key tied
        with the Consumer Key of the client application that sent this
        request.  If `True`, the client application MUST provide the
        HTTP header fields `X-API-Key` and `X-API-Sig`.


    :return: identification of the RESTful API application the HTTP
        request is sent to.
    """
    # When a RESTful API application is deployed on a development or an
    # integration, the signature of an HTTP request is not absolutely
    # required.
    if signature_required:
        environment_stage = getattr(settings, 'ENVIRONMENT_STAGE', EnvironmentStage.dev)
        signature_required = environment_stage not in (
            EnvironmentStage.dev,
            EnvironmentStage.int
        )

    # When the signature of the HTTP request is required, check the presence
    # of the two HTTP headers `X-API-Key` and `X-API-Sig`, and check whether
    # the digest hash of the HTTP request as provided by the client
    # application is valid.
    #
    # @note: Authenticated HTTP request required HTTP signature, therefore
    #     checking the signature of a HTTP request has to be done before the
    #     authentication verification.
    consumer_key = request.get_header('X-API-Key', data_type=HttpRequest.ArgumentDataType.hexadecimal)
    api_sig = request.get_header('X-API-Sig', is_required=signature_required)

    return ApplicationService().validate_signature(
        consumer_key,
        request.uri,
        request.raw_body if request.headers.get('Content-Type').startswith('application/json') else None,
        api_sig,
        strict=signature_required)
