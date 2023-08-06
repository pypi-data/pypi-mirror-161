#!/usr/bin/env python
#
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

import collections
import logging
import os
import sys

from majormode.perseus.constant.stage import EnvironmentStage
from majormode.perseus.utils import env
import psutil


# Build the default logging formatter.
DEFAULT_LOGGING_FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")


def __get_address_from_environment():
    """
    Return the host address of the API server instances

    The function retrieve the address defined in the environment variable
    `API_SERVER_HOSTNAME`, or defaults to the address defined in the
     constant `DEFAULT_API_SERVER_HOSTNAME` of the settings file.


    :return: The host address of the API server instances


    :raise Exception: If no address has been defined in the environment
        variable `API_SERVER_HOSTNAME`, nor in the constant
        `DEFAULT_API_SERVER_HOSTNAME` of the settings file.
    """
    import settings  # Settings of the inheriting API server application.
    address = env.getenv('API_SERVER_HOSTNAME', default_value=getattr(settings, 'DEFAULT_API_SERVER_HOSTNAME'))
    if address is None:
        raise Exception('No host address (or interface) has been defined in the environment or in the settings file')
    return address


def __get_console_handler(logging_formatter=DEFAULT_LOGGING_FORMATTER):
    """
    Return a logging handler that sends logging output to the system's
    standard output.


    :param logging_formatter: An object `Formatter` to set for this handler.


    :return: An instance of the `StreamHandler` class.
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging_formatter)
    return console_handler


def __get_current_process_name():
    """
    Return the name of the current process


    :return: The name of the current process.
    """
    return psutil.Process().name()


def __get_opened_port_processes():
    """
    Return the list of processes that have opened TCP or UDP ports.


    :return: A dictionary where the key corresponds to a port number and
        the value corresponds to a list of `psutil.Process` that have
        opened this port.
    """
    opened_port_processes = collections.defaultdict(list)

    for process in psutil.process_iter():
        try:
            for connection in process.connections():
                if connection.status == psutil.CONN_LISTEN:
                    opened_port_processes[connection.laddr.port].append(process)
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

    return opened_port_processes


def __get_ports(ports=None):
    """
    Return the list of the ports of the API server instances.


    :param ports: A list of Internet Protocol port numbers which server
        application instances will listen at.  If more than one port is
        specified, the function will fork as many processes to listen at
        these additional ports.

        The argument `ports` can be an integer, a string representing a list
        of ports separated with comma, a list of integers or strings.

        If the argument `ports` is null or empty, the function retrieves the
        list of ports from the environment variable `API_SERVER_PORTS` if
        defined, otherwise the default variable `DEFAULT_API_SERVER_PORT`
        defined in the file `settings.py` of the API server project.


    :return: A list of integers corresponding to the ports of the API
        server instances.


    :raise TypeError: If the argument `ports` is not an integer, a string,
        or a list of integers/strings.

    :raise ValueError: If no ports are specified.
    """
    if ports is None:
        ports = __get_ports_from_environment()

    if isinstance(ports, int):  # integer
        ports = [ports]
    elif isinstance(ports, str):  # comma-separated values
        ports = [int(port) for port in ports.split(',')]
    elif isinstance(ports, (list, tuple, set)):
        ports = [int(port) for port in ports]
    else:
        raise TypeError("A port or a list of ports is expected")

    if len(ports) == 0:
        raise ValueError("No port number has been specified")

    return ports


def __get_ports_from_environment():
    """
    Return the ports of the API server instances

    The function retrieve the ports defined in the environment variable
    `API_SERVER_PORTS`, or defaults to the port defined in the constant
    `DEFAULT_API_SERVER_PORT` of the settings file.


    :return: A list of integers.


    :raise Exception: If no port has been defined in the environment
        variable `API_SERVER_PORTS`, nor in the constant
        `DEFAULT_API_SERVER_PORT` of the settings file.
    """
    import settings

    ports = env.getenv(
        'API_SERVER_PORTS',
        is_required=False,
        data_type=env.DataType.list,
        item_data_type=env.DataType.integer)

    if not ports:
        port = getattr(settings, 'DEFAULT_API_SERVER_PORT')
        if port is None:
            raise Exception('No port has been defined in the environment or in the settings file')
        ports = [port]

    return ports


def __load_environment_variables():
    """
    Load the environment variables from the .env file located in the
    current directory.
    """
    env_file_path_name = os.path.join(os.getcwd(), '.env')
    print(f'Loading environment file {env_file_path_name}')  # Logger not setup yet
    return env.loadenv(env_file_path_name)


def __setup_logger(
        logging_formatter=DEFAULT_LOGGING_FORMATTER,
        logging_level=logging.INFO,
        logger_name=None):
    """
    Setup a logging handler that sends logging output to the system's
    standard output.


    :param logging_formatter: An object `Formatter` to set for this handler.

    :param logger_name: Name of the logger to add the logging handler to.
        If `logger_name` is `None`, the function attaches the logging
        handler to the root logger of the hierarchy.

    :param logging_level: The threshold for the logger to `level`.  Logging
        messages which are less severe than `level` will be ignored;
        logging messages which have severity level or higher will be
        emitted by whichever handler or handlers service this logger,
        unless a handler’s level has been set to a higher severity level
        than `level`.


    :return: An object `Logger`.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)
    logger.addHandler(__get_console_handler(logging_formatter=logging_formatter))
    logger.propagate = False
    return logger


