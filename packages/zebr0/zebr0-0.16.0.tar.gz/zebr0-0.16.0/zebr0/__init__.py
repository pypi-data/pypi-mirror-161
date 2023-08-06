from __future__ import annotations

import argparse
import http.server
import json
import threading
from pathlib import Path
from typing import List, Optional, Any

import jinja2
import requests_cache

ENCODING = "utf-8"

URL = "url"
LEVELS = "levels"
EXTRA_VARS = "extra-vars"
CACHE = "cache"

URL_DEFAULT = "https://hub.zebr0.io"
LEVELS_DEFAULT = []
EXTRA_VARS_DEFAULT = {}
CACHE_DEFAULT = 300
CONFIGURATION_FILE_DEFAULT = Path("/etc/zebr0.conf")


class Client:
    """
    Nested key-value system with built-in inheritance and templating, designed for configuration management and deployment.

    This Client can connect to any key-value server that follows HTTP REST standards.
    For now it only supports plain text responses, JSON support is in the works.

    Nested keys and inheritance:
    To fully exploit the Client, you should define a structure in the naming of your keys, like "<project>/<environment/<key>".
    Then use the "levels" parameter of the constructor to point to a specific project and environment, like ["mattermost", "production"].
    Finally, use the get() function to fetch a key and it will automatically look for the most specific value possible.
    Note that you don't have to duplicate keys for each project and environment, as they can be inherited from their parent level.

    Templating:
    By default, values are processed through the Jinja templating engine.
    You can refer to the constructor parameters {{ url }}, {{ levels[x] }} or any given extra variable.
    You can also include the value from another key {{ "another-key" | get }} or the content of a file {{ "/path/to/the/file" | read }}.
    Visit https://jinja.palletsprojects.com to learn more about filters, blocks and other features of Jinja that you can use.

    Configuration file:
    Client configuration can also be read from a JSON file, a simple dictionary with the "url", "levels" and "cache" keys.
    The save_configuration() function can help you create one from an existing Client.
    The suggested default path can be used for a system-wide configuration.
    If provided, constructor parameters will always supersede the values from the configuration file, which in turn supersede the default values.

    Note that the inheritance and templating mechanisms are performed by the client, to be as server-agnostic as possible.

    :param url: URL of the key-value server, defaults to https://hub.zebr0.io
    :param levels: levels of specialization (e.g. ["mattermost", "production"] for a <project>/<environment>/<key> structure), defaults to []
    :param extra_vars: dictionary that can be used to declare extra variables to the templating engine, defaults to {}
    :param cache: in seconds, the duration of the cache of http responses, defaults to 300 seconds
    :param configuration_file: path to the configuration file, defaults to /etc/zebr0.conf for a system-wide configuration
    """

    def __init__(self, *, url: str = "", levels: Optional[List[str]] = None, cache: int = 0, extra_vars: dict = None, configuration_file: Path = CONFIGURATION_FILE_DEFAULT, **_) -> None:
        self.configuration_file = configuration_file

        # first set default values
        self.url = URL_DEFAULT
        self.levels = LEVELS_DEFAULT
        self.extra_vars = EXTRA_VARS_DEFAULT
        self.cache = CACHE_DEFAULT

        # then override with the configuration file if present
        try:
            configuration = json.loads(configuration_file.read_text(ENCODING))

            self.url = configuration.get(URL, URL_DEFAULT)
            self.levels = configuration.get(LEVELS, LEVELS_DEFAULT)
            self.extra_vars = configuration.get(EXTRA_VARS, EXTRA_VARS_DEFAULT)
            self.cache = configuration.get(CACHE, CACHE_DEFAULT)
        except OSError:
            pass  # configuration file not found, ignored

        # finally override with the parameters if present
        if url:
            self.url = url
        if levels:
            self.levels = levels
        if extra_vars:
            self.extra_vars = extra_vars
        if cache:
            self.cache = cache

        # templating setup
        self.jinja_environment = jinja2.Environment(keep_trailing_newline=True)
        self.jinja_environment.globals[URL] = self.url
        self.jinja_environment.globals[LEVELS] = self.levels
        self.jinja_environment.globals.update(self.extra_vars)
        self.jinja_environment.filters["get"] = self.get
        self.jinja_environment.filters["read"] = read

        # http requests setup
        self.http_session = requests_cache.CachedSession(backend="memory", expire_after=cache)

    def get(self, key: str, default: str = "", template: bool = True, strip: bool = True, extra_vars: dict = None) -> str:
        """
        Fetches the value of a provided key from the server.
        Based on the levels defined in the Client, will return the first key found from the deepest level to the root level.
        A default value can be provided to be returned if the key isn't found at any level.

        :param key: key to look for
        :param default: value to return if the key isn't found at any level
        :param template: shall the value be processed by the templating engine?
        :param strip: shall the value be stripped off leading and trailing white spaces?
        :param extra_vars: dictionary that can be used to declare extra variables to the templating engine
        :return: the resulting value of the key
        """

        # let's do this with a nice recursive function :)
        def fetch(levels):
            response = self.http_session.get("/".join([self.url] + levels + [key]))

            if response.ok:
                return response.text  # if the key is found, we return the value
            elif levels:
                return fetch(levels[:-1])  # if not, we try at the parent level
            else:
                return default  # if we're at the top level, the key just doesn't exist, we return the default value

        value = fetch(self.levels)  # let's try at the deepest level first

        value = self.jinja_environment.from_string(value).render(extra_vars or {}) if template else value  # templating
        value = value.strip() if strip else value  # stripping

        return value

    def save_configuration(self) -> None:
        """
        Saves the Client's configuration to a JSON file.
        """

        configuration = {URL: self.url, LEVELS: self.levels, EXTRA_VARS: self.extra_vars, CACHE: self.cache}
        self.configuration_file.write_text(json.dumps(configuration), ENCODING)


