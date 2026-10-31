"""Run independent local devices and expose their combined readiness on port 8098."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import signal
import subprocess
import sys
import threading
import urllib.request

from backend.emulators.devices import REGISTRY


def load_config(path, health_port):
    devices = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(devices, list) or not devices:
        raise ValueError("Fleet must contain at least one device")
    serials, ports = set(), {health_port}
    for device in devices:
        if device.get("family") not in REGISTRY:
            raise ValueError("Unknown device family")
        serial, port = device.get("serial"), device.get("port")
        if not isinstance(serial, str) or not serial or serial in serials:
            raise ValueError("Device serials must be nonempty and unique")
        if type(port) is not int or not 1024 <= port <= 65535 or port in ports:
            raise ValueError("Device ports must be unique and between 1024 and 65535")
        serials.add(serial)
        ports.add(port)
    return devices


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(Path(__file__).with_name("fleet.json")))
    parser.add_argument("--health-port", type=int, default=8098)
    parser.add_argument("--interval", type=float, default=1)
    args = parser.parse_args()
    if not 1024 <= args.health_port <= 65535 or not 0 < args.interval < float("inf"):
        parser.error("Use a valid health port and a finite positive interval")
    devices = load_config(args.config, args.health_port)
    stopped = threading.Event()
    children = []

    def request_stop(*_):
        stopped.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    def check(item):
        device, child = item
        result = dict(device, status="unhealthy")
        if child.poll() is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{device['port']}/state", timeout=2) as response:
                    state = json.load(response)
                if isinstance(state, dict) and state:
                    result["status"] = "healthy"
            except (OSError, ValueError):
                pass
        return result

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in ("/", "/health", "/devices"):
                self.send_error(404)
                return
            with ThreadPoolExecutor(max_workers=len(devices)) as pool:
                results = list(pool.map(check, list(children)))
            healthy = len(results) == len(devices) and all(d["status"] == "healthy" for d in results)
            body = json.dumps({"status": "healthy" if healthy else "unhealthy", "devices": results}).encode()
            self.send_response(200 if healthy else 503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("0.0.0.0", args.health_port), Handler)
    serving = False
    failed = False
    try:
        for device in devices:
            child = subprocess.Popen([
                sys.executable, "-m", "backend.emulators.main", device["family"],
                "--serial", device["serial"], "--port", str(device["port"]),
                "--interval", str(args.interval),
            ])
            children.append((device, child))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        serving = True
        print(f"Fleet started: {len(children)} devices; health port {args.health_port}", flush=True)
        while not stopped.wait(0.5):
            if any(child.poll() is not None for _, child in children):
                print("A device exited; stopping fleet so the container can restart", file=sys.stderr)
                failed = True
                break
    finally:
        if serving:
            server.shutdown()
        server.server_close()
        for _, child in children:
            if child.poll() is None:
                child.terminate()
        for _, child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
