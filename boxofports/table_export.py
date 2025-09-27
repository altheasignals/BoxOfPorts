"""
Table Export Utilities for BoxOfPorts CLI

These utilities help export table data to CSV and JSON formats.
Like ripples in still water, when there is no pebble tossed...
"""

import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Optional

from rich.console import Console
from rich.table import Table

console = Console()


# ============================================================================= 
# Sorting Infrastructure for Table Display and Export
# Like notes flowing from one chord to the next...
# =============================================================================

@dataclass
class ColumnSpec:
    """Specification for a table column with display and sorting metadata.
    
    Defines how data flows from raw values through display transformations
    to the final table, like water finding its natural course.
    """
    title: str
    key: str
    is_timestamp: bool = False
    is_port: bool = False
    style: Optional[str] = None
    display_transform: Optional[Callable[[Any], str]] = None
    export_transform: Optional[Callable[[Any], Any]] = None


@dataclass
class SortTerm:
    """A single sorting criterion - which column and which direction.
    
    Like the rhythm that keeps the band in time.
    """
    col_index: int  # 0-based index
    ascending: bool


def parse_sort_option(spec: Optional[str], columns: list[ColumnSpec]) -> list[SortTerm]:
    """Parse a sort specification into sort terms.
    
    Args:
        spec: Sort specification like "2,1d,4a" or None
        columns: Column specifications for validation
        
    Returns:
        List of sort terms, or default terms if spec is None/empty/invalid
        
    The spec flows like this: "2,1d,4a" means:
    - Sort by column 2 ascending (default)
    - Then by column 1 descending
    - Then by column 4 ascending
    """
    if not spec or not spec.strip():
        return default_sort_terms(columns)
    
    terms = []
    tokens = [token.strip() for token in spec.split(',') if token.strip()]
    
    for token in tokens:
        try:
            # Parse column number and direction
            if token.lower().endswith('d'):
                col_num = int(token[:-1])
                ascending = False
            elif token.lower().endswith('a'):
                col_num = int(token[:-1])
                ascending = True
            else:
                col_num = int(token)
                ascending = True  # Default to ascending
                
            # Convert to 0-based index and validate
            col_index = col_num - 1
            if 0 <= col_index < len(columns):
                terms.append(SortTerm(col_index=col_index, ascending=ascending))
            else:
                console.print(f"[dim]Ignoring invalid column number: {col_num}[/dim]")
                
        except ValueError:
            console.print(f"[dim]Ignoring invalid sort token: {token}[/dim]")
    
    # If no valid terms found, return defaults
    if not terms:
        return default_sort_terms(columns)
        
    return terms


def default_sort_terms(columns: list[ColumnSpec]) -> list[SortTerm]:
    """Determine default sort terms based on column characteristics.
    
    The natural order flows like this:
    1) Time's arrow - timestamp descending (most recent first)
    2) Port's path - port ascending (natural order)
    3) Second column ascending (often names or aliases)
    4) First column ascending (fallback)
    """
    # Look for timestamp columns first
    for i, col in enumerate(columns):
        if col.is_timestamp:
            return [SortTerm(col_index=i, ascending=False)]  # Timestamps descending
    
    # Look for port columns
    for i, col in enumerate(columns):
        if col.is_port:
            return [SortTerm(col_index=i, ascending=True)]   # Ports ascending
    
    # Default to second column if it exists, otherwise first column
    if len(columns) >= 2:
        return [SortTerm(col_index=1, ascending=True)]  # Second column ascending
    elif len(columns) >= 1:
        return [SortTerm(col_index=0, ascending=True)]  # First column ascending
    else:
        return []  # No columns to sort by


