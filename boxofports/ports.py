"""Port parsing utilities for EJOIN Multi-WAN Router."""

import re

from .csv_port_parser import CSVPortParseError, expand_csv_ports_if_needed
from .http import EjoinHTTPError


class PortParseError(EjoinHTTPError):
    """Error parsing port specification."""
    pass


def parse_port_spec(port_spec: str) -> list[str]:
    """
    Parse port specifications into individual port identifiers.
    
    Supported formats:
    - Single ports: "1A", "2B", "3C", "4D"
    - Decimal ports: "1.01", "2.02", "32.04"
    - Ranges: "1-4", "1A-4D", "2.01-2.04"
    - Lists: "1A,2B,3C"
    - Mixed: "1A,2B,4-8,10.01-10.04"
    - All ports: "*", "all"
    - CSV files: "ports.csv" (requires 'port' column, optional 'slot' column)
    
    Args:
        port_spec: Port specification string or CSV file path
        
    Returns:
        List of individual port identifiers
        
    Raises:
        PortParseError: If port specification is invalid
    """
    if not port_spec or not port_spec.strip():
        raise PortParseError("Empty port specification")

    # Check if it's a CSV file first
    try:
        csv_ports = expand_csv_ports_if_needed(port_spec)
        if csv_ports is not None:
            return csv_ports
    except CSVPortParseError as e:
        raise PortParseError(f"CSV parsing failed: {e}") from e

    port_spec = port_spec.strip()

    # Handle special cases
    if port_spec.lower() in ("all", "*"):
        # Return all possible ports (this is a placeholder - in real usage
        # we'd need to query the device for available ports)
        return [f"{i}A" for i in range(1, 33)]

    ports = []
    parts = [part.strip() for part in port_spec.split(",")]

    for part in parts:
        if not part:
            continue

        try:
            if "-" in part and not part.startswith("-") and not part.endswith("-"):
                # Range specification
                ports.extend(_parse_port_range(part))
            else:
                # Single port
                ports.append(_normalize_port(part))
        except Exception as e:
            raise PortParseError(f"Invalid port specification '{part}': {e}") from e

    if not ports:
        raise PortParseError("No valid ports found in specification")

    # Remove duplicates while preserving order
    seen = set()
    unique_ports = []
    for port in ports:
        if port not in seen:
            seen.add(port)
            unique_ports.append(port)

    return unique_ports


def _parse_port_range(range_spec: str) -> list[str]:
    """Parse a port range specification like '1A-4D' or '2.01-2.04'."""
    start_str, end_str = range_spec.split("-", 1)
    start_str = start_str.strip()
    end_str = end_str.strip()

    # Detect format type
    if "." in start_str or "." in end_str:
        return _parse_decimal_range(start_str, end_str)
    else:
        return _parse_alpha_range(start_str, end_str)


def _parse_decimal_range(start_str: str, end_str: str) -> list[str]:
    """Parse decimal format range like '2.01-2.04'."""
    start_match = re.match(r"^(\d+)\.(\d+)$", start_str)
    end_match = re.match(r"^(\d+)\.(\d+)$", end_str)

    if not start_match or not end_match:
        raise PortParseError(f"Invalid decimal port range format: {start_str}-{end_str}")

    start_port = int(start_match.group(1))
    start_slot = int(start_match.group(2))
    end_port = int(end_match.group(1))
    end_slot = int(end_match.group(2))

    if start_port != end_port:
        raise PortParseError("Decimal range must be within the same port number")

    if start_slot > end_slot:
        raise PortParseError("Invalid range: start slot must be <= end slot")

    return [f"{start_port}.{slot:02d}" for slot in range(start_slot, end_slot + 1)]


