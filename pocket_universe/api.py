#!/usr/bin/env python3
"""Pocket Universe API — lightweight JSON server using stdlib (no external deps)."""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure the package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pocket_universe.generator import generate


class UniverseHandler(BaseHTTPRequestHandler):
    """HTTP handler serving pocket universe JSON over port 8080."""

    def _send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_404(self, message="Not found"):
        self._send_json({"error": message}, 404)

    def _send_400(self, message="Bad request"):
        self._send_json({"error": message}, 400)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/health":
            self._send_json({"status": "ok", "service": "pocket-universe-api"})
            return

        if path == "/generate" or path == "":
            query = parse_qs(parsed.query)
            seed = query.get("seed", [None])[0]

            if not seed:
                self._send_400("Missing 'seed' query parameter. Usage: /generate?seed=ember")
                return

            try:
                universe = generate(seed)
                self._send_json(universe)
            except Exception as e:
                self._send_500(f"Generation failed: {str(e)}")
            return

        if path == "/seeds":
            words = [
                "ember", "thaw", "drift", "cinder", "hollow", "veil",
                "fold", "knot", "pulse", "spark", "shard", "echo",
                "bloom", "rust", "salt", "tar", "lime", "frost",
                "dust", "flint", "mica", "resin", "silt", "brine",
                "char", "flux", "grit", "haze", "loam", "moss",
            ]
            self._send_json({"seeds": words})
            return

        self._send_404(f"No route for {path}")

    def _send_500(self, message="Internal error"):
        self._send_json({"error": message}, 500)

    def log_message(self, format, *args):
        print(f"[API] {args[0]} {args[1]} {args[2]}")


def main():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), UniverseHandler)
    print(f"[Pocket Universe API] Listening on http://0.0.0.0:{port}")
    print(f"[Pocket Universe API] Try: curl http://localhost:{port}/generate?seed=ember")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Pocket Universe API] Shutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
