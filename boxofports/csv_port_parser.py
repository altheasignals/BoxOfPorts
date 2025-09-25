"""CSV port parsing utilities for BoxOfPorts.

When the music plays, the ports dance together in harmony.
This module handles reading port specifications from CSV files.
"""

import csv
import re
from pathlib import Path
from typing import List, Union, Optional


class CSVPortParseError(Exception):
    """Error parsing ports from CSV file."""
    pass


def is_csv_file(port_spec: str) -> bool:
    """Check if a port specification string is likely a CSV file path.
    
    Args:
        port_spec: Port specification string
        
    Returns:
        True if this looks like a CSV file path
    """
    if not port_spec or not isinstance(port_spec, str):
        return False
    
    port_spec = port_spec.strip()
    
    # Check for .csv extension
    if port_spec.lower().endswith('.csv'):
        return True
    
    # Check if it's a readable file path (without .csv extension)
    try:
        path = Path(port_spec)
        if path.exists() and path.is_file():
            # Try to peek at the first line to see if it looks like CSV
            with open(path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                # If it contains 'port' and either commas or appears to be a header
                if 'port' in first_line.lower() and (',' in first_line or len(first_line.split()) <= 3):
                    return True
    except (OSError, IOError, PermissionError):
        pass
    
    return False


def parse_ports_from_csv(file_path: Union[str, Path]) -> List[str]:
    """Parse port specifications from a CSV file.
    
    Expected CSV format:
    - Required column: 'port' 
    - Optional column: 'slot'
    
    Examples:
        Simple format (ports only):
        port
        1A
        2B
        3.01
        
        With slots:
        port,slot
        1,A
        2,B
        3,01
        
    The function combines port+slot when both are present:
    - Numeric slots: port "3", slot "01" -> "3.01"
    - Letter slots: port "1", slot "A" -> "1A"
    - If slot is empty/missing for a row, uses port as-is
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of formatted port strings
        
    Raises:
        CSVPortParseError: If file format is invalid or required columns are missing
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise CSVPortParseError(f"CSV file not found: {file_path}")
    
    ports = []
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate headers
            if not reader.fieldnames:
                raise CSVPortParseError("CSV file is empty or has no headers")
            
            # Check for required 'port' column (case-insensitive)
            port_column = None
            slot_column = None
            
            for field in reader.fieldnames:
                if field.lower() == 'port':
                    port_column = field
                elif field.lower() == 'slot':
                    slot_column = field
            
            if not port_column:
                raise CSVPortParseError("CSV file must contain a 'port' column")
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 for header row
                try:
                    port_value = row[port_column].strip()
                    if not port_value:
                        continue  # Skip empty rows
                    
                    # Get slot value if column exists
                    slot_value = None
                    if slot_column and row[slot_column] is not None and row[slot_column].strip():
                        slot_value = row[slot_column].strip()
                    
                    # Format the port specification
                    if slot_value:
                        formatted_port = _combine_port_and_slot(port_value, slot_value)
                    else:
                        formatted_port = _normalize_port_value(port_value)
                    
                    ports.append(formatted_port)
                    
                except (ValueError, KeyError) as e:
                    raise CSVPortParseError(f"Invalid data in row {row_num}: {e}")
    
    except csv.Error as e:
        raise CSVPortParseError(f"CSV parsing error: {e}")
    except IOError as e:
        raise CSVPortParseError(f"File reading error: {e}")
    
    if not ports:
        raise CSVPortParseError("No valid ports found in CSV file")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_ports = []
    for port in ports:
        if port not in seen:
            seen.add(port)
            unique_ports.append(port)
    
    return unique_ports


def _combine_port_and_slot(port_value: str, slot_value: str) -> str:
    """Combine port and slot values into a properly formatted port string.
    
    Args:
        port_value: Port number/identifier
        slot_value: Slot identifier
        
    Returns:
        Formatted port string
    """
    port_value = port_value.strip()
    slot_value = slot_value.strip().upper()
    
    # If slot is numeric (like "01", "1", "02"), use decimal format
    if slot_value.isdigit():
        slot_num = int(slot_value)
        return f"{port_value}.{slot_num:02d}"
    
    # If slot is a letter (like "A", "B"), use alpha format  
    elif len(slot_value) == 1 and slot_value in 'ABCD':
        return f"{port_value}{slot_value}"
    
    # If slot looks like a decimal part (like ".01"), combine directly
    elif slot_value.startswith('.'):
        return f"{port_value}{slot_value}"
    
    # Otherwise, assume it's already a complete format or use as suffix
    else:
        # Try to detect if it's a partial decimal
        if re.match(r'^\d{2}$', slot_value):  # Like "01", "02"
            return f"{port_value}.{slot_value}"
        else:
            return f"{port_value}{slot_value}"


def _normalize_port_value(port_value: str) -> str:
    """Normalize a port value from CSV.
    
    Args:
        port_value: Raw port value from CSV
        
    Returns:
        Normalized port string
    """
    port_value = port_value.strip().upper()
    
    # If it's already a complete port spec (like "1A", "2.01"), return as-is
    if re.match(r'^\d+[A-D]$', port_value) or re.match(r'^\d+\.\d+$', port_value):
        return port_value
    
    # If it's just a number, default to slot A
    if port_value.isdigit():
        return f"{port_value}A"
    
    # Return as-is for any other format
    return port_value


def parse_imeis_from_csv(file_path: Union[str, Path]) -> List[str]:
    """Parse IMEI values from a CSV file.
    
    Expected CSV format:
    - Required column: 'imei'
    - Optional columns: 'port', 'slot' (for validation/matching)
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of IMEI strings
        
    Raises:
        CSVPortParseError: If file format is invalid or required columns are missing
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise CSVPortParseError(f"CSV file not found: {file_path}")
    
    imeis = []
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate headers
            if not reader.fieldnames:
                raise CSVPortParseError("CSV file is empty or has no headers")
            
            # Check for required 'imei' column (case-insensitive)
            imei_column = None
            
            for field in reader.fieldnames:
                if field.lower() == 'imei':
                    imei_column = field
                    break
            
            if not imei_column:
                raise CSVPortParseError("CSV file must contain an 'imei' column")
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 for header row
                try:
                    imei_value = row[imei_column].strip()
                    if not imei_value:
                        continue  # Skip empty rows
                    
                    imeis.append(imei_value)
                    
                except (ValueError, KeyError) as e:
                    raise CSVPortParseError(f"Invalid data in row {row_num}: {e}")
    
    except csv.Error as e:
        raise CSVPortParseError(f"CSV parsing error: {e}")
    except IOError as e:
        raise CSVPortParseError(f"File reading error: {e}")
    
    if not imeis:
        raise CSVPortParseError("No valid IMEIs found in CSV file")
    
    return imeis


def expand_csv_ports_if_needed(port_spec: str) -> List[str]:
    """Expand port specification, checking for CSV files first.
    
    This function integrates CSV parsing with the existing port parsing system.
    If the port_spec looks like a CSV file, it will be parsed as such.
    Otherwise, returns None to indicate regular port parsing should be used.
    
    Args:
        port_spec: Port specification (could be CSV file or regular spec)
        
    Returns:
        List of port strings if CSV was parsed, None if regular parsing should be used
        
    Raises:
        CSVPortParseError: If CSV parsing fails
    """
    if is_csv_file(port_spec):
        return parse_ports_from_csv(port_spec)
    return None


def extract_port_and_slot(port_str: str) -> tuple[int, int]:
    """Extract port number and slot from a port string.
    
    Args:
        port_str: Port identifier like '1A', '2.03', '3B', etc.
        
    Returns:
        Tuple of (port_number, slot_number)
        
    Raises:
        ValueError: If port format is invalid
    """
    port_str = port_str.strip().upper()
    
    # Handle decimal format like "3.01", "2.02"
    if '.' in port_str:
        parts = port_str.split('.')
        if len(parts) == 2:
            try:
                port_num = int(parts[0])
                slot_num = int(parts[1])
                return (port_num, slot_num)
            except ValueError:
                pass
    
    # Handle alpha format like "1A", "2B", "3C", "4D"
    if len(port_str) >= 2 and port_str[-1] in 'ABCD':
        slot_letter = port_str[-1]
        port_part = port_str[:-1]
        try:
            port_num = int(port_part)
            slot_num = {'A': 1, 'B': 2, 'C': 3, 'D': 4}[slot_letter]
            return (port_num, slot_num)
        except (ValueError, KeyError):
            pass
    
    # If just a number, default to slot 1
    if port_str.isdigit():
        return (int(port_str), 1)
    
    raise ValueError(f"Invalid port format: {port_str}")


def expand_csv_imeis_if_needed(imei_spec: str) -> Optional[List[str]]:
    """Expand IMEI specification, checking for CSV files first.
    
    Args:
        imei_spec: IMEI specification (could be CSV file or comma-separated list)
        
    Returns:
        List of IMEI strings if CSV was parsed, None if regular parsing should be used
        
    Raises:
        CSVPortParseError: If CSV parsing fails
    """
    if is_csv_file(imei_spec):
        return parse_imeis_from_csv(imei_spec)
    return None
