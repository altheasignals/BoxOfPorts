"""IMEI import utilities for reading IMEI changes from files."""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Union

from .api_models import IMEIPortChange
from .ports import port_to_decimal, parse_port_spec


class IMEIImportError(Exception):
    """Error during IMEI file import."""
    pass


def import_imei_from_csv(file_path: Union[str, Path]) -> List[IMEIPortChange]:
    """Import IMEI changes from CSV file.
    
    Expected CSV format:
    port,imei
    1A,123456789012345
    2B,987654321098765
    
    Or with explicit slot:
    port,slot,imei
    1,1,123456789012345
    2,1,987654321098765
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of IMEIPortChange objects
        
    Raises:
        IMEIImportError: If file format is invalid
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise IMEIImportError(f"File not found: {file_path}")
    
    changes = []
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate headers
            if not reader.fieldnames:
                raise IMEIImportError("CSV file is empty or has no headers")
            
            required_fields = ['port', 'imei']
            missing_fields = [field for field in required_fields if field not in reader.fieldnames]
            if missing_fields:
                raise IMEIImportError(f"Missing required CSV columns: {missing_fields}")
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 for header row
                try:
                    port_str = row['port'].strip()
                    imei = row['imei'].strip()
                    slot = int(row.get('slot', '1').strip())
                    
                    # Convert port format if needed
                    port_num = _parse_port_to_number(port_str)
                    
                    change = IMEIPortChange(
                        port=port_num,
                        slot=slot,
                        imei=imei
                    )
                    changes.append(change)
                    
                except (ValueError, KeyError) as e:
                    raise IMEIImportError(f"Invalid data in row {row_num}: {e}")
    
    except csv.Error as e:
        raise IMEIImportError(f"CSV parsing error: {e}")
    except IOError as e:
        raise IMEIImportError(f"File reading error: {e}")
    
    if not changes:
        raise IMEIImportError("No valid IMEI changes found in file")
    
    return changes


def import_imei_from_json(file_path: Union[str, Path]) -> List[IMEIPortChange]:
    """Import IMEI changes from JSON file.
    
    Expected JSON format:
    [
        {"port": 1, "slot": 1, "imei": "123456789012345"},
        {"port": 2, "slot": 1, "imei": "987654321098765"}
    ]
    
    Or with string port identifiers:
    [
        {"port": "1A", "imei": "123456789012345"},
        {"port": "2B", "imei": "987654321098765"}
    ]
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of IMEIPortChange objects
        
    Raises:
        IMEIImportError: If file format is invalid
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise IMEIImportError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise IMEIImportError(f"Invalid JSON format: {e}")
    except IOError as e:
        raise IMEIImportError(f"File reading error: {e}")
    
    if not isinstance(data, list):
        raise IMEIImportError("JSON file must contain an array of IMEI changes")
    
    changes = []
    
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise IMEIImportError(f"Item {i} must be an object with port, slot, and imei fields")
        
        try:
            port_value = item.get('port')
            if port_value is None:
                raise ValueError("Missing 'port' field")
            
            imei = item.get('imei')
            if imei is None:
                raise ValueError("Missing 'imei' field")
            
            slot = item.get('slot', 1)
            
            # Convert port format if needed
            if isinstance(port_value, str):
                port_num = _parse_port_to_number(port_value)
            else:
                port_num = int(port_value)
            
            change = IMEIPortChange(
                port=port_num,
                slot=int(slot),
                imei=str(imei)
            )
            changes.append(change)
            
        except (ValueError, TypeError) as e:
            raise IMEIImportError(f"Invalid data in item {i}: {e}")
    
    if not changes:
        raise IMEIImportError("No valid IMEI changes found in file")
    
    return changes


def _parse_port_to_number(port_str: str) -> int:
    """Parse port string to port number.
    
    Examples:
        "1A" -> 1
        "2B" -> 2  
        "3.01" -> 3
        "4" -> 4
        
    Args:
        port_str: Port string identifier
        
    Returns:
        Port number (1-based)
        
    Raises:
        ValueError: If port format is invalid
    """
    port_str = port_str.strip()
    
    # Handle decimal format like "3.01"
    if '.' in port_str:
        parts = port_str.split('.')
        return int(parts[0])
    
    # Handle alpha format like "3A"
    import re
    match = re.match(r'^(\d+)([A-Z]?)$', port_str.upper())
    if match:
        return int(match.group(1))
    
    # Try parsing as plain number
    try:
        return int(port_str)
    except ValueError:
        pass
    
    raise ValueError(f"Invalid port format: {port_str}")


def export_imei_template_csv(file_path: Union[str, Path], ports: List[str] = None) -> None:
    """Export a CSV template for IMEI changes.
    
    Args:
        file_path: Output file path
        ports: Optional list of ports to include in template
    """
    file_path = Path(file_path)
    
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['port', 'imei', 'slot'])
        
        if ports:
            for port in ports:
                writer.writerow([port, '123456789012345', 1])
        else:
            # Default template with some example ports
            writer.writerow(['1A', '123456789012345', 1])
            writer.writerow(['2A', '987654321098765', 1])
            writer.writerow(['3A', '456789123456789', 1])


def validate_imei_changes(changes: List[IMEIPortChange]) -> List[str]:
    """Validate IMEI changes and return any warnings.
    
    Args:
        changes: List of IMEI changes to validate
        
    Returns:
        List of warning messages
    """
    warnings = []
    
    # Check for duplicate ports
    port_slots = set()
    for change in changes:
        port_slot = (change.port, change.slot)
        if port_slot in port_slots:
            warnings.append(f"Duplicate port/slot: {change.port}.{change.slot:02d}")
        port_slots.add(port_slot)
    
    # Check IMEI format (additional validation beyond pydantic)
    for change in changes:
        if not change.imei.isdigit():
            warnings.append(f"Port {change.port}: IMEI contains non-digit characters")
        elif len(set(change.imei)) == 1:
            warnings.append(f"Port {change.port}: IMEI appears to be a test pattern (all same digits)")
    
    # Check for reasonable port ranges
    for change in changes:
        if change.port > 64:
            warnings.append(f"Port {change.port} is unusually high (max typically 64)")
        if change.slot > 4:
            warnings.append(f"Port {change.port}: Slot {change.slot} is unusually high (max typically 4)")
    
    return warnings