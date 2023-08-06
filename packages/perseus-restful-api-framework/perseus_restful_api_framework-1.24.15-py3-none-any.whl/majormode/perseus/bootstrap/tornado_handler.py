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
import json
import logging
import os
import sys
import traceback

import tornado.httpserver
import tornado.ioloop
import tornado.web

from majormode.perseus.constant.http import HttpMethod
from majormode.perseus.model import obj
from majormode.perseus.service.base_http_handler import HttpRequest
from majormode.perseus.service.base_http_handler import HttpRequestHandler
from majormode.perseus.service.base_http_handler import HttpRequestLog
from majormode.perseus.service.base_http_handler import HttpResponse
from majormode.perseus.service.base_service import BaseService
from majormode.perseus.utils import cast

import settings


class MainHandler(tornado.web.RequestHandler):
    """

    """
    class RestHeartbreakerHttpResponse:
        """
        Represent the response to a HTTP request back to a client that is not
        compliant with the REST paradigm, such as a Flash application.

        Flash application cannot easily interpret HTTP status codes.  The REST
        framework should therefore have an option for returning status in JSON
        format.  The HTTP status should always be ``200``, with the actual
        success code returned in the body of the content.  This code can then
        be interpreted by Flash.

        This class decorates the HTTP response into a dictionary containing
        two keys:

        * ``code``: indicate the real HTTP status code of the response.

        * ``response``: the embedded response's object.

        The string representation of an instance of this class corresponds to
        JSON serialization of this dictionary and embedded object, which can
        be passed back to the client application that performed the HTTP
        request.
        """
        def __init__(self, status_code, response):
            """
            Build a decorated HTTP response for a client application that is not
            REST compliant and that cannot get access to HTTP status code directly
            from the HTTP library it is using.


            :param status_code: the real HTTP status code of the HTTP response.

            :param response: an instance of ``base_http_handler.HttpResponse``
                corresponding to the real HTTP response to be returned to the
                client application.
            """
            self.status_code = status_code
            self.response = response

        def __str__(self):
            """
            Return a JSON string representation of the decorated HTTP response
            corresponding to an array of two keys:

            * ``code``: Indicate the real HTTP status code of the response.

            * ``response``: The embedded response's object.


            :return: String representation of the JSON expression that decorates
                the result returned by the method that has processed the HTTP
                request.
            """
            return json.dumps(self.response.result and obj.stringify(
                dict(code=self.status_code, response=self.response.result)))

    class RuntimeException(Exception):
        """
        Base class of runtime exception that might occur while processing a
        HTTP request.
        """
        def __init__(self, message=None):
            super().__init__(message)

    class HandlerNotFoundException(RuntimeException):
        """
        Signal that no HTTP handler matches the specified HTTP method and
        Uniform Resource Identifier (URI) of the HTTP request that the client
        application sent to the RESTful API server.
        """

    # Mapping between exceptions raised by HTTP handlers and HTTP codes.
    BASE_SERVICE_EXCEPTIONS = (
        (BaseService.DeletedObjectException, 410),
        (BaseService.DisabledObjectException, 410),
        (BaseService.InvalidOperationException, 405),
        (BaseService.IllegalAccessException, 403),
        (BaseService.InvalidArgumentException, 400),
        (BaseService.UndefinedObjectException, 404),

        # @note: MUST be declared at the end to catch all the business logic
        #     exceptions that don't inherit from framework exception, but
        #    `BaseServiceException`.
        (BaseService.BaseServiceException, 412),
    )

    def initialize(self, logger):
        self._logger = logger

    def _find_handler(self, http_method, uri_path):
        """
        Return the handler corresponding to the current HTTP request based on
        the HTTP method and the URL of this request.


        :param http_method: An item of the enumeration `HttpMethod`.


        :return: A ``HttpMethodSpec`` instance wrapping a class inheriting
            from ``HttpRequestHandler``.


        :raise HandlerNotFoundException: If the specified URI path doesn't
            match any HTTP handler for the given HTTP method.
        """
        self._logger.debug(f'Searching HTTP handler for "{http_method} {uri_path}"...')

        for handler in HttpRequestHandler.handlers.values():
            if http_method == handler.http_method and handler.uri_pattern_regex.match(uri_path):
                self._logger.debug(f'Found HTTP handler {handler.handler_method} {handler.uri_pattern})')
                return handler

        raise MainHandler.HandlerNotFoundException()

    @staticmethod
    def __get_http_method(request):
        """
        Return the real HTTP method of the specified HTTP request.

        While not normally an issue with thick clients, accessing full RESTful
        capabilities of available services via browsers often is problematic
        as many browsers, Flash, and some firewalls, only allow a form to GET
        or POST.  They don't allow for other HTTP methods, like PUT or DELETE.
        A solution is to add a header to the HTTP request, X-HTTP-Method-Override,
        that is supposed to be interpreted by the service and acted upon
        regardless of the actual HTTP method used.  Another solution is to add
        a hidden field as CakePHP usually does (cf. CakePHP, Cookbook 1.3,
        Common Tasks With CakePHP, REST;
        http://book.cakephp.org/1.3/en/The-Manual/Common-Tasks-With-CakePHP/REST.html).


        :param request: A `tornado.httputil.HTTPServerRequest` instance
            containing additional request parameters including headers and
            body data.


        :return: an item of the enumeration `HttpMethod`.
        """
        # Check whether the client application requests the RESTful API server
        # to override the method specified in the request by whether passing the
        # HTTP header `X-HTTP-Method-Override`, whether passing the argument
        # `_method` (a convention becoming increasingly common in other
        # frameworks).
        return cast.string_to_enum(
            request.headers.get('X-HTTP-Method-Override')
            or request.arguments.get('_method')
            or request.method,
            HttpMethod)

    @staticmethod
    def __get_uploaded_files(request):
        """
        Return information about the files that have been uploaded along with
        the HTTP request sent to the RESTful API server.


        :param request: A `tornado.httputil.HTTPServerRequest` instance
            containing additional request parameters including headers and
            body data.


        :return: A list of `HttpRequest.HttpRequestUploadedFile` instances.
        """
        return [
            HttpRequest.HttpRequestUploadedFile(
                field_name,
                field_value['filename'],
                field_value['content_type'],
                field_value['body'])
            for (field_name, field_values) in request.files.items()
            for field_value in field_values]

    def do(self, *args, **kwargs):
        """
        Process the HTTP request that a client application sends to the
        platform, calling the underlying service function that matches the
        specified HTTP method and Uniform Resource Identifier (URI).
        """
        request = None
        exception = None

        execution_start_time = datetime.datetime.now()

        try:
            # Retrieve the possibly overridden HTTP method of this request.
            http_method = self.__get_http_method(self.request)

            # Build the HTTP request to be processed.
            request = HttpRequest(
                http_method,
                self.request.uri,
                dict([(key, values[0].decode("utf-8")) for key, values in self.request.arguments.items()]),
                self.request.headers,
                self.request.remote_ip,
                body=self.request.body,
                uploaded_files=self.__get_uploaded_files(self.request))

