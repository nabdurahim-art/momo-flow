"""
momo_api.py
-----------
Plain-Python (http.server) REST API for MoMo SMS transactions.

Endpoints:
    GET    /transactions        -> list all transactions
    GET    /transactions/{id}   -> view one transaction
    POST   /transactions        -> create a transaction
    PUT    /transactions/{id}   -> update a transaction
    DELETE /transactions/{id}   -> delete a transaction

All endpoints require HTTP Basic Authentication.
Run:
    python3 momo_api.py
Then test with curl (see README.md / docs/api_docs.md for examples).
"""

import sys
import os
import json
import base64
import hmac
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "dsa"))
from xml_parser import parse_sms_xml, build_index  # noqa: E402

HOST = "0.0.0.0"
# Override with MOMO_API_PORT when 8000 is already taken (defaults to 8000).
PORT = int(os.environ.get("MOMO_API_PORT", "8000"))

# --- Hardcoded demo credentials -------------------------------------------
# NOTE: Basic Auth sends username:password base64-encoded on every request,
# not encrypted. This is fine for a class assignment over HTTPS/localhost,
# but see docs/api_docs.md for why it's weak in production and what to use
# instead (JWT / OAuth2).
VALID_USERNAME = "admin"
VALID_PASSWORD = "momo_secret123"

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "modified_sms_v2.xml")

# In-memory store: dict keyed by id is the source of truth (O(1) access).
# The server is threaded (ThreadingHTTPServer), so every read-modify-write on
# these two globals must happen while holding STORE_LOCK.
TRANSACTIONS = {}
NEXT_ID = 1
STORE_LOCK = threading.Lock()

# Fields that must be JSON numbers (matches DECIMAL columns in
# database/database_setup.sql).
MONEY_FIELDS = ("amount", "fee", "new_balance")


def type_errors(body):
    """Return human-readable messages for money fields that are not numbers."""
    errors = []
    for field in MONEY_FIELDS:
        if field in body:
            value = body[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errors.append(f"{field} must be a number, got {type(value).__name__}")
    return errors


def load_data():
    global TRANSACTIONS, NEXT_ID
    records = parse_sms_xml(DATA_PATH)
    index = build_index(records)
    skipped = len(records) - len(index)
    if skipped:
        print(f"Warning: skipped {skipped} record(s) with a missing or non-integer id")
    TRANSACTIONS = index
    NEXT_ID = (max(TRANSACTIONS) + 1) if TRANSACTIONS else 1


def check_auth(header_value):
    """Return True if the Authorization header holds valid Basic Auth credentials."""
    if not header_value or not header_value.startswith("Basic "):
        return False
    encoded = header_value.split(" ", 1)[1]
    try:
        decoded = base64.b64decode(encoded, validate=False).decode("utf-8")
        username, _, password = decoded.partition(":")
    except Exception:
        return False
    # compare_digest keeps the comparison constant-time (no timing leak).
    username_ok = hmac.compare_digest(username.encode(), VALID_USERNAME.encode())
    password_ok = hmac.compare_digest(password.encode(), VALID_PASSWORD.encode())
    return username_ok and password_ok


class MomoRequestHandler(BaseHTTPRequestHandler):

    # ---- helpers -----------------------------------------------------
    def _send_json(self, status_code, payload):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authenticated(self):
        if not check_auth(self.headers.get("Authorization")):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="MoMo API"')
            self.send_header("Content-Type", "application/json")
            body = json.dumps({"error": "Unauthorized. Valid Basic Auth credentials required."}).encode()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return False
        return True

    def _content_length(self):
        """Return the declared body length, or None once a 400 has been sent."""
        raw = self.headers.get("Content-Length")
        if raw is None:
            return 0
        try:
            length = int(raw)
        except ValueError:
            self._send_json(400, {"error": f"Invalid Content-Length header: {raw!r}"})
            return None
        if length < 0:
            self._send_json(400, {"error": "Content-Length must not be negative"})
            return None
        return length

    def _read_body(self):
        """Parse the request body as a JSON object.

        Returns a dict, or None if an error response has already been sent
        (malformed JSON, non-object body, or a bad Content-Length header).
        """
        length = self._content_length()
        if length is None:
            return None
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Malformed JSON body"})
            return None
        if not isinstance(body, dict):
            self._send_json(400, {"error": "JSON body must be an object"})
            return None
        return body

    def _parse_path(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        return parts  # e.g. ["transactions", "3"]

    # ---- HTTP verbs ----------------------------------------------------
    def do_GET(self):
        if not self._authenticated():
            return
        parts = self._parse_path()

        if parts == []:
            # Root URL: browsers prompt for credentials here, so hand back a
            # small index instead of a dead-end 404.
            self._send_json(200, {
                "name": "MoMo Transactions API",
                "endpoints": {
                    "GET /transactions": "list all transactions",
                    "GET /transactions/{id}": "view one transaction",
                    "POST /transactions": "create a transaction",
                    "PUT /transactions/{id}": "update a transaction",
                    "DELETE /transactions/{id}": "delete a transaction",
                },
                "hint": "Open /transactions to see the data. "
                        "Full documentation: docs/api_docs.md",
            })
            return

        if parts == ["transactions"]:
            with STORE_LOCK:
                snapshot = list(TRANSACTIONS.values())
            self._send_json(200, {"count": len(snapshot), "transactions": snapshot})
            return

        if len(parts) == 2 and parts[0] == "transactions":
            tx_id = self._to_id(parts[1])
            if tx_id is None:
                return
            with STORE_LOCK:
                record = TRANSACTIONS.get(tx_id)
                # Copy before releasing the lock: json.dumps(..., indent=2) runs
                # Python-level code and must not iterate a dict another thread
                # is updating.
                snapshot = dict(record) if record is not None else None
            if snapshot is None:
                self._send_json(404, {"error": f"Transaction {tx_id} not found"})
            else:
                self._send_json(200, snapshot)
            return

        self._send_json(404, {"error": "Not found"})
