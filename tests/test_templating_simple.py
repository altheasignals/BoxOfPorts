"""Simple tests for SMS templating functionality."""

import pytest
from boxofports.templating import render_sms_template


def test_basic_render():
    """Test basic template rendering."""
    engine = SMSTemplateEngine()
    result = engine.render("Hello {{ name }}", name="World")
    assert result == "Hello World"


def test_render_for_port():
    """Test render_for_port with built-in variables."""
    engine = SMSTemplateEngine()
    result = engine.render_for_port("Port: {{ port }}, Index: {{ idx }}", "1A", 5)
    assert "Port: 1A" in result
    assert "Index: 5" in result
    
    # Test timestamp variable separately
    result_with_ts = engine.render_for_port("Time: {{ ts }}", "1A")
    assert "Z" in result_with_ts  # Should contain timestamp with 'Z' suffix


def test_validate_template():
    """Test template validation."""
    engine = SMSTemplateEngine()
    
    # Valid template
    is_valid, error = engine.validate_template("Hello {{ name }}")
    assert is_valid
    assert error == ""
    
    # Invalid template
    is_valid, error = engine.validate_template("Hello {{ invalid")
    assert not is_valid
    assert error != ""


def test_custom_filters():
    """Test custom filters."""
    engine = SMSTemplateEngine()
    
    # Test upper filter
    result = engine.render("{{ text | upper }}", text="hello")
    assert result == "HELLO"
    
    # Test lower filter
    result = engine.render("{{ text | lower }}", text="HELLO")
    assert result == "hello"
    
    # Test truncate filter
    result = engine.render("{{ text | truncate(5) }}", text="Hello World")
    assert len(result) == 5
    assert result.endswith("...")


def test_phone_filter():
    """Test phone formatting filter."""
    engine = SMSTemplateEngine()
    
    # Test international format
    result = engine.render("{{ number | phone('international') }}", number="1234567890")
    assert result == "+1234567890"
    
    # Test local format
    result = engine.render("{{ number | phone('local') }}", number="+1234567890")
    assert result == "1234567890"