#            request._prepare_()

            # Find and execute the HTTP handler responsible for processing this
            # HTTP request (endpoint defined with HTTP method and URI).
            handler = self._find_handler(http_method, self.request.path)
            response = handler.process(request)

        except MainHandler.HandlerNotFoundException as exception:
            self.set_status(404)
            response = HttpResponse.from_exception(exception)

        except BaseService.BaseServiceException as exception:
            for (base_service_exception, http_status_code) in self.BASE_SERVICE_EXCEPTIONS:
                if isinstance(exception, base_service_exception):
                    self.set_status(http_status_code)
                    break

            response = HttpResponse.from_exception(exception)

        except Exception as exception:
            traceback.print_exc()
            self.set_status(500)
            response = HttpResponse.from_exception(exception)

        finally:
            execution_end_time = datetime.datetime.now()
            execution_duration = execution_end_time - execution_start_time

        # [PATCH] Checked whether the client application indicates that it is
        # not compliant with REST paradigm, such as Flash application, meaning
        # that it cannot easily interpret HTTP status codes with the library
        # it using.  The platform then decorate the real HTTP response and
        # code status in a JSON dictionary that is passed back to the client
        # application with HTTP status ``200``.
        is_rest_compliant = self.request.headers.get('X-REST-Compliance')
        if is_rest_compliant is not None:
            is_rest_compliant = cast.string_to_boolean(is_rest_compliant, strict=False)
        else:
            user_agent = self.request.headers.get('User-Agent')
            is_rest_compliant = (user_agent is None) or ('flash' not in user_agent.lower())

        if not is_rest_compliant:
            response = self.RestHeartbreakerHttpResponse(self.get_status(), response)
            self.set_status(200)

        # Return the JSON representation of the response back to the client
        # application.
        self.set_header("Content-Type", "application/json")

        self.write(str(response))
        dispatch_duration = datetime.datetime.now() - execution_end_time

        # Log detailed information related to the processing of this HTTP
        # request.
        # self._logger.info(json.dumps(jsonpickle.pickler.Pickler(unpicklable=False)  \
        #     .flatten(HttpRequestLog(request, response, execution_duration, dispatch_duration, exception))))

    def delete(self, *args, **kwargs):
        self.do(args, kwargs)

    def get(self, *args, **kwargs):
        self.do(args, kwargs)

    def on_finish(self) -> None:
        pass

    def options(self, *args, **kwargs):
        # self._logger.info(f'Ignoring OPTIONS {self.request.uri}')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'DELETE,GET,HEAD,OPTIONS,POST,PUT')
        self.set_header('Access-Control-Allow-Headers', '*')

    def post(self, *args, **kwargs):
        self.do(args, kwargs)

    def put(self, *args, **kwargs):
        self.do(args, kwargs)

    def set_default_headers(self):
        """
        Support Cross-Origin Resource Sharing (CORS)s a mechanism that uses
        additional HTTP headers to tell a browser to let a web application
        running at one origin (domain) have permission to access selected
        resources from a server at a different origin.

        A web application executes a cross-origin HTTP request when it
        requests a resource that has a different origin (domain, protocol, and
        port) than its own origin.
        """
        self.set_header('Content-Type', 'application/json')
        self.set_header('Access-Control-Allow-Origin', '*')

        # Firefox is the only browser that requires to specify comma-separated
        # values of header; Firefox strictly respects the ABNF specification for
        # the header Access-Control-Allow-Methods value. Firefox doesn't accept
        # the value "*".
        # [https://fetch.spec.whatwg.org/#cors-preflight-fetch]
        self.set_header('Access-Control-Allow-Headers', '*,Content-Type,X-Api-Key,X-Api-Sig')
        self.set_header('Access-Control-Allow-Methods', 'GET,HEAD,OPTIONS,POST,PUT')