def reload(ports=None):
    raise NotImplementedError


def start(ports=None, address=None):
    """
    Run the server application on the specified port(s).


    :param ports: A list of Internet Protocol port numbers which server
        application instances will listen at.  If more than one port is
        specified, the function will fork as many processes to listen at
        these additional ports.

        The argument `ports` can be an integer, a string representing a list
        of ports separated with comma, a list of integers or strings.

        If the argument `ports` is null or empty, the function retrieves the
        list of ports from the environment variable `API_SERVER_PORTS` if
        defined, otherwise the default variable `DEFAULT_API_SERVER_PORT`
        defined in the file `settings.py` of the API server project.
        
    :param address: Address to bound the listening socket to.  Address may
        be either an IP address or hostname.  If it’s a hostname, the
        server will listen on all IP addresses associated with the name.
        Address may be an empty string or `None` to listen on all
        available interfaces.


    :raise Exception: If some of the specified ports are in use.

    :raise TypeError: If the argument `ports` is not an integer, a string,
        or a list of integers/strings.

    :raise ValueError: If no ports are specified.
    """
    __load_environment_variables()
    import settings  # Settings of the inheriting API server application.

    # Retrieve the host address and port of the API server instances.
    if address is None:
        address = __get_address_from_environment()

    ports = __get_ports(ports=ports)

    # Retrieve the logger with the specified name or, if name is `None`,
    # the logger which is the root logger of the hierarchy.
    logger_name = getattr(settings, 'LOGGER_NAME')
    logging_formatter = getattr(settings, 'LOGGING_FORMATTER')
    logging_level = getattr(settings, 'LOGGING_LEVEL')
    logger = __setup_logger(
        logging_formatter=logging_formatter,
        logging_level=logging_level,
        logger_name=logger_name)

    # Check whether some specified port numbers are already used by other
    # processes.
    opened_ports = __get_opened_port_processes()
    unavailable_ports = [port for port in ports if port in opened_ports]

    if len(unavailable_ports) > 0:
        unavailable_ports_str = ', '.join([str(port) for port in unavailable_ports])
        raise Exception(f"The following ports are already in use: {unavailable_ports_str}")

    # Fork the process to run as many instances as the number of ports
    # passed to this function, including this instance.
    from majormode.perseus.bootstrap import tornado_handler

    environment_stage = getattr(settings, 'ENVIRONMENT_STAGE', EnvironmentStage.dev)
    logger.info(f"Environment stage {environment_stage}")

    for port in ports[1:]:
        pid = os.fork()
        if pid == 0:  # Child process
            logger.info(f"Boot the API server instance ({address}:{port})")
            tornado_handler.boot(port, settings.APP_PATH, address=address)

    logger.info(f"Boot the API server instance ({address}:{ports[0]})")
    tornado_handler.boot(ports[0], settings.APP_PATH, address=address)


def stop(ports):
    """
    Terminate the current processes running that are listening TCP and
    UPD connections on the specified ports.


    :param ports: A list of Internet Protocol port numbers which server
        application instances will listen at.  If more than one port is
        specified, the function will fork as many processes to listen at
        these additional ports.

        The argument `ports` can be an integer, a string representing a list
        of ports separated with comma, a list of integers or strings.

        If the argument `ports` is null or empty, the function retrieves the
        list of ports from the environment variable `API_SERVER_PORTS` if
        defined, otherwise the default variable `DEFAULT_API_SERVER_PORT`
        defined in the file `settings.py` of the API server project.


    :return: A list of tuple `(psutil.Process, port)` of the processes
        that the function has terminated.

    :raise TypeError: If the argument `ports` is not an integer, a string,
        or a list of integers/strings.

    :raise ValueError: If no ports are specified.
    """
    __load_environment_variables()
    import settings  # Settings of the inheriting API server application.

    ports = __get_ports(ports=ports)

    # Retrieve the logger with the specified name or, if name is `None`,
    # the logger which is the root logger of the hierarchy.
    logger_name = getattr(settings, 'LOGGER_NAME')
    logging_formatter = getattr(settings, 'LOGGING_FORMATTER')
    logging_level = getattr(settings, 'LOGGING_LEVEL')
    logger = __setup_logger(
        logging_formatter=logging_formatter,
        logging_level=logging_level,
        logger_name=logger_name)

    # Search for Python processes listening at the specified ports and
    # terminate them.
    opened_port_processes = __get_opened_port_processes()
    terminated_processes = []

    for port in ports:
        for process in opened_port_processes[port]:
            try:
                logger.info(f"Process '{process.name()}' is listening at port {port}")
                if process.name() == __get_current_process_name():
                    logger.info(f"Stop the API server instance ({port})...")
                    process.terminate()
                    process.wait(5000)
                    terminated_processes.append((process, port))
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass

    return terminated_processes