def coerce_timestamp(value: Any) -> Optional[datetime]:
    """Coerce a value to a datetime for sorting.
    
    Handles ISO format strings, epoch seconds, and other common formats.
    Returns None if the value cannot be parsed as a timestamp.
    """
    if isinstance(value, datetime):
        return value
        
    if not value:
        return None
        
    str_val = str(value).strip()
    if not str_val:
        return None
    
    # Try ISO format first
    try:
        return datetime.fromisoformat(str_val.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        pass
    
    # Try epoch seconds
    try:
        timestamp = float(str_val)
        if 1000000000 <= timestamp <= 9999999999:  # Reasonable epoch range
            return datetime.fromtimestamp(timestamp)
    except (ValueError, TypeError):
        pass
        
    # Try common date formats
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%m-%d %H:%M',
        '%Y-%m-%d',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(str_val, fmt)
        except (ValueError, TypeError):
            continue
            
    return None


def coerce_port(value: Any) -> tuple[int, int, str]:
    """Coerce a value to a port sorting key.
    
    Returns (board_num, slot_order, original_string) where:
    - board_num: Numeric board number (1, 2, 3, etc.)
    - slot_order: Slot order (A=1, B=2, C=3, D=4) 
    - original_string: Original value as string for tie-breaking
    
    Examples:
    - "1A" -> (1, 1, "1A")
    - "2B" -> (2, 2, "2B")
    - "10D" -> (10, 4, "10D")
    - "1A-1D" -> (1, 1, "1A-1D")  # Takes first port-like token
    """
    if not value:
        return (999999, 999999, str(value))  # Sort empty values last
        
    str_val = str(value).strip().upper()
    if not str_val:
        return (999999, 999999, str(value))
    
    # Look for port patterns like 1A, 2B, 10D, etc.
    # Also handles ranges like "1A-1D" by taking the first port
    port_pattern = r'(\d+)([ABCD])'
    match = re.search(port_pattern, str_val)
    
    if match:
        board_num = int(match.group(1))
        slot_letter = match.group(2)
        
        # Map slot letters to order
        slot_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
        slot_order = slot_map.get(slot_letter, 999)  # Unknown letters sort last
        
        return (board_num, slot_order, str_val)
    
    # Try to extract just numbers
    num_match = re.search(r'(\d+)', str_val)
    if num_match:
        board_num = int(num_match.group(1))
        return (board_num, 0, str_val)  # Numeric-only ports sort before lettered ones
        
    # Non-port values sort by string
    return (999999, 999999, str_val)


def coerce_generic(value: Any) -> tuple[int, Any]:
    """Coerce a value to a generic sorting key.
    
    Returns (priority, sort_value) where:
    - priority: 0 for real values, 1 for None/empty (keeps empties clustered)
    - sort_value: Numeric value if parseable, otherwise case-folded string
    """
    if value is None or value == '':
        return (1, '')  # Empty values sort last
        
    # Try to parse as number
    try:
        if isinstance(value, (int, float)):
            return (0, float(value))
        str_val = str(value).strip()
        if str_val:
            return (0, float(str_val))
    except (ValueError, TypeError):
        pass
    
    # Fall back to string comparison
    str_val = str(value).strip().casefold() if value else ''
    return (0, str_val)


def sort_rows(rows: list[dict], columns: list[ColumnSpec], terms: list[SortTerm]) -> list[dict]:
    """Sort table rows by multiple criteria.
    
    Uses stable sorting to preserve relative order of equal elements.
    Sorts from the last term to the first to achieve the correct precedence,
    like laying down tracks from the end back to the beginning.
    
    Args:
        rows: List of row dictionaries
        columns: Column specifications
        terms: Sort terms in order of precedence
        
    Returns:
        New list of sorted rows (original list is unchanged)
    """
    if not rows or not terms:
        return rows.copy()
    
    # Work on a copy to avoid modifying the original
    sorted_rows = rows.copy()
    
    # Apply sorts in reverse order for correct precedence
    # (Python's sort is stable, so later sorts take precedence)
    for term in reversed(terms):
        if term.col_index >= len(columns):
            continue
            
        col_spec = columns[term.col_index]
        
        def sort_key(row: dict) -> Any:
            value = row.get(col_spec.key)
            
            # Choose coercion based on column characteristics
            if col_spec.is_timestamp:
                coerced = coerce_timestamp(value)
                # For timestamps, None sorts last (oldest)
                return (1, datetime.min) if coerced is None else (0, coerced)
            elif col_spec.is_port:
                return coerce_port(value)
            else:
                return coerce_generic(value)
        
        sorted_rows.sort(key=sort_key, reverse=not term.ascending)
    
    return sorted_rows


# ============================================================================= 
# Column Specifications for Different Table Types
# Each table type has its own column mapping, like instruments in an orchestra
# =============================================================================

def get_sms_send_tasks_columns() -> list[ColumnSpec]:
    """Column specs for SMS send task preview tables."""
    return [
        ColumnSpec(
            title="TID", 
            key="TID", 
            style="cyan"
        ),
        ColumnSpec(
            title="Device Alias", 
            key="Device Alias", 
            style="magenta"
        ),
        ColumnSpec(
            title="Port", 
            key="Port", 
            is_port=True, 
            style="green"
        ),
        ColumnSpec(
            title="To", 
            key="To", 
            style="yellow"
        ),
        ColumnSpec(
            title="Text", 
            key="Text", 
            style="white",
            display_transform=lambda v: (v[:50] + "...") if isinstance(v, str) and len(v) > 50 else v
        ),
        ColumnSpec(
            title="Status", 
            key="Status", 
            style="blue"
        ),
    ]


def get_sms_send_results_columns() -> list[ColumnSpec]:
    """Column specs for SMS send results tables."""
    return [
        ColumnSpec(
            title="TID", 
            key="TID", 
            style="cyan"
        ),
        ColumnSpec(
            title="Device Alias", 
            key="Device Alias", 
            style="magenta"
        ),
        ColumnSpec(
            title="Status", 
            key="Status", 
            style="blue"
        ),
    ]


def get_imei_columns() -> list[ColumnSpec]:
    """Column specs for IMEI tables."""
    return [
        ColumnSpec(
            title="Device Alias", 
            key="Device Alias", 
            style="magenta"
        ),
        ColumnSpec(
            title="Port", 
            key="Port", 
            is_port=True, 
            style="cyan"
        ),
        ColumnSpec(
            title="IMEI", 
            key="IMEI", 
            style="green"
        ),
    ]


def get_profiles_columns() -> list[ColumnSpec]:
    """Column specs for profile configuration tables."""
    return [
        ColumnSpec(
            title="Name", 
            key="Name", 
            style="cyan"
        ),
        ColumnSpec(
            title="Device Alias", 
            key="Device Alias", 
            style="magenta"
        ),
        ColumnSpec(
            title="Host:Port", 
            key="Host:Port", 
            style="green"
        ),
        ColumnSpec(
            title="Username", 
            key="Username", 
            style="yellow"
        ),
        ColumnSpec(
            title="Status", 
            key="Status", 
            style="blue"
        ),
    ]


def get_inbox_messages_columns() -> list[ColumnSpec]:
    """Column specs for standard inbox message tables."""
    return [
        ColumnSpec(
            title="ID", 
            key="ID", 
            style="cyan"
        ),
        ColumnSpec(
            title="Device Alias", 
            key="Device Alias", 
            style="magenta"
        ),
        ColumnSpec(
            title="Type", 
            key="Type", 
            style="blue"
        ),
        ColumnSpec(
            title="Port", 
            key="Port", 
            is_port=True, 
            style="green"
        ),
        ColumnSpec(
            title="From", 
            key="From", 
            style="yellow"
        ),
        ColumnSpec(
            title="Time", 
            key="Time", 
            is_timestamp=True, 
            style="magenta"
        ),
        ColumnSpec(
            title="Content", 
            key="Content", 
            style="white"
        ),
    ]


def get_inbox_delivery_reports_columns() -> list[ColumnSpec]:
    """Column specs for delivery report tables."""
    return [
        ColumnSpec(
            title="ID", 
            key="ID", 
            style="cyan"
        ),
        ColumnSpec(
            title="Device Alias", 
            key="Device Alias", 
            style="magenta"
        ),
        ColumnSpec(
            title="Type", 
            key="Type", 
            style="blue"
        ),
        ColumnSpec(
            title="Port", 
            key="Port", 
            is_port=True, 
            style="green"
        ),
        ColumnSpec(
            title="Time", 
            key="Time", 
            is_timestamp=True, 
            style="magenta"
        ),
        ColumnSpec(
            title="To", 
            key="To", 
            style="cyan"
        ),
        ColumnSpec(
            title="Status", 
            key="Status", 
            style="white"
        ),
    ]


# ============================================================================= 
# Centralized Table Rendering and Export
# One function to rule them all, like a conductor leading the orchestra
# =============================================================================

def render_and_export_table(
    title: str,
    columns: list[ColumnSpec],
    rows: list[dict[str, Any]],
    profile_name: Optional[str],
    command_name: str,
    sort_option: Optional[str],
    csv_filename: Optional[str] = None,
    json_filename: Optional[str] = None,
    export_csv: bool = False,
    export_json: bool = False,
    table_console: Optional[Console] = None,
) -> bool:
    """Render a sorted table and handle exports in one unified flow.
    
    This function orchestrates the complete table workflow:
    1. Parse sort options and apply sorting
    2. Export to CSV/JSON if requested
    3. Render Rich table unless in console-only mode
    
    Args:
        title: Table title for display
        columns: Column specifications defining structure and behavior
        rows: Raw data rows (will be sorted)
        profile_name: Current profile (unused, kept for compatibility)
        command_name: Command identifier (unused, kept for compatibility)
        sort_option: Sort specification string (e.g. "2,1d,4a")
        csv_filename: Unused, kept for compatibility
        json_filename: Unused, kept for compatibility
        export_csv: Whether to export CSV to stdout
        export_json: Whether to export JSON to stdout
        table_console: Console for table output (uses module console if None)
        
    Returns:
        True if console-only export mode (suppresses other output)
        False if normal table display mode
        
    Like a river that flows through multiple channels, this function
    ensures consistent behavior across all table-producing commands.
    """
    if not rows:
        # Handle empty data case
        if export_csv or export_json:
            return handle_table_export(
                data=[],
                profile_name=profile_name,
                command_name=command_name,
                csv_filename=csv_filename,
                json_filename=json_filename,
                export_csv=export_csv,
                export_json=export_json
            )
        return False
    
    # Step 1: Parse sort options and sort the data
    sort_terms = parse_sort_option(sort_option, columns)
    sorted_rows = sort_rows(rows, columns, sort_terms)
    
    # Step 2: Handle exports (this might trigger console-only mode)
    console_only_mode = False
    if export_csv or export_json:
        console_only_mode = handle_table_export(
            data=sorted_rows,
            profile_name=profile_name,
            command_name=command_name,
            csv_filename=csv_filename,
            json_filename=json_filename,
            export_csv=export_csv,
            export_json=export_json
        )
    
    # Step 3: If console-only mode, skip table rendering
    if console_only_mode:
        return True
    
    # Step 4: Build and display Rich table
    display_console = table_console or console
    table = Table(title=title)
    
    # Add columns with their styling
    for col_spec in columns:
        table.add_column(
            col_spec.title,
            style=col_spec.style,
            width=None  # Let Rich auto-size
        )
    
    # Add rows with display transforms
    for row in sorted_rows:
        table_row = []
        for col_spec in columns:
            raw_value = row.get(col_spec.key, '')
            
            # Apply display transform if present
            if col_spec.display_transform:
                display_value = col_spec.display_transform(raw_value)
            else:
                display_value = str(raw_value) if raw_value is not None else ''
                
            table_row.append(display_value)
        
        table.add_row(*table_row)
    
    # Print the table
    display_console.print(table)
    return False


def generate_export_filename(
    profile_name: str | None,
    command_name: str,
    file_format: str,
    custom_filename: str | None = None
) -> str:
    """
    Generate a filename for export based on profile, command, and timestamp.
    
    Args:
        profile_name: Current profile name (can be None)
        command_name: The command being executed (e.g., 'inbox-list', 'config-list')
        file_format: File format ('csv' or 'json')
        custom_filename: User-specified filename (optional)
    
    Returns:
        Generated filename with proper extension
    """
    if custom_filename:
        # Ensure proper extension
        if not custom_filename.lower().endswith(f'.{file_format.lower()}'):
            return f"{custom_filename}.{file_format.lower()}"
        return custom_filename

    # Generate default filename: {profile_name}-{command}-{timestamp}.{format}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    profile_part = f"{profile_name}-" if profile_name else "default-"

    return f"{profile_part}{command_name}-{timestamp}.{file_format.lower()}"


def export_table_data_to_csv(
    data: list[dict[str, Any]],
    filename: str,
    fieldnames: list[str] | None = None
) -> None:
    """
    Export table data to CSV format.
    
    Args:
        data: List of dictionaries representing table rows
        filename: Output filename
        fieldnames: Column names (optional, will be inferred from first row if not provided)
    """
    if not data:
        console.print("[yellow]No data to export to CSV[/yellow]")
        return

    # Infer fieldnames from first row if not provided
    if not fieldnames:
        fieldnames = list(data[0].keys())

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        console.print(f"[green]✓ CSV export written to: {filename}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to write CSV export: {e}[/red]")


def export_table_data_to_json(
    data: list[dict[str, Any]],
    filename: str,
    indent: int = 2
) -> None:
    """
    Export table data to JSON format.
    
    Args:
        data: List of dictionaries representing table rows
        filename: Output filename
        indent: JSON indentation level
    """
    if not data:
        console.print("[yellow]No data to export to JSON[/yellow]")
        return

    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=indent, ensure_ascii=False, default=str)

        console.print(f"[green]✓ JSON export written to: {filename}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to write JSON export: {e}[/red]")