def discover_http_handlers(app_path, logger):
    """
    Search recursively for Python files of HTTP request handlers.

    The naming convention specifies that HTTP request handler Python files
    MUST end with ``_http_handler.py``.

    The function searches Python files in the directory `site-packages`
    where third party Python libraries are installed in using `pip`.  The
    function also searches for `.egg` directories that contain the code of
    third party Python libraries installed with `easy_install`.


    :param app_path: Absolute path of the RESTful API server application.

    :param logger: The logger of the RESTful API server application.


    :todo: compiled Python files MUST be supported. These files are more
        likely deployed in a production environment.
    """
    search_paths = [
        path
        for path in sys.path
        if os.path.isdir(path) and (path.endswith('site-packages') or path.endswith('.egg'))
    ]

    search_paths += [app_path]

    for path in search_paths:
        logger.info(f'Searching HTTP handlers from {path}')
        for path_name, _dir_names_, file_names in os.walk(path, followlinks=False):
            for python_file_name in filter(lambda file_name: file_name.endswith('_http_handler.py'), file_names):
                python_module_name = '{}.{}'.format(
                    os.path.relpath(path_name, path).replace(os.sep, os.extsep),
                    os.path.splitext(python_file_name)[0])

                try:
                    __import__(python_module_name)  # [WARNING] Returns the top-level module.
                    _service_module_ = sys.modules[python_module_name]
                    logger.info(f'Python module {python_module_name} loaded')

                except ImportError:  # Ignore modules that are not in the Python path.
                    logger.info(f'Python module {python_module_name} ignored')
                    logger.debug(traceback.format_exc())


def boot(port, app_path, address=None):
    """
    Start the RESTful API application.

    The function first searches for HTTP handlers responsible for
    processing HTTP request for a given endpoint and HTTP method.


    :param address: Address to bound the listening socket to.  Address may
        be either an IP address or hostname.  If it’s a hostname, the
        server will listen on all IP addresses associated with the name.
        Address may be an empty string or `None` to listen on all
        available interfaces.

    :param port: Port to bound the listening socket to.

    :param app_path: Absolute path of the RESTful API server application.
    """
    # Retrieve the logger with the specified name or, if name is `None`,
    # the logger which is the root logger of the hierarchy.
    logger = logging.getLogger(getattr(settings, 'LOGGER_NAME'))

    # Search for methods responsible for handling HTTP requests.
    discover_http_handlers(app_path, logger)

    # Define the main handler of the RESTful API and start the server
    # application.
    application = tornado.web.Application([
        (r'.*', MainHandler, dict(logger=logger)),
    ])

    application.listen(port, address)
    tornado.ioloop.IOLoop.current().start()

