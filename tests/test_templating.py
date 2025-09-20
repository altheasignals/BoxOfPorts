"""Tests for SMS templating functionality."""

import pytest
from datetime import datetime

from ejoinctl.templating import SMSTemplateEngine
from jinja2 import TemplateError


@pytest.fixture
def template_engine():
    """Create a template engine instance for testing."""
    return SMSTemplateEngine()


def test_simple_template(template_engine):
    """Test simple variable substitution."""
    template = "Hello {{ name }}, your port is {{ port }}"
    
    result = template_engine.render(template, name="John", port="1A")
    assert result == "Hello John, your port is 1A"


def test_builtin_variables(template_engine):
    """Test built-in template variables with render_for_port."""
    template = "Port: {{ port }}, Index: {{ idx }}"
    
    result = template_engine.render_for_port(template, "2B", 5)
    assert "Port: 2B" in result
    assert "Index: 5" in result


def test_timestamp_variable(template_engine):
    """Test timestamp variable rendering with render_for_port."""
    template = "Sent at: {{ ts }}"
    
    result = template_engine.render_for_port(template, "1A")
    
    # Check that timestamp was generated (contains current year at least)
    current_year = str(datetime.now().year)
    assert current_year in result
    assert "Sent at:" in result


def test_timestamp_format_filter(template_engine):
    """Test timestamp formatting filter."""
    template = "Date: {{ timestamp | strftime('%Y-%m-%d') }}"
    
    result = template_engine.render(template, {})
    
    # Should contain current date in YYYY-MM-DD format
    current_date = datetime.now().strftime('%Y-%m-%d')
    assert f"Date: {current_date}" == result


def test_uppercase_filter(template_engine):
    """Test uppercase filter."""
    template = "Port {{ port | upper }} is active"
    variables = {"port": "1a"}
    
    result = template_engine.render(template, variables)
    assert result == "Port 1A is active"


def test_lowercase_filter(template_engine):
    """Test lowercase filter."""
    template = "Device {{ device | lower }} status"
    variables = {"device": "ROUTER"}
    
    result = template_engine.render(template, variables)
    assert result == "Device router status"


def test_capitalize_filter(template_engine):
    """Test capitalize filter."""
    template = "{{ message | capitalize }}"
    variables = {"message": "hello world"}
    
    result = template_engine.render(template, variables)
    assert result == "Hello world"


def test_title_filter(template_engine):
    """Test title filter."""
    template = "{{ message | title }}"
    variables = {"message": "hello world"}
    
    result = template_engine.render(template, variables)
    assert result == "Hello World"


def test_replace_filter(template_engine):
    """Test replace filter."""
    template = "{{ message | replace('old', 'new') }}"
    variables = {"message": "This is old text"}
    
    result = template_engine.render(template, variables)
    assert result == "This is new text"


def test_default_filter(template_engine):
    """Test default filter for missing values."""
    template = "Port: {{ missing_port | default('Unknown') }}"
    
    result = template_engine.render(template, {})
    assert result == "Port: Unknown"


def test_multiple_filters(template_engine):
    """Test chaining multiple filters."""
    template = "{{ message | lower | capitalize | replace('hello', 'hi') }}"
    variables = {"message": "HELLO WORLD"}
    
    result = template_engine.render(template, variables)
    assert result == "Hi world"


def test_conditional_rendering(template_engine):
    """Test conditional blocks in templates."""
    template = """{% if urgent %}URGENT: {% endif %}{{ message }}"""
    
    # With urgent flag
    result1 = template_engine.render(template, {"urgent": True, "message": "System alert"})
    assert result1 == "URGENT: System alert"
    
    # Without urgent flag
    result2 = template_engine.render(template, {"urgent": False, "message": "System alert"})
    assert result2 == "System alert"


def test_loop_rendering(template_engine):
    """Test loop rendering in templates."""
    template = """Ports: {% for port in ports %}{{ port }}{% if not loop.last %}, {% endif %}{% endfor %}"""
    variables = {"ports": ["1A", "2B", "3C"]}
    
    result = template_engine.render(template, variables)
    assert result == "Ports: 1A, 2B, 3C"


def test_missing_variable_error(template_engine):
    """Test error handling for missing variables."""
    template = "Hello {{ missing_name }}"
    
    with pytest.raises(TemplateError) as exc_info:
        template_engine.render(template, {})
    
    assert "missing_name" in str(exc_info.value)


def test_invalid_template_syntax(template_engine):
    """Test error handling for invalid template syntax."""
    template = "Hello {{ invalid syntax"
    
    with pytest.raises(TemplateError):
        template_engine.render(template, {})


def test_complex_template(template_engine):
    """Test a complex real-world template."""
    template = """
{% if urgent %}🚨 URGENT: {% endif %}Gateway Alert
Port: {{ port | upper }}
Status: {{ status | title }}
Time: {{ timestamp | strftime('%H:%M:%S') }}
{% if details %}
Details: {{ details }}
{% endif %}
Contact support if needed.
    """.strip()
    
    variables = {
        "urgent": True,
        "port": "1a",
        "status": "offline",
        "details": "Connection timeout"
    }
    
    result = template_engine.render(template, variables)
    
    assert "🚨 URGENT: Gateway Alert" in result
    assert "Port: 1A" in result
    assert "Status: Offline" in result
    assert "Details: Connection timeout" in result
    assert "Contact support if needed." in result


def test_whitespace_handling(template_engine):
    """Test template whitespace handling."""
    template = "{{ port }}-{{ status }}"
    variables = {"port": "1A", "status": "OK"}
    
    result = template_engine.render(template, variables)
    assert result == "1A-OK"


def test_numeric_variables(template_engine):
    """Test numeric variable handling."""
    template = "Signal: {{ signal_strength }}dBm ({{ percentage }}%)"
    variables = {"signal_strength": -75, "percentage": 85}
    
    result = template_engine.render(template, variables)
    assert result == "Signal: -75dBm (85%)"


def test_boolean_variables(template_engine):
    """Test boolean variable handling."""
    template = "Online: {{ is_online }}"
    
    result1 = template_engine.render(template, {"is_online": True})
    assert result1 == "Online: True"
    
    result2 = template_engine.render(template, {"is_online": False})
    assert result2 == "Online: False"


def test_none_values(template_engine):
    """Test handling of None values."""
    template = "Value: {{ value | default('N/A') }}"
    
    result = template_engine.render(template, {"value": None})
    assert result == "Value: N/A"


def test_empty_template(template_engine):
    """Test empty template handling."""
    template = ""
    
    result = template_engine.render(template, {})
    assert result == ""


def test_template_with_only_text(template_engine):
    """Test template with no variables."""
    template = "This is just plain text"
    
    result = template_engine.render(template, {})
    assert result == "This is just plain text"