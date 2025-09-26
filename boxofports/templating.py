"""Jinja2 templating system for SMS message templates."""

from datetime import UTC, datetime
from typing import Any

import jinja2


class SMSTemplateEngine:
    """Template engine for SMS messages with built-in variables and filters."""

    def __init__(self):
        """Initialize the template environment with custom filters."""
        self.env = jinja2.Environment(
            undefined=jinja2.StrictUndefined,  # Fail on undefined variables
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters
        self.env.filters.update({
            'phone': self._format_phone,
            'upper': lambda x: str(x).upper(),
            'lower': lambda x: str(x).lower(),
            'truncate': self._truncate,
            'pad_left': self._pad_left,
            'pad_right': self._pad_right,
        })

        # Register custom functions
        self.env.globals.update({
            'now': self._now,
            'utcnow': self._utcnow,
            'format_time': self._format_time,
        })

    def render(self, template_str: str, **variables) -> str:
        """
        Render a template with the given variables.
        
        Built-in variables available in templates:
        - port: Current port identifier (e.g., "1A", "2.02")
        - ts: Current UTC timestamp in ISO format
        - idx: Current iteration index (0-based)
        
        Args:
            template_str: Template string with Jinja2 syntax
            **variables: Additional template variables
            
        Returns:
            Rendered template string
            
        Raises:
            jinja2.TemplateError: If template rendering fails
        """
        try:
            template = self.env.from_string(template_str)
            return template.render(**variables)
        except jinja2.TemplateError as e:
            raise ValueError(f"Template rendering error: {e}") from e

    def render_for_port(self, template_str: str, port: str, idx: int = 0, **variables) -> str:
        """
        Render a template for a specific port with built-in variables.
        
        Args:
            template_str: Template string
            port: Port identifier
            idx: Iteration index
            **variables: Additional template variables
            
        Returns:
            Rendered template string
        """
        builtin_vars = {
            'port': port,
            'ts': datetime.now(UTC).isoformat().replace('+00:00', 'Z'),
            'idx': idx,
        }

        # User variables override built-ins if there's a conflict
        all_vars = {**builtin_vars, **variables}

        return self.render(template_str, **all_vars)

    def validate_template(self, template_str: str) -> tuple[bool, str]:
        """
        Validate a template without rendering it.
        
        Args:
            template_str: Template string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            self.env.from_string(template_str)
            return True, ""
        except jinja2.TemplateError as e:
            return False, str(e)

    # Custom filter functions
    def _format_phone(self, phone: str, format_type: str = 'international') -> str:
        """Format phone number."""
        if not phone:
            return phone

        # Remove all non-digit characters
        digits = ''.join(c for c in phone if c.isdigit())

        if format_type == 'international' and not digits.startswith('+'):
            return f"+{digits}"
        elif format_type == 'local' and digits.startswith('+'):
            return digits[1:]

        return digits

    def _truncate(self, text: str, length: int, end: str = '...') -> str:
        """Truncate text to specified length."""
        if len(text) <= length:
            return text
        return text[:length - len(end)] + end

    def _pad_left(self, text: str, width: int, fill_char: str = ' ') -> str:
        """Pad text on the left."""
        return str(text).rjust(width, fill_char)

    def _pad_right(self, text: str, width: int, fill_char: str = ' ') -> str:
        """Pad text on the right."""
        return str(text).ljust(width, fill_char)

    # Global functions
    def _now(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Get current local time."""
        return datetime.now().strftime(format_str)

    def _utcnow(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Get current UTC time."""
        return datetime.utcnow().strftime(format_str)

    def _format_time(self, timestamp: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format an ISO timestamp."""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime(format_str)
        except (ValueError, AttributeError):
            return timestamp


# Global template engine instance
template_engine = SMSTemplateEngine()


def render_sms_template(template: str, port: str, idx: int = 0, **variables) -> str:
    """
    Convenience function to render an SMS template.
    
    Examples:
        >>> render_sms_template("Hi from {{port}} at {{ts}}", "1A")
        "Hi from 1A at 2023-12-07T10:30:45Z"
        
        >>> render_sms_template("Test #{{idx + 1}}: {{message}}", "2B", 0, message="Hello")
        "Test #1: Hello"
    """
    return template_engine.render_for_port(template, port, idx, **variables)


def parse_template_variables(var_strings: list[str]) -> dict[str, str]:
    """
    Parse template variable strings in format 'key=value'.
    
    Args:
        var_strings: List of strings like ['name=John', 'age=25']
        
    Returns:
        Dictionary of template variables
        
    Raises:
        ValueError: If variable format is invalid
    """
    variables = {}

    for var_string in var_strings:
        if '=' not in var_string:
            raise ValueError(f"Invalid variable format '{var_string}'. Expected 'key=value'")

        key, value = var_string.split('=', 1)
        key = key.strip()
        value = value.strip()

        if not key:
            raise ValueError(f"Empty variable name in '{var_string}'")

        # Try to convert to appropriate type
        variables[key] = _convert_value(value)

    return variables


def _convert_value(value: str) -> Any:
    """Convert string value to appropriate type."""
    # Try boolean
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'

    # Try integer
    try:
        return int(value)
    except ValueError:
        pass

    # Try float
    try:
        return float(value)
    except ValueError:
        pass

    # Keep as string
    return value


# Template examples and documentation
TEMPLATE_EXAMPLES = {
    "basic": {
        "template": "Port {{port}} says hi at {{ts}}",
        "description": "Basic template with port and timestamp",
    },
    "with_index": {
        "template": "Message #{{idx + 1}} from {{port}}",
        "description": "Template with message index",
    },
    "with_variables": {
        "template": "Hello {{name}}, your balance is ${{balance|pad_left(8, '0')}}",
        "description": "Template with custom variables and filters",
        "variables": {"name": "John", "balance": 42.50},
    },
    "phone_formatting": {
        "template": "From {{port}}: Call {{phone|phone('international')}}",
        "description": "Template with phone number formatting",
        "variables": {"phone": "15551234567"},
    },
    "time_formatting": {
        "template": "Alert at {{now('%H:%M')}} from port {{port}}",
        "description": "Template with time formatting",
    },
    "conditional": {
        "template": "Port {{port}}{% if status == 'ok' %}: All good{% else %}: Error{{' - ' + error if error}}{% endif %}",
        "description": "Template with conditional content",
        "variables": {"status": "error", "error": "Connection failed"},
    },
}


def get_template_help() -> str:
    """Get help text for template usage."""
    help_text = """
SMS Template Help
=================

Built-in Variables:
  port    - Current port identifier (e.g., "1A", "2.02")
  ts      - Current UTC timestamp in ISO format
  idx     - Current iteration index (0-based)

Built-in Functions:
  now(format)     - Current local time (default: "%Y-%m-%d %H:%M:%S")
  utcnow(format)  - Current UTC time (default: "%Y-%m-%d %H:%M:%S")
  format_time(ts, format) - Format an ISO timestamp

Built-in Filters:
  phone(format)   - Format phone number ('international' or 'local')
  upper           - Convert to uppercase
  lower           - Convert to lowercase
  truncate(len)   - Truncate to specified length
  pad_left(width, char) - Pad on the left
  pad_right(width, char) - Pad on the right

Examples:
"""

    for name, example in TEMPLATE_EXAMPLES.items():
        help_text += f"\n{name.title()}:\n"
        help_text += f"  Template: {example['template']}\n"
        help_text += f"  Description: {example['description']}\n"
        if 'variables' in example:
            help_text += f"  Variables: {example['variables']}\n"

    return help_text
