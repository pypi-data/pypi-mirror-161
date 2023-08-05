import cgi
import dataclasses
import functools
import itertools
import json
import pathlib
import time
import traceback
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing.context import Process
from typing import List, Union

import requests


def using_test_server(port=3000, response_map=None, log_dir="temp/"):
    def wrap(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            server = Process(
                target=run_test_server,
                kwargs=dict(port=port, response_map=response_map, log_dir=log_dir),
                daemon=False
            )
            server.start()
            time.sleep(2)
            r = requests.get(f'http://localhost:{port}/healthcheck')
            if r.status_code != 200:
                server.terminate()
                server.join()
                raise Exception("Server failed to start!")
            try:
                res = fn(*args, **kwargs)
            finally:
                server.terminate()
                server.join()
            return res

        return wrapper

    return wrap


def run_test_server(port=3000, response_map=None, log_dir="temp/"):
    server = TestServer(port=port, response_map=response_map, log_dir=log_dir)
    server.serve_forever(50)


@dataclasses.dataclass
class ParseAndExtractDataSummary:
    path: str
    url_qs: dict
    content_qs: dict
    content_type: str


def default_encoder(obj):
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        return str(obj)


class TestServer(HTTPServer):
    def __init__(self, port=3000, shutdown_poll_freq=50, response_map=None, log_dir="temp/"):
        if response_map is None:
            self.response_map = {}
        else:
            self.response_map = response_map
        print(f"Starting server on port {port}")
        self.started = False
        self.process = None
        self.log_dir = log_dir
        self.log_list = []
        self.shutdown_poll_freq = shutdown_poll_freq
        super().__init__(('', port), TestServer.RequestHandler)

    @dataclasses.dataclass
    class ResponseConfig:
        accepted_methods: Union[List[str], str]
        content_type: str
        content: bytes

        def accepts_method(self, method):
            if self.accepted_methods == 'all':
                return True
            return method.lower() in [accepted_method.lower() for accepted_method in self.accepted_methods]

        def add_data(self, handler):
            handler.send_header("Content-type", self.content_type)
            handler.end_headers()
            handler.wfile.write(self.content)

    class RequestHandler(BaseHTTPRequestHandler):
        server: 'TestServer'

        def do_GET(self):
            self.map_to_response("GET")

        def do_POST(self):
            self.map_to_response("POST")

        def do_PATCH(self):
            self.map_to_response("PATCH")

        def parse_and_extract(self):
            parsed_url = urllib.parse.urlparse(f"http://localhost:{self.server.server_port}{self.path}")
            url_qs = urllib.parse.parse_qs(parsed_url.query)
            if self.headers.get("content-type") is not None:
                content_type, post_dict = cgi.parse_header(self.headers.get('content-type'))
                if content_type == 'multipart/form-data':
                    length = int(self.headers.get('content-length'))
                    post_dict['CONTENT-LENGTH'] = length
                    post_dict['boundary'] = post_dict['boundary'].encode("utf-8")
                    content_qs = cgi.parse_multipart(self.rfile, post_dict)
                elif content_type in ['application/x-www-form-urlencoded', 'application/json']:
                    length = int(self.headers.get('content-length', 0))
                    read_data = self.rfile.read(length).decode('utf-8')
                    if read_data == "":
                        content_qs = {}
                    elif content_type == 'application/x-www-form-urlencoded':
                        content_qs = urllib.parse.parse_qs(self.rfile.read(length), keep_blank_values=True)
                    else:
                        content_qs = json.loads(read_data)
                else:
                    content_qs = {}
            else:
                content_qs = {}
                content_type = None
            return ParseAndExtractDataSummary(
                content_qs=content_qs,
                url_qs=url_qs,
                content_type=content_type,
                path=parsed_url.path
            )

        def map_to_response(self, method):
            try:
                if method == "GET" and self.path == "/debug-logs":
                    self.send_response(200)
                    self.add_debug_logs()
                    return
                if method == "GET" and self.path == "/healthcheck":
                    self.send_response(200)
                    self.add_healthcheck()
                    return
                if method == "GET" and self.path == "/teapot":
                    self.send_response(418)
                    self.add_teapot()
                    return
                parse_extract_summary = self.parse_and_extract()
                self.server.log(method, self.path, parse_extract_summary)
                if parse_extract_summary.path in self.server.response_map:
                    if callable(self.server.response_map[parse_extract_summary.path]):
                        response_value = self.server.response_map[parse_extract_summary.path](parse_extract_summary)
                    else:
                        response_value = self.server.response_map[parse_extract_summary.path]
                    if isinstance(response_value, TestServer.ResponseConfig):
                        if response_value.accepts_method(method):
                            self.send_response(200)
                        else:
                            self.send_response(405)
                            self.add_405()
                            return
                        response_value.add_data(self)
                    else:
                        self.send_response(200)
                        self.infer_type_and_add_data(response_value)
                        return
                else:
                    self.send_response(404)
                    self.add_404()
                    return
            except Exception as e:
                self.send_response(500)
                stacktrace = traceback.format_exc()
                print(stacktrace)
                self.infer_type_and_add_data({"exception": str(e), "stacktrace": stacktrace})

        def infer_type_and_add_data(self, response_value):
            if isinstance(response_value, dict):
                self.send_header("Content-type", "application/json")
                self.end_headers()
                data = json.dumps(response_value, default=default_encoder).encode('utf-8')
                self.wfile.write(data)
            elif isinstance(response_value, str):
                self.send_header("Content-type", "text/html")
                self.end_headers()
                data = response_value.encode('utf-8')
                self.wfile.write(data)
            else:
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                data = str(response_value).encode('utf-8')
                self.wfile.write(data)

        def add_debug_logs(self):
            results = list(itertools.starmap(
                lambda method, path, summary: {"method": method, "path": path, "summary": dataclasses.asdict(summary)},
                self.server.log_list
            ))
            self.send_header("Content-type", "application/json")
            self.end_headers()
            data = json.dumps(results, default=default_encoder).encode('utf-8')
            self.wfile.write(data)

        def add_404(self):
            self.send_header("Content-type", "application/json")
            self.end_headers()
            data = json.dumps({"error": "404 error path not configured"}, default=default_encoder).encode('utf-8')
            self.wfile.write(data)

        def add_405(self):
            self.send_header("Content-type", "application/json")
            self.end_headers()
            data = json.dumps({"error": "405 error method not supported"}, default=default_encoder).encode('utf-8')
            self.wfile.write(data)

        def add_healthcheck(self):
            self.send_header("Content-type", "application/json")
            self.end_headers()
            data = json.dumps({"healthy": "true"}, default=default_encoder).encode('utf-8')
            self.wfile.write(data)

        def add_teapot(self):
            self.send_header("Content-type", "application/json")
            self.end_headers()
            data = json.dumps({"my-status": "I'm a teapot"}, default=default_encoder).encode('utf-8')
            self.wfile.write(data)

    def log(self, method, path, summary: ParseAndExtractDataSummary):
        self.log_list.append((method, path, summary))
        path = pathlib.Path(self.log_dir)
        path.mkdir(exist_ok=True, parents=True)
        with open(path / "test_server_logs.log", "a+", encoding='utf8') as file:
            file.write(f"{method} {path}: {json.dumps(dataclasses.asdict(summary), default=default_encoder)}\n")

    @staticmethod
    def debug_logs(port):
        """
        Accesses debug logs of a test server running on a given port
        """
        logs = requests.get(f"http://localhost:{port}/debug-logs")
        return json.loads(logs.content)
