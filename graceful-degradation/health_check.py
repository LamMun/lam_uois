#!/usr/bin/env python3
"""
VSR Graceful Degradation Health Check

Pings a global external IP and flips app_config.json into LOCAL_ONLY mode
when international latency is too high.

Default behavior:
- Check every 10 seconds
- Threshold: 500 ms
- Timeout / packet loss = degraded connection
"""

import argparse
import json
import platform
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

DEFAULT_GLOBAL_IP = "8.8.8.8"
DEFAULT_THRESHOLD_MS = 500
DEFAULT_INTERVAL_SECONDS = 10
DEFAULT_CONFIG_FILE = "app_config.json"


def ping_once(ip: str, timeout_seconds: int = 5) -> Optional[int]:
    """Return latency in ms, or None if ping fails/times out."""
    system = platform.system().lower()

    if "windows" in system:
        cmd = ["ping", "-n", "1", "-w", str(timeout_seconds * 1000), ip]
    else:
        cmd = ["ping", "-c", "1", "-W", str(timeout_seconds), ip]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 2,
            check=False,
        )
    except Exception:
        return None

    output = result.stdout + result.stderr

    # Common Windows format: time=23ms or time<1ms
    match = re.search(r"time[=<]\s*(\d+(?:\.\d+)?)\s*ms", output, re.IGNORECASE)
    if match:
        return int(float(match.group(1)))

    # Common Linux/macOS format: time=23.4 ms
    match = re.search(r"time=\s*(\d+(?:\.\d+)?)\s*ms", output, re.IGNORECASE)
    if match:
        return int(float(match.group(1)))

    return None


def write_config(config_file: Path, local_only: bool, latency_ms: Optional[int], target_ip: str, threshold_ms: int) -> None:
    status = "local-only" if local_only else "normal"
    config = {
        "LOCAL_ONLY": local_only,
        "status": status,
        "last_latency_ms": latency_ms,
        "target_ip": target_ip,
        "threshold_ms": threshold_ms,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "reason": "latency too high or ping failed" if local_only else "latency normal",
    }

    config_file.write_text(json.dumps(config, indent=4), encoding="utf-8")
    print(f"[{config['updated_at']}] latency={latency_ms}ms | mode={status}")


def run_check(args: argparse.Namespace) -> None:
    config_file = Path(args.config)

    if args.simulate_latency is not None:
        latency = args.simulate_latency
    else:
        latency = ping_once(args.ip, args.timeout)

    local_only = latency is None or latency > args.threshold
    write_config(config_file, local_only, latency, args.ip, args.threshold)


def main() -> None:
    parser = argparse.ArgumentParser(description="VSR international latency circuit breaker")
    parser.add_argument("--ip", default=DEFAULT_GLOBAL_IP, help="Global IP to ping")
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD_MS, help="Latency threshold in ms")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SECONDS, help="Check interval in seconds")
    parser.add_argument("--config", default=DEFAULT_CONFIG_FILE, help="Path to app_config.json")
    parser.add_argument("--timeout", type=int, default=5, help="Ping timeout in seconds")
    parser.add_argument("--once", action="store_true", help="Run only one check")
    parser.add_argument("--simulate-latency", type=int, default=None, help="Demo mode: use a fake latency value in ms")
    args = parser.parse_args()

    if args.once:
        run_check(args)
        return

    print("Starting VSR international latency health-check...")
    print(f"Target IP: {args.ip} | threshold: {args.threshold} ms | interval: {args.interval} s")

    while True:
        run_check(args)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
