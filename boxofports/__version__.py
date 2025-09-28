"""Version information for BoxOfPorts."""

__version__ = "1.2.11"
__title__ = "BoxOfPorts"
__command__ = "boxofports"
__description__ = "SMS Gateway Management CLI for EJOIN Router Operators"
__author__ = "Althea Signals Network LLC"
__author_email__ = "support@altheasignals.net"
__url__ = "https://altheasignals.net"
__license__ = "Proprietary"

# Build information
__build_date__ = "2025-01-26"
__api_version__ = "2.2"
__python_requires__ = ">=3.11"

# Design inspiration
__inspiration__ = "And it's just a box of ports. I don't know who put it there"

def get_version_info() -> dict:
    """Get comprehensive version information."""
    return {
        "version": __version__,
        "title": __title__,
        "command": __command__,
        "description": __description__,
        "author": __author__,
        "api_version": __api_version__,
        "build_date": __build_date__,
        "python_requires": __python_requires__,
        "license": __license__,
        "url": __url__,
    }

def get_version_string() -> str:
    """Get formatted version string for display."""
    return f"{__title__} v{__version__} (API v{__api_version__})"

def get_full_version_info() -> str:
    """Get full version information for --version output."""
    return f"""
{__title__} version {__version__}

{__description__}
Command: {__command__}
API Version: {__api_version__}
Build Date: {__build_date__}

Developed by: {__author__}
Website: {__url__}
License: {__license__}

Python Requirements: {__python_requires__}

Inspired by "{__inspiration__}"
Built for operators who know that connectivity flows like ripples in water.
""".strip()