def export_table_data_to_csv_console(
    data: list[dict[str, Any]],
    fieldnames: list[str] | None = None
) -> None:
    """
    Export table data to CSV format directly to console (stdout) for pipeline integration.
    
    Args:
        data: List of dictionaries representing table rows
        fieldnames: Column names (optional, will be inferred from first row if not provided)
    """
    if not data:
        return

    # Infer fieldnames from first row if not provided
    if not fieldnames:
        fieldnames = list(data[0].keys())

    import sys
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)


def export_table_data_to_json_console(
    data: list[dict[str, Any]],
    indent: int = 2
) -> None:
    """
    Export table data to JSON format directly to console (stdout) for pipeline integration.
    
    Args:
        data: List of dictionaries representing table rows
        indent: JSON indentation level
    """
    if not data:
        return

    import sys
    json.dump(data, sys.stdout, indent=indent, ensure_ascii=False, default=str)


def handle_table_export(
    data: list[dict[str, Any]],
    profile_name: str | None,
    command_name: str,
    csv_filename: str | None = None,
    json_filename: str | None = None,
    export_csv: bool = False,
    export_json: bool = False
) -> bool:
    """
    Handle exporting table data to CSV and/or JSON to stdout.
    
    Args:
        data: Table data as list of dictionaries
        profile_name: Current profile name (unused, kept for compatibility)
        command_name: Command identifier (unused, kept for compatibility)
        csv_filename: Unused, kept for compatibility
        json_filename: Unused, kept for compatibility
        export_csv: Whether to export CSV to stdout
        export_json: Whether to export JSON to stdout
    
    Returns:
        bool: True if console-only output was used (suppresses other output)
    """
    if not (export_csv or export_json):
        return False

    if not data:
        if csv_filename is not None or json_filename is not None:
            console.print("[dim]No table data available for export[/dim]")
        return False

    console_only_output = False

    # Export CSV (always to console now)
    if export_csv:
        export_table_data_to_csv_console(data)
        console_only_output = True

    # Export JSON (always to console now) 
    if export_json:
        export_table_data_to_json_console(data)
        console_only_output = True

    return console_only_output


