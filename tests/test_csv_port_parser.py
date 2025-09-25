"""Tests for CSV port parsing functionality.

Every silver lining has a touch of grey - test the shadows and the light.
"""

import tempfile
import pytest
from pathlib import Path

from boxofports.csv_port_parser import (
    is_csv_file,
    parse_ports_from_csv,
    parse_imeis_from_csv,
    extract_port_and_slot,
    expand_csv_ports_if_needed,
    expand_csv_imeis_if_needed,
    CSVPortParseError,
)


class TestCSVDetection:
    """Test CSV file detection."""
    
    def test_csv_extension_detection(self):
        """Test detection of .csv files."""
        assert is_csv_file("ports.csv") is True
        assert is_csv_file("PORTS.CSV") is True
        assert is_csv_file("my_ports.csv") is True
    
    def test_non_csv_detection(self):
        """Test detection of non-CSV strings."""
        assert is_csv_file("1A,2B,3C") is False
        assert is_csv_file("1-4") is False
        assert is_csv_file("*") is False
        assert is_csv_file("") is False
        assert is_csv_file(None) is False


class TestPortExtraction:
    """Test port and slot extraction."""
    
    def test_alpha_format_extraction(self):
        """Test extraction from alpha format ports."""
        assert extract_port_and_slot("1A") == (1, 1)
        assert extract_port_and_slot("2B") == (2, 2)
        assert extract_port_and_slot("3C") == (3, 3)
        assert extract_port_and_slot("4D") == (4, 4)
    
    def test_decimal_format_extraction(self):
        """Test extraction from decimal format ports."""
        assert extract_port_and_slot("1.01") == (1, 1)
        assert extract_port_and_slot("2.02") == (2, 2)
        assert extract_port_and_slot("3.03") == (3, 3)
        assert extract_port_and_slot("4.04") == (4, 4)
    
    def test_numeric_only_extraction(self):
        """Test extraction from numeric-only ports (defaults to slot 1)."""
        assert extract_port_and_slot("1") == (1, 1)
        assert extract_port_and_slot("10") == (10, 1)
        assert extract_port_and_slot("32") == (32, 1)
    
    def test_invalid_port_format(self):
        """Test error handling for invalid port formats."""
        with pytest.raises(ValueError):
            extract_port_and_slot("invalid")
        with pytest.raises(ValueError):
            extract_port_and_slot("1E")  # Invalid slot letter
        with pytest.raises(ValueError):
            extract_port_and_slot("1.99")  # Invalid decimal slot


class TestCSVPortParsing:
    """Test CSV port parsing functionality."""
    
    def create_temp_csv(self, content: str) -> Path:
        """Create a temporary CSV file with given content."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write(content)
        temp_file.flush()
        return Path(temp_file.name)
    
    def test_ports_only_csv(self):
        """Test CSV with only port column."""
        csv_content = '''port
1A
2B
3.01
4'''
        csv_file = self.create_temp_csv(csv_content)
        
        try:
            ports = parse_ports_from_csv(csv_file)
            assert ports == ["1A", "2B", "3.01", "4A"]
        finally:
            csv_file.unlink()
    
    def test_ports_with_slots_csv(self):
        """Test CSV with port and slot columns."""
        csv_content = '''port,slot
1,A
2,B
3,01
4,02'''
        csv_file = self.create_temp_csv(csv_content)
        
        try:
            ports = parse_ports_from_csv(csv_file)
            assert ports == ["1A", "2B", "3.01", "4.02"]
        finally:
            csv_file.unlink()
    
    def test_mixed_slots_csv(self):
        """Test CSV with mixed slot formats."""
        csv_content = '''port,slot
1,A
2,
3,01
4,D'''
        csv_file = self.create_temp_csv(csv_content)
        
        try:
            ports = parse_ports_from_csv(csv_file)
            assert ports == ["1A", "2A", "3.01", "4D"]  # Empty slot defaults to A (slot 1)
        finally:
            csv_file.unlink()
    
    def test_missing_port_column(self):
        """Test error when port column is missing."""
        csv_content = '''slot,imei
A,123456789012345
B,987654321098765'''
        csv_file = self.create_temp_csv(csv_content)
        
        try:
            with pytest.raises(CSVPortParseError, match="must contain a 'port' column"):
                parse_ports_from_csv(csv_file)
        finally:
            csv_file.unlink()
    
    def test_empty_csv(self):
        """Test error with empty CSV."""
        csv_content = ''
        csv_file = self.create_temp_csv(csv_content)
        
        try:
            with pytest.raises(CSVPortParseError, match="empty or has no headers"):
                parse_ports_from_csv(csv_file)
        finally:
            csv_file.unlink()
    
    def test_duplicate_ports_removed(self):
        """Test that duplicate ports are removed while preserving order."""
        csv_content = '''port
1A
2B
1A
3C
2B'''
        csv_file = self.create_temp_csv(csv_content)
        
        try:
            ports = parse_ports_from_csv(csv_file)
            assert ports == ["1A", "2B", "3C"]  # Duplicates removed, order preserved
        finally:
            csv_file.unlink()


class TestCSVIMEIParsing:
    """Test CSV IMEI parsing functionality."""
    
    def create_temp_csv(self, content: str) -> Path:
        """Create a temporary CSV file with given content."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write(content)
        temp_file.flush()
        return Path(temp_file.name)
    
    def test_imei_only_csv(self):
        """Test CSV with only IMEI column."""
        csv_content = '''imei
123456789012345
987654321098765
111222333444555'''
        csv_file = self.create_temp_csv(csv_content)
        
        try:
            imeis = parse_imeis_from_csv(csv_file)
            assert imeis == ["123456789012345", "987654321098765", "111222333444555"]
        finally:
            csv_file.unlink()
    
    def test_missing_imei_column(self):
        """Test error when IMEI column is missing."""
        csv_content = '''port,slot
1A,1
2B,2'''
        csv_file = self.create_temp_csv(csv_content)
        
        try:
            with pytest.raises(CSVPortParseError, match="must contain an 'imei' column"):
                parse_imeis_from_csv(csv_file)
        finally:
            csv_file.unlink()


class TestExpansionFunctions:
    """Test high-level expansion functions."""
    
    def create_temp_csv(self, content: str) -> Path:
        """Create a temporary CSV file with given content."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write(content)
        temp_file.flush()
        return Path(temp_file.name)
    
    def test_expand_csv_ports_if_needed_with_csv(self):
        """Test expansion function with CSV file."""
        csv_content = '''port
1A
2B'''
        csv_file = self.create_temp_csv(csv_content)
        
        try:
            ports = expand_csv_ports_if_needed(str(csv_file))
            assert ports == ["1A", "2B"]
        finally:
            csv_file.unlink()
    
    def test_expand_csv_ports_if_needed_with_non_csv(self):
        """Test expansion function with non-CSV input."""
        result = expand_csv_ports_if_needed("1A,2B,3C")
        assert result is None  # Should return None for non-CSV input
    
    def test_expand_csv_imeis_if_needed_with_csv(self):
        """Test IMEI expansion function with CSV file."""
        csv_content = '''imei
123456789012345
987654321098765'''
        csv_file = self.create_temp_csv(csv_content)
        
        try:
            imeis = expand_csv_imeis_if_needed(str(csv_file))
            assert imeis == ["123456789012345", "987654321098765"]
        finally:
            csv_file.unlink()
    
    def test_expand_csv_imeis_if_needed_with_non_csv(self):
        """Test IMEI expansion function with non-CSV input."""
        result = expand_csv_imeis_if_needed("123456789012345,987654321098765")
        assert result is None  # Should return None for non-CSV input