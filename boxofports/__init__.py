"""
BoxOfPorts - SMS Gateway Management CLI for EJOIN Router Operators

A comprehensive command-line tool designed for SMS gateway operators managing
EJOIN multi-WAN routers. Built for the daily reality of managing dozens of
gateways with failing ports, SIM card swaps, and compliance monitoring.

Command: boxofports (local) / bop (Docker wrapper)
Like rain in a box, but for ports.

Developed by Althea Signals Network LLC
Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.

Features:
- SMS operations and inbox management
- STOP message compliance monitoring
- Device operations (lock/unlock ports)
- Profile management for multiple gateways
- Port specification parsing and automation
- Rich CLI output with tables and JSON export
"""

from .__version__ import (
    __version__,
    __author__,
    __author_email__ as __email__,
    __license__,
    # optional: other metadata you want public
)
__all__ = ["__version__", "__author__", "__email__", "__license__"]