def convert_rich_table_to_data(table: Table) -> list[dict[str, Any]]:
    """
    Convert a Rich Table object to a list of dictionaries for export.
    
    Note: This is a helper function but Rich tables don't expose their data directly,
    so it's better to build the export data alongside the table creation.
    
    Args:
        table: Rich Table object
    
    Returns:
        List of dictionaries representing table data
    """
    # This is a placeholder - in practice, we'll build the export data
    # directly when creating tables rather than trying to extract it from Rich tables
    console.print("[yellow]⚠ Rich table conversion not implemented - build export data directly[/yellow]")
    return []


# Utility functions for common table data transformations

def sms_tasks_to_export_data(tasks: list[dict[str, Any]], device_alias: str = "") -> list[dict[str, str]]:
    """Convert SMS task data to export format."""
    export_data = []
    for task in tasks:
        export_data.append({
            'TID': str(task.get('tid', '')),
            'Device Alias': device_alias,
            'Port': str(task.get('from', '')),
            'To': str(task.get('to', '')),
            'Text': str(task.get('sms', '')),
            'Status': 'PENDING'
        })
    return export_data


def sms_results_to_export_data(results: list[dict[str, Any]], device_alias: str = "") -> list[dict[str, str]]:
    """Convert SMS result data to export format."""
    export_data = []
    for result in results:
        export_data.append({
            'TID': str(result.get('tid', '')),
            'Device Alias': device_alias,
            'Status': str(result.get('status', ''))
        })
    return export_data


