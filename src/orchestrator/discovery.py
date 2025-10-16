"""
mDNS discovery utilities to broadcast the orchestrator presence on the LAN.
"""

from __future__ import annotations

import ipaddress
import socket
from typing import Optional

try:
    from zeroconf import ServiceInfo, Zeroconf
except ImportError:  # pragma: no cover - optional dependency
    Zeroconf = None  # type: ignore
    ServiceInfo = None  # type: ignore

SERVICE_TYPE = "_sos._tcp.local."


def _local_ip() -> str:
    """Attempt to detect the primary LAN IP."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception:
        return "127.0.0.1"


def register_mdns_service(port: int) -> Optional[Zeroconf]:
    """
    Advertise the orchestrator service via mDNS/zeroconf.

    Returns the Zeroconf instance so callers can close() it on shutdown.
    """
    if Zeroconf is None or ServiceInfo is None:
        return None

    hostname = socket.gethostname()
    address = _local_ip()
    try:
        addr_bytes = ipaddress.ip_address(address).packed
    except ValueError:
        addr_bytes = socket.inet_aton("127.0.0.1")

    info = ServiceInfo(
        SERVICE_TYPE,
        f"{hostname}.{SERVICE_TYPE}",
        addresses=[addr_bytes],
        port=port,
        properties={"token": "available".encode()},
        server=f"{hostname}.local.",
    )
    zeroconf = Zeroconf()
    zeroconf.register_service(info)
    return zeroconf
