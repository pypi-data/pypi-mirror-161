"""HTTP test server to make testing easy with external APIs."""
# pylint: disable=unused-import
try:
    from importlib.metadata import version
except ImportError:  # pragma: no cover
    from importlib_metadata import version  # type: ignore

import json
import os
import threading

import flask
import pytest
from fw_utils import AttrDict
from werkzeug.serving import WSGIRequestHandler, make_server

__version__ = version(__name__)

# by default a random available port is selected - allow making it deterministic
PORT = int(os.getenv("FW_HTTP_TESTSERVER_PORT") or 0)

# NOTE werkzeug 2.1 switched to HTTP/1.1 to support keep-alive
# but this results unclosed socket ResourceWarning in tests
# use HTTP/1.0 until we figure out how to solve this
WSGIRequestHandler.protocol_version = "HTTP/1.0"


@pytest.fixture(scope="function")
def http_testserver(http_testserver_session):  # pylint: disable=redefined-outer-name
    """Function scoped HTTP server fixture that cleans state after each test."""
    yield http_testserver_session
    http_testserver_session.reset()


@pytest.fixture(scope="session")
def http_testserver_session():
    """Session scoped HTTP server fixture that shuts down upon exit."""
    try:
        server = HttpTestServer(PORT)
        server.start()
        yield server
    finally:
        server.shutdown()


class HttpTestServer(threading.Thread):
    """HTTP server with on-the-fly handler configuration for testing."""

    def __init__(self, port: int = 0):
        super().__init__()
        self.app = flask.Flask(self.__class__.__name__)
        self.app.before_request(self._track_request)
        self.server = make_server("0.0.0.0", port, self.app, threaded=True)
        self.host = "127.0.0.1"
        self.port: int = self.server.port
        self.addr = f"{self.host}:{self.port}"
        self.url = f"http://{self.addr}"
        self.reset()

    def __getattr__(self, name: str):
        """Proxy attributes of flask for simple access."""
        return getattr(flask, name)

    def __repr__(self) -> str:
        """Return string representation of the test server."""
        return f"{type(self).__name__}(port={self.port})"

    def run(self):
        """Thread entrypoint called upon start()."""
        self.server.serve_forever()

    def _track_request(self):
        """Track each incoming request for test assertions later."""
        request = flask.request
        body = request.get_data()  # read/store before accessing .files
        # TODO filenames under files shouldn't be inflated for dot-notation
        self.requests.append(
            AttrDict(
                name=f"{request.method} {request.path}",
                method=request.method,
                url=request.path,
                params=AttrDict(request.args),
                headers=AttrDict(request.headers),
                form=AttrDict(request.form),
                body=body,
                json=request.get_json(silent=True),
                files={k: v.getvalue() for k, v in request.files.items()},
            )
        )

    @property
    def request_log(self):
        """Return the list of names for the tracked requests."""
        return [request.name for request in self.requests]

    @property
    def request_map(self):
        """Return the dictionary of the tracked requests by name."""
        return {request.name: request for request in self.requests}

    def pop_first(self):
        """Return (and remove) the first tracked request."""
        return self.requests.pop(0)

    # pylint: disable=too-many-arguments
    def add_response(
        self, url, body="", method="GET", status=200, headers=None, func=None
    ):
        """Add handler that responds with given body, status and headers."""

        def callback(*_args, **_kwargs):
            if func:
                func(self.requests[-1])
            data = json.dumps(body) if isinstance(body, list) else body
            return data, status, headers or {}

        self.add_callback(url, callback, methods=[method])

    def add_callback(self, url, callback, methods=("GET",)):
        """Add a custom callback as a handler."""
        callback.__name__ = "_".join([url, *sorted(methods)])
        # allow overriding view function
        self.app.view_functions.pop(callback.__name__, None)
        self.app.add_url_rule(url, methods=methods, view_func=callback)

    def reset(self):
        """Restore initial state."""
        self.requests = []
        self.app.url_map = self.app.url_map_class()
        self.app.view_functions = {"static": self.app.view_functions["static"]}

    def shutdown(self):
        """Shutdown server upon receiving GET /shutdown."""
        self.server.shutdown()
        self.join()