def imei_data_to_export_data(port_imeis: dict[str, str], device_alias: str = "") -> list[dict[str, str]]:
    """Convert IMEI data to export format."""
    export_data = []
    for port, imei in port_imeis.items():
        export_data.append({
            'Device Alias': device_alias,
            'Port': str(port),
            'IMEI': str(imei or 'Not available')
        })
    return export_data


def profiles_to_export_data(profiles_data: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Convert profile data to export format."""
    export_data = []
    for profile in profiles_data:
        export_data.append({
            'Name': str(profile.get('name', '')),
            'Device Alias': str(profile.get('device_alias', '')),
            'Host:Port': str(profile.get('host_port', '')),
            'Username': str(profile.get('username', '')),
            'Status': str(profile.get('status', ''))
        })
    return export_data


def messages_to_export_data(messages: list[Any], message_type: str = 'standard', device_alias: str = "") -> list[dict[str, str]]:
    """
    Convert message objects to export format.
    
    Args:
        messages: List of message objects
        message_type: Type of messages ('standard', 'delivery_reports', 'search', 'stop')
        device_alias: Device alias to include in export data
    """
    export_data = []

    for msg in messages:
        base_data = {
            'ID': str(msg.id),
            'Device Alias': device_alias,
            'Type': msg.message_type.value if hasattr(msg, 'message_type') else 'unknown',
            'Port': str(msg.port),
            'From': str(msg.sender),
            'Time': msg.timestamp.isoformat() if hasattr(msg.timestamp, 'isoformat') else str(msg.timestamp),
        }

        if message_type == 'delivery_reports':
            # Special format for delivery reports
            base_data.update({
                'To': str(msg.delivery_phone_number or msg.recipient or 'N/A'),
                'Status': str(msg.delivery_status_code) if msg.delivery_status_code is not None else 'N/A'
            })
        else:
            # Standard format
            if hasattr(msg, 'is_delivery_report') and msg.is_delivery_report and msg.delivery_status_code is not None:
                content = f"Status: {msg.delivery_status_code} → {msg.delivery_phone_number or 'N/A'}"
            else:
                content = str(msg.content)

            base_data['Content'] = content

        export_data.append(base_data)

    return export_data