class TestServer:
    """
    Rudimentary key-value HTTP server, for development or testing purposes only.
    The keys and their values are stored in a dictionary, that can be defined either in the constructor or through the "data" attribute.
    Access logs are also available through the "access_logs" attribute.

    Basic usage:

    >>> server = TestServer({"key": "value", ...})
    >>> server.start()
    >>> ...
    >>> server.stop()

    Or as a context manager, in which case the server will be started automatically, then stopped at the end of the "with" block:

    >>> with TestServer() as server:
    >>>    server.data = {"key": "value", ...}
    >>>    ...

    :param data: the keys and their values stored in a dictionary, defaults to an empty dictionary
    :param address: the address the server will be listening to, defaults to 127.0.0.1
    :param port: the port the server will be listening to, defaults to 8000
    """

    def __init__(self, data: dict = None, address: str = "127.0.0.1", port: int = 8000) -> None:
        self.data = data or {}
        self.access_logs = []

        class RequestHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(zelf):
                key = zelf.path[1:]  # the key is the request's path, minus the leading "/"
                value = self.data.get(key)

                if value:
                    zelf.send_response(200)
                    zelf.end_headers()
                    zelf.wfile.write(str(value).encode(ENCODING))
                else:
                    zelf.send_response(404)
                    zelf.end_headers()

                self.access_logs.append(zelf.path)

        self.server = http.server.ThreadingHTTPServer((address, port), RequestHandler)

    def start(self) -> None:
        """ Starts the server in a separate thread. """
        threading.Thread(target=self.server.serve_forever).start()

    def stop(self) -> None:
        """ Stops the server. """
        self.server.shutdown()
        self.server.server_close()

    def __enter__(self) -> TestServer:
        """ When used as a context manager, starts the server at the beginning of the "with" block. """
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """ When used as a context manager, stops the server at the end of the "with" block. """
        self.stop()


def read(path: str, encoding: str = ENCODING) -> str:
    """
    Filter for the Jinja templating engine, that allows to read a file's content.

    :param path: path to the file
    :param encoding: encoding of the file, defaults to "utf-8"
    :return: the content of the file
    """

    try:
        return Path(path).read_text(encoding=encoding)
    except IOError:
        return ""


def build_argument_parser(*args: Any, **kwargs: Any) -> argparse.ArgumentParser:
    """
    Builds an ArgumentParser that zebr0 executables can use to share a common Client CLI syntax.

    :param args: arguments of the ArgumentParser constructor
    :param kwargs: keyword arguments of the ArgumentParser constructor
    :return: the customized ArgumentParser
    """

    argparser = argparse.ArgumentParser(*args, **kwargs)

    argparser.add_argument("-u", "--url", help=f"URL of the key-value server, defaults to {URL_DEFAULT}", metavar="<url>")
    argparser.add_argument("-l", "--levels", nargs="*", help=f'levels of specialization (e.g. "mattermost production" for a <project>/<environment>/<key> structure), defaults to {LEVELS_DEFAULT}', metavar="<level>")
    argparser.add_argument("-e", "--extra-vars", type=lambda s: dict(**json.loads(s)), help=f'json object that can be used to declare extra variables to the templating engine (e.g. {{"platform": "aws"}}), defaults to {EXTRA_VARS_DEFAULT}', metavar="<json object>")
    argparser.add_argument("-c", "--cache", type=int, help=f"in seconds, the duration of the cache of http responses, defaults to {CACHE_DEFAULT}", metavar="<duration>")
    argparser.add_argument("-f", "--configuration-file", type=Path, default=CONFIGURATION_FILE_DEFAULT, help=f"path to the configuration file, defaults to {CONFIGURATION_FILE_DEFAULT} for a system-wide configuration", metavar="<path>")

    return argparser


def main(args: Optional[List[str]] = None) -> None:
    argparser = build_argument_parser(description="Saves zebr0's configuration in a JSON file.")
    argparser.add_argument("-t", "--test", help="tests the configuration by fetching a key", metavar="<key>")
    args = argparser.parse_args(args)

    # creates a client from the given parameters, then saves the configuration
    client = Client(**vars(args))
    client.save_configuration()

    if args.test:
        # creates a client from the configuration file, then tests the configuration
        client = Client(configuration_file=args.configuration_file)
        print(client.get(args.test))