def _parse_alpha_range(start_str: str, end_str: str) -> list[str]:
    """Parse alpha format range like '1A-4D' or '1-4'."""
    # Handle pure numeric range like "1-4"
    if start_str.isdigit() and end_str.isdigit():
        start_num = int(start_str)
        end_num = int(end_str)
        if start_num > end_num:
            raise PortParseError("Invalid range: start must be <= end")
        return [f"{i}A" for i in range(start_num, end_num + 1)]

    # Handle alphanumeric format like "1A-4D"
    start_match = re.match(r"^(\d+)([A-D])$", start_str)
    end_match = re.match(r"^(\d+)([A-D])$", end_str)

    if not start_match or not end_match:
        raise PortParseError(f"Invalid alpha port range format: {start_str}-{end_str}")

    start_port = int(start_match.group(1))
    start_slot = start_match.group(2)
    end_port = int(end_match.group(1))
    end_slot = end_match.group(2)

    ports = []
    slot_order = ["A", "B", "C", "D"]

    for port_num in range(start_port, end_port + 1):
        if port_num == start_port and port_num == end_port:
            # Same port, range within slots
            start_idx = slot_order.index(start_slot)
            end_idx = slot_order.index(end_slot)
            for slot_idx in range(start_idx, end_idx + 1):
                ports.append(f"{port_num}{slot_order[slot_idx]}")
        elif port_num == start_port:
            # First port, start from specified slot
            start_idx = slot_order.index(start_slot)
            for slot_idx in range(start_idx, len(slot_order)):
                ports.append(f"{port_num}{slot_order[slot_idx]}")
        elif port_num == end_port:
            # Last port, end at specified slot
            end_idx = slot_order.index(end_slot)
            for slot_idx in range(0, end_idx + 1):
                ports.append(f"{port_num}{slot_order[slot_idx]}")
        else:
            # Middle ports, include all slots
            for slot in slot_order:
                ports.append(f"{port_num}{slot}")

    return ports


def _normalize_port(port_str: str) -> str:
    """Normalize a single port identifier."""
    port_str = port_str.strip().upper()

    # Decimal format (e.g., "1.01", "2.02")
    if re.match(r"^\d+\.\d+$", port_str):
        return port_str

    # Alpha format (e.g., "1A", "2B")
    if re.match(r"^\d+[A-D]$", port_str):
        return port_str

    # Pure numeric - default to slot A
    if port_str.isdigit():
        return f"{port_str}A"

    raise PortParseError(f"Unrecognized port format: {port_str}")


def port_to_decimal(port: str) -> str:
    """
    Convert port identifier to decimal format used by some API endpoints.
    
    Examples:
        "1A" -> "1.01"
        "2B" -> "2.02"
        "3C" -> "3.03"
        "4D" -> "4.04"
        "1.01" -> "1.01" (already decimal)
    """
    if "." in port:
        return port  # Already in decimal format

    match = re.match(r"^(\d+)([A-D])$", port.upper())
    if not match:
        raise PortParseError(f"Cannot convert port to decimal format: {port}")

    port_num = match.group(1)
    slot_letter = match.group(2)
    slot_num = {"A": "01", "B": "02", "C": "03", "D": "04"}[slot_letter]

    return f"{port_num}.{slot_num}"


def port_to_alpha(port: str) -> str:
    """
    Convert port identifier to alpha format.
    
    Examples:
        "1.01" -> "1A"
        "2.02" -> "2B" 
        "3.03" -> "3C"
        "4.04" -> "4D"
        "1A" -> "1A" (already alpha)
    """
    if "." not in port:
        return port.upper()  # Already in alpha format

    match = re.match(r"^(\d+)\.(\d+)$", port)
    if not match:
        raise PortParseError(f"Cannot convert port to alpha format: {port}")

    port_num = match.group(1)
    slot_num = match.group(2)
    slot_letter = {"01": "A", "02": "B", "03": "C", "04": "D"}.get(slot_num)

    if not slot_letter:
        raise PortParseError(f"Invalid slot number in port: {port}")

    return f"{port_num}{slot_letter}"


def format_ports_for_api(ports: list[str], format_type: str = "alpha") -> str:
    """
    Format a list of ports for API consumption.
    
    Args:
        ports: List of port identifiers
        format_type: "alpha" for 1A format, "decimal" for 1.01 format
        
    Returns:
        Comma-separated string of formatted ports
    """
    if format_type == "decimal":
        formatted = [port_to_decimal(port) for port in ports]
    else:
        formatted = [port_to_alpha(port) for port in ports]

    return ",".join(formatted)


def expand_ports(port_spec: str) -> list[str]:
    """Convenience function to parse and expand port specifications."""
    return parse_port_spec(port_spec)
