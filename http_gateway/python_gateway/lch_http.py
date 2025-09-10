# encoding: utf-8
"""
Minimal Python 3.11+ HTTP service.

Endpoints
- GET  /health            -> 200 ok
- POST /lch_call          -> Accepts JSON: {"message": "..."}; clears result cache; enqueues message; 200
- GET  /lch_get_ret       -> If cached result exists, return it and clear cache; else 401
- POST /lch_set_ret       -> Accepts JSON: {"result": "..."}; sets cached result; 200

Run: python http_gateway/python_gateway/lch_http.py
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional, Tuple
from queue import Queue
import json
import sys
import threading

MORE_OUTPUT = False

# Thread-safe queue to hold incoming strings
message_queue: Queue[str] = Queue()
# Cached result string; set via /lch_set_ret, retrieved via /lch_get_ret
result_cache: Optional[str] = None

g_tick_id = -1  # type: int

def _parse_json_message(body_bytes: bytes) -> str:
	"""Parse request body as JSON and return the 'message' string.

	Raises ValueError if body is not valid JSON or schema is wrong.
	"""
	body_text = body_bytes.decode("utf-8", errors="replace")
	try:
		data = json.loads(body_text)
	except Exception as exc:
		raise ValueError(f"Invalid JSON: {exc}")

	if not isinstance(data, dict):
		raise ValueError("Expected JSON object with key 'message'")
	if "message" not in data:
		raise ValueError("Missing required key 'message'")
	if not isinstance(data["message"], str):
		raise ValueError("'message' must be a string")
	return data["message"]

def _parse_json_field(body_bytes: bytes, field: str) -> str:
	"""Parse request body as JSON and return the given string field."""
	body_text = body_bytes.decode("utf-8", errors="replace")
	try:
		data = json.loads(body_text)
	except Exception as exc:
		raise ValueError(f"Invalid JSON: {exc}")
	if not isinstance(data, dict):
		raise ValueError(f"Expected JSON object with key '{field}'")
	if field not in data:
		raise ValueError(f"Missing required key '{field}'")
	if not isinstance(data[field], str):
		raise ValueError(f"'{field}' must be a string")
	return data[field]


class LCHRequestHandler(BaseHTTPRequestHandler):
	server_version = "LCHHTTP/1.0"

	def do_GET(self):  # noqa: N802 (match BaseHTTPRequestHandler)
		if self.path == "/health":
			self._send_response(200, b"ok", content_type="text/plain; charset=utf-8")
			return
		if self.path == "/lch_get_ret":
			self._handle_get_result()
			return
		self._send_response(404, b"Not Found", content_type="text/plain; charset=utf-8")

	def do_POST(self):  # noqa: N802
		if self.path == "/lch_call":
			self._handle_post_call()
			return
		if self.path == "/lch_set_ret":
			self._handle_post_set_result()
			return
		self._send_response(404, b"Not Found", content_type="text/plain; charset=utf-8")

	# Helpers
	def _send_json(self, status: int, obj: dict):
		payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
		self._send_response(status, payload, content_type="application/json; charset=utf-8")

	def _send_response(self, status: int, payload: bytes, *, content_type: str):
		self.send_response(status)
		self.send_header("Content-Type", content_type)
		self.send_header("Content-Length", str(len(payload)))
		# Simple CORS to help local tools if needed; safe for localhost use
		self.send_header("Access-Control-Allow-Origin", "*")
		self.end_headers()
		if payload:
			self.wfile.write(payload)

	# Quiet noisy default logging; print concise info instead.
	def log_message(self, format: str, *args):  # noqa: A003 (shadow built-in)
		if not MORE_OUTPUT:
			return
		sys.stdout.write("[http] " + (format % args) + "\n")

	def _log_info(self, msg: str):
		if not MORE_OUTPUT:
			return
		sys.stdout.write(f"[queue] {msg}\n")

	# Route handlers
	def _handle_post_call(self):
		global result_cache
		content_length = int(self.headers.get("Content-Length", "0"))
		try:
			raw_body = self.rfile.read(content_length) if content_length > 0 else b""
			message = _parse_json_message(raw_body)
			# Clear the cached result when a new call arrives
			result_cache = None
			message_queue.put_nowait(message)
			self._send_json(200, {"status": "ok"})
			self._log_info(f"Enqueued message: {message!r}")
		except ValueError as ve:
			self._send_json(400, {"status": "error", "error": str(ve)})
		except Exception as exc:
			self._send_json(500, {"status": "error", "error": str(exc)})

	def _handle_post_set_result(self):
		global result_cache
		content_length = int(self.headers.get("Content-Length", "0"))
		try:
			raw_body = self.rfile.read(content_length) if content_length > 0 else b""
			res = _parse_json_field(raw_body, "result")
			result_cache = res
			self._send_json(200, {"status": "ok"})
		except ValueError as ve:
			self._send_json(400, {"status": "error", "error": str(ve)})
		except Exception as exc:
			self._send_json(500, {"status": "error", "error": str(exc)})

	def _handle_get_result(self):
		global result_cache
		if result_cache:
			payload = json.dumps({"status": "ok", "result": result_cache}, ensure_ascii=False).encode("utf-8")
			result_cache = None
			self._send_response(200, payload, content_type="application/json; charset=utf-8")
			return
		self._send_json(401, {"status": "no_result"})


def start_server(host: str = "127.0.0.1", port: int = 8000) -> Tuple[ThreadingHTTPServer, threading.Thread]:
	"""Start the HTTP server on a background thread (non-blocking).

	Returns (server, thread). Call stop_server(server) to shut it down.
	"""
	server = ThreadingHTTPServer((host, port), LCHRequestHandler)
	thread = threading.Thread(target=server.serve_forever, name="LCHHTTPServer", daemon=True)
	thread.start()
	print(f"HTTP server listening on http://{host}:{port} (POST /lch_call)")
	return server, thread


def stop_server(server: ThreadingHTTPServer):
	"""Stop a server started with start_server()."""
	try:
		server.shutdown()
	finally:
		server.server_close()


def get_message(timeout: Optional[float] = None) -> Optional[str]:
    """Get a message from the queue, or None if timeout occurs."""
    try:
        return message_queue.get(timeout=timeout)
    except Exception:
        return None


def tick_queue(debug_input_func):
    """Tick function to be called periodically to process the message queue."""
    msg = get_message(timeout=0.0)
    if msg is None:
        print("[queue] No message in queue")
        return
    debug_input_func(msg)
