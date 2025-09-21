"""Tests for port parsing utilities."""

import pytest

from boxofports.ports import (
    parse_port_spec,
    port_to_decimal,
    port_to_alpha,
    format_ports_for_api,
    PortParseError,
)


def test_parse_single_port():
    """Test parsing single port specifications."""
    assert parse_port_spec("1A") == ["1A"]
    assert parse_port_spec("2B") == ["2B"]
    assert parse_port_spec("1.01") == ["1.01"]
    assert parse_port_spec("32.04") == ["32.04"]


def test_parse_port_list():
    """Test parsing comma-separated port lists."""
    assert parse_port_spec("1A,2B,3C") == ["1A", "2B", "3C"]
    assert parse_port_spec("1.01,2.02") == ["1.01", "2.02"]


def test_parse_port_range():
    """Test parsing port ranges."""
    assert parse_port_spec("1A-1D") == ["1A", "1B", "1C", "1D"]
    assert parse_port_spec("1-3") == ["1A", "2A", "3A"]
    assert parse_port_spec("2.01-2.03") == ["2.01", "2.02", "2.03"]


def test_parse_mixed_port_spec():
    """Test parsing mixed port specifications."""
    result = parse_port_spec("1A,3B-3D,5.01")
    expected = ["1A", "3B", "3C", "3D", "5.01"]
    assert result == expected


def test_parse_invalid_port():
    """Test parsing invalid port specifications."""
    with pytest.raises(PortParseError):
        parse_port_spec("")
    
    with pytest.raises(PortParseError):
        parse_port_spec("1X")  # Invalid slot letter
    
    with pytest.raises(PortParseError):
        parse_port_spec("1A-2.01")  # Mixed range types


def test_port_conversions():
    """Test port format conversions."""
    # Alpha to decimal
    assert port_to_decimal("1A") == "1.01"
    assert port_to_decimal("2B") == "2.02"
    assert port_to_decimal("3C") == "3.03"
    assert port_to_decimal("4D") == "4.04"
    
    # Decimal to alpha
    assert port_to_alpha("1.01") == "1A"
    assert port_to_alpha("2.02") == "2B"
    assert port_to_alpha("3.03") == "3C"
    assert port_to_alpha("4.04") == "4D"
    
    # Already in correct format
    assert port_to_decimal("1.01") == "1.01"
    assert port_to_alpha("1A") == "1A"


def test_format_ports_for_api():
    """Test formatting ports for API consumption."""
    ports = ["1A", "2B", "3.03"]
    
    # Format as alpha
    assert format_ports_for_api(ports, "alpha") == "1A,2B,3C"
    
    # Format as decimal
    assert format_ports_for_api(ports, "decimal") == "1.01,2.02,3.03"


def test_port_deduplication():
    """Test that duplicate ports are removed."""
    result = parse_port_spec("1A,1A,2B,1A")
    assert result == ["1A", "2B"]


def test_numeric_port_default():
    """Test that numeric ports default to slot A."""
    assert parse_port_spec("5") == ["5A"]
    assert parse_port_spec("1,2") == ["1A", "2A"]