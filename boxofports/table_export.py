"""
Table Export Utilities for BoxOfPorts CLI

These utilities help export table data to CSV and JSON formats.
Like ripples in still water, when there is no pebble tossed...
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.table import Table

console = Console()


def generate_export_filename(
    profile_name: Optional[str],
    command_name: str,
    file_format: str,
    custom_filename: Optional[str] = None
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
    data: List[Dict[str, Any]], 
    filename: str,
    fieldnames: Optional[List[str]] = None
) -> None:
    """
    Export table data to CSV format.
    
    Args:
        data: List of dictionaries representing table rows
        filename: Output filename
        fieldnames: Column names (optional, will be inferred from first row if not provided)
    """
    if not data:
        console.print(f"[yellow]No data to export to CSV[/yellow]")
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
    data: List[Dict[str, Any]], 
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
        console.print(f"[yellow]No data to export to JSON[/yellow]")
        return
    
    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=indent, ensure_ascii=False, default=str)
        
        console.print(f"[green]✓ JSON export written to: {filename}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to write JSON export: {e}[/red]")


def export_table_data_to_csv_console(
    data: List[Dict[str, Any]], 
    fieldnames: Optional[List[str]] = None
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
    data: List[Dict[str, Any]], 
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
    data: List[Dict[str, Any]],
    profile_name: Optional[str],
    command_name: str,
    csv_filename: Optional[str] = None,
    json_filename: Optional[str] = None,
    export_csv: bool = False,
    export_json: bool = False
) -> bool:
    """
    Handle exporting table data to CSV and/or JSON based on user options.
    
    This is the main function that should be called after displaying a table.
    
    Args:
        data: Table data as list of dictionaries
        profile_name: Current profile name
        command_name: Command identifier (e.g., 'inbox-list', 'sms-send')
        csv_filename: Custom CSV filename (optional)
        json_filename: Custom JSON filename (optional) 
        export_csv: Whether to export CSV
        export_json: Whether to export JSON
    
    Returns:
        bool: True if console-only output was used (suppresses other output)
    """
    if not (export_csv or export_json):
        return False
    
    if not data:
        if not (csv_filename == "" or json_filename == ""):
            console.print("[dim]No table data available for export[/dim]")
        return False
    
    console_only_output = False
    
    # Export CSV
    if export_csv:
        if csv_filename == "":
            # Console output for pipeline integration
            export_table_data_to_csv_console(data)
            console_only_output = True
        else:
            # File output
            csv_file = generate_export_filename(profile_name, command_name, 'csv', csv_filename)
            export_table_data_to_csv(data, csv_file)
    
    # Export JSON
    if export_json:
        if json_filename == "":
            # Console output for pipeline integration
            export_table_data_to_json_console(data)
            console_only_output = True
        else:
            # File output
            json_file = generate_export_filename(profile_name, command_name, 'json', json_filename)
            export_table_data_to_json(data, json_file)
    
    return console_only_output


def convert_rich_table_to_data(table: Table) -> List[Dict[str, Any]]:
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

def sms_tasks_to_export_data(tasks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Convert SMS task data to export format."""
    export_data = []
    for task in tasks:
        export_data.append({
            'TID': str(task.get('tid', '')),
            'Port': str(task.get('from', '')),
            'To': str(task.get('to', '')),
            'Text': str(task.get('sms', '')),
            'Status': 'PENDING'
        })
    return export_data


def sms_results_to_export_data(results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Convert SMS result data to export format."""
    export_data = []
    for result in results:
        export_data.append({
            'TID': str(result.get('tid', '')),
            'Status': str(result.get('status', ''))
        })
    return export_data


def imei_data_to_export_data(port_imeis: Dict[str, str]) -> List[Dict[str, str]]:
    """Convert IMEI data to export format."""
    export_data = []
    for port, imei in port_imeis.items():
        export_data.append({
            'Port': str(port),
            'IMEI': str(imei or 'Not available')
        })
    return export_data


def profiles_to_export_data(profiles_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Convert profile data to export format."""
    export_data = []
    for profile in profiles_data:
        export_data.append({
            'Name': str(profile.get('name', '')),
            'Host:Port': str(profile.get('host_port', '')),
            'Username': str(profile.get('username', '')),
            'Status': str(profile.get('status', ''))
        })
    return export_data


def messages_to_export_data(messages: List[Any], message_type: str = 'standard') -> List[Dict[str, str]]:
    """
    Convert message objects to export format.
    
    Args:
        messages: List of message objects
        message_type: Type of messages ('standard', 'delivery_reports', 'search', 'stop')
    """
    export_data = []
    
    for msg in messages:
        base_data = {
            'ID': str(msg.id),
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