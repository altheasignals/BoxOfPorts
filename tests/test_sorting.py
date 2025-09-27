"""
Unit tests for sorting utilities and type coercion in table_export.py

Also validates help text consistency for --sort, --csv, and --json options
across all table-producing commands.
"""
import pytest
import re
from datetime import datetime
from boxofports.table_export import (
    ColumnSpec, SortTerm,
    parse_sort_option, default_sort_terms,
    coerce_timestamp, coerce_port, coerce_generic,
    sort_rows
)


class TestColumnSpec:
    """Test ColumnSpec data structure."""
    
    def test_basic_column_spec(self):
        """Test creating basic column specifications."""
        col = ColumnSpec(title="Test", key="test_key")
        assert col.title == "Test"
        assert col.key == "test_key"
        assert col.is_timestamp is False
        assert col.is_port is False
        assert col.style is None
        assert col.display_transform is None
        assert col.export_transform is None
    
    def test_column_spec_with_flags(self):
        """Test column specs with timestamp and port flags."""
        timestamp_col = ColumnSpec(title="Time", key="time", is_timestamp=True)
        port_col = ColumnSpec(title="Port", key="port", is_port=True)
        
        assert timestamp_col.is_timestamp
        assert not timestamp_col.is_port
        assert port_col.is_port
        assert not port_col.is_timestamp


class TestSortTerm:
    """Test SortTerm data structure."""
    
    def test_sort_term_creation(self):
        """Test creating sort terms."""
        term = SortTerm(col_index=2, ascending=True)
        assert term.col_index == 2
        assert term.ascending is True
        
        term_desc = SortTerm(col_index=0, ascending=False)
        assert term_desc.col_index == 0
        assert term_desc.ascending is False


class TestParseSortOption:
    """Test parsing sort option strings into sort terms."""
    
    def get_test_columns(self):
        """Helper to create test column specifications."""
        return [
            ColumnSpec(title="ID", key="id"),
            ColumnSpec(title="Name", key="name"),
            ColumnSpec(title="Port", key="port", is_port=True),
            ColumnSpec(title="Time", key="time", is_timestamp=True),
            ColumnSpec(title="Status", key="status")
        ]
    
    def test_parse_none_returns_defaults(self):
        """Test that None input returns default sort terms."""
        columns = self.get_test_columns()
        terms = parse_sort_option(None, columns)
        
        # Should pick first timestamp column (index 3) descending
        assert len(terms) == 1
        assert terms[0].col_index == 3
        assert terms[0].ascending is False
    
    def test_parse_empty_returns_defaults(self):
        """Test that empty string returns default sort terms."""
        columns = self.get_test_columns()
        terms = parse_sort_option("", columns)
        
        # Should pick first timestamp column (index 3) descending
        assert len(terms) == 1
        assert terms[0].col_index == 3
        assert terms[0].ascending is False
    
    def test_parse_simple_column_numbers(self):
        """Test parsing simple column numbers without direction."""
        columns = self.get_test_columns()
        terms = parse_sort_option("2,1,4", columns)
        
        assert len(terms) == 3
        assert terms[0].col_index == 1  # Column 2 (1-based) -> index 1
        assert terms[0].ascending is True  # Default
        assert terms[1].col_index == 0  # Column 1 -> index 0
        assert terms[1].ascending is True
        assert terms[2].col_index == 3  # Column 4 -> index 3
        assert terms[2].ascending is True
    
    def test_parse_with_directions(self):
        """Test parsing column numbers with explicit directions."""
        columns = self.get_test_columns()
        terms = parse_sort_option("2d,1a,4d", columns)
        
        assert len(terms) == 3
        assert terms[0].col_index == 1  # Column 2
        assert terms[0].ascending is False  # Descending
        assert terms[1].col_index == 0  # Column 1
        assert terms[1].ascending is True   # Ascending
        assert terms[2].col_index == 3  # Column 4
        assert terms[2].ascending is False  # Descending
    
    def test_parse_mixed_case_directions(self):
        """Test parsing with mixed case direction markers."""
        columns = self.get_test_columns()
        terms = parse_sort_option("2D,1A,4d", columns)
        
        assert len(terms) == 3
        assert terms[0].col_index == 1
        assert terms[0].ascending is False
        assert terms[1].col_index == 0
        assert terms[1].ascending is True
        assert terms[2].col_index == 3
        assert terms[2].ascending is False
    
    def test_parse_ignores_invalid_tokens(self):
        """Test that invalid tokens are ignored gracefully."""
        columns = self.get_test_columns()
        terms = parse_sort_option("2,invalid,99,1d,badtoken", columns)
        
        # Should only get valid column numbers (2 and 1d)
        assert len(terms) == 2
        assert terms[0].col_index == 1  # Column 2
        assert terms[0].ascending is True
        assert terms[1].col_index == 0  # Column 1
        assert terms[1].ascending is False
    
    def test_parse_all_invalid_returns_defaults(self):
        """Test that all invalid tokens returns default terms."""
        columns = self.get_test_columns()
        terms = parse_sort_option("invalid,99,badtoken", columns)
        
        # Should fall back to default (timestamp descending)
        assert len(terms) == 1
        assert terms[0].col_index == 3
        assert terms[0].ascending is False
    
    def test_parse_whitespace_tolerance(self):
        """Test that parser handles whitespace gracefully."""
        columns = self.get_test_columns()
        terms = parse_sort_option("  2d , 1a , 4  ", columns)
        
        assert len(terms) == 3
        assert terms[0].col_index == 1
        assert terms[0].ascending is False
        assert terms[1].col_index == 0
        assert terms[1].ascending is True
        assert terms[2].col_index == 3
        assert terms[2].ascending is True


class TestDefaultSortTerms:
    """Test default sort term selection logic."""
    
    def test_defaults_to_first_timestamp_descending(self):
        """Test that first timestamp column is preferred, descending."""
        columns = [
            ColumnSpec(title="ID", key="id"),
            ColumnSpec(title="Name", key="name"),
            ColumnSpec(title="Created", key="created", is_timestamp=True),
            ColumnSpec(title="Updated", key="updated", is_timestamp=True),  # Second timestamp
            ColumnSpec(title="Port", key="port", is_port=True)
        ]
        
        terms = default_sort_terms(columns)
        assert len(terms) == 1
        assert terms[0].col_index == 2  # First timestamp column
        assert terms[0].ascending is False
    
    def test_falls_back_to_first_port_ascending(self):
        """Test fallback to first port column when no timestamps."""
        columns = [
            ColumnSpec(title="ID", key="id"),
            ColumnSpec(title="Name", key="name"),
            ColumnSpec(title="Port", key="port", is_port=True),
            ColumnSpec(title="Status", key="status"),
            ColumnSpec(title="Port2", key="port2", is_port=True)  # Second port
        ]
        
        terms = default_sort_terms(columns)
        assert len(terms) == 1
        assert terms[0].col_index == 2  # First port column
        assert terms[0].ascending is True
    
    def test_falls_back_to_second_column_ascending(self):
        """Test fallback to second column when no timestamps or ports."""
        columns = [
            ColumnSpec(title="ID", key="id"),
            ColumnSpec(title="Name", key="name"),
            ColumnSpec(title="Status", key="status"),
            ColumnSpec(title="Other", key="other")
        ]
        
        terms = default_sort_terms(columns)
        assert len(terms) == 1
        assert terms[0].col_index == 1  # Second column (index 1)
        assert terms[0].ascending is True
    
    def test_falls_back_to_first_column_when_only_one(self):
        """Test fallback to first column when only one column exists."""
        columns = [
            ColumnSpec(title="ID", key="id")
        ]
        
        terms = default_sort_terms(columns)
        assert len(terms) == 1
        assert terms[0].col_index == 0  # First column
        assert terms[0].ascending is True
    
    def test_returns_empty_for_no_columns(self):
        """Test that empty column list returns empty terms."""
        terms = default_sort_terms([])
        assert len(terms) == 0


class TestCoerceTimestamp:
    """Test timestamp coercion for sorting."""
    
    def test_coerce_datetime_object(self):
        """Test coercing existing datetime objects."""
        dt = datetime(2023, 12, 25, 10, 30, 45)
        result = coerce_timestamp(dt)
        assert result == dt
    
    def test_coerce_iso_format_string(self):
        """Test coercing ISO format timestamp strings."""
        iso_string = "2023-12-25T10:30:45"
        result = coerce_timestamp(iso_string)
        assert result == datetime(2023, 12, 25, 10, 30, 45)
        
        # With timezone
        iso_with_tz = "2023-12-25T10:30:45Z"
        result_tz = coerce_timestamp(iso_with_tz)
        assert result_tz is not None
        assert result_tz.year == 2023
        assert result_tz.month == 12
        assert result_tz.day == 25
    
    def test_coerce_epoch_seconds(self):
        """Test coercing epoch seconds."""
        epoch = 1703505045  # 2023-12-25 10:30:45 UTC
        result = coerce_timestamp(epoch)
        assert result is not None
        assert result.year == 2023
        assert result.month == 12
        assert result.day == 25
    
    def test_coerce_common_date_formats(self):
        """Test coercing common date format strings."""
        formats_and_dates = [
            ("2023-12-25 10:30:45", datetime(2023, 12, 25, 10, 30, 45)),
            ("2023-12-25 10:30", datetime(2023, 12, 25, 10, 30)),
            ("12-25 10:30", datetime(1900, 12, 25, 10, 30)),  # Year defaults
            ("2023-12-25", datetime(2023, 12, 25)),
        ]
        
        for date_str, expected in formats_and_dates:
            result = coerce_timestamp(date_str)
            # Compare relevant parts since some formats don't include all fields
            assert result is not None, f"Failed to parse: {date_str}"
            if expected.year != 1900:  # Skip year check for partial formats
                assert result.year == expected.year, f"Year mismatch for: {date_str}"
            assert result.month == expected.month, f"Month mismatch for: {date_str}"
            assert result.day == expected.day, f"Day mismatch for: {date_str}"
    
    def test_coerce_invalid_returns_none(self):
        """Test that invalid timestamps return None."""
        invalid_inputs = [
            None,
            "",
            "   ",
            "not-a-date",
            "invalid-format",
            123,  # Too small for epoch
            99999999999999,  # Too large for epoch
        ]
        
        for invalid in invalid_inputs:
            result = coerce_timestamp(invalid)
            assert result is None, f"Should return None for: {invalid}"


class TestCoercePort:
    """Test port coercion for sorting."""
    
    def test_coerce_simple_ports(self):
        """Test coercing simple port specifications."""
        test_cases = [
            ("1A", (1, 1, "1A")),
            ("2B", (2, 2, "2B")),
            ("10C", (10, 3, "10C")),
            ("15D", (15, 4, "15D")),
        ]
        
        for port_str, expected in test_cases:
            result = coerce_port(port_str)
            assert result == expected, f"Failed for port: {port_str}"
    
    def test_coerce_port_ranges_takes_first(self):
        """Test that port ranges take the first port for sorting."""
        test_cases = [
            ("1A-1D", (1, 1, "1A-1D")),  # Takes 1A
            ("2B-3C", (2, 2, "2B-3C")),  # Takes 2B
            ("10A-12D", (10, 1, "10A-12D")),  # Takes 10A
        ]
        
        for port_range, expected in test_cases:
            result = coerce_port(port_range)
            assert result == expected, f"Failed for port range: {port_range}"
    
    def test_coerce_port_lists_takes_first(self):
        """Test that port lists take the first port for sorting."""
        test_cases = [
            ("1A,2B,3C", (1, 1, "1A,2B,3C")),  # Takes 1A
            ("5D,1B", (5, 4, "5D,1B")),  # Takes 5D
        ]
        
        for port_list, expected in test_cases:
            result = coerce_port(port_list)
            assert result == expected, f"Failed for port list: {port_list}"
    
    def test_coerce_numeric_only_ports(self):
        """Test coercing numeric-only port specifications."""
        test_cases = [
            ("1", (1, 0, "1")),    # Numeric ports get slot_order 0
            ("10", (10, 0, "10")),
            ("port1", (1, 0, "PORT1")),  # Extract number from text
        ]
        
        for port_str, expected in test_cases:
            result = coerce_port(port_str)
            assert result == expected, f"Failed for numeric port: {port_str}"
    
    def test_coerce_case_insensitive(self):
        """Test that port coercion is case insensitive."""
        test_cases = [
            ("1a", (1, 1, "1A")),
            ("2b", (2, 2, "2B")),
            ("3c", (3, 3, "3C")),
            ("4d", (4, 4, "4D")),
        ]
        
        for port_str, expected in test_cases:
            result = coerce_port(port_str)
            assert result == expected, f"Failed for case test: {port_str}"
    
    def test_coerce_invalid_ports_sort_last(self):
        """Test that invalid port specifications sort last."""
        invalid_inputs = [
            None,
            "",
            "   ",
            "invalid",
            "no-numbers-here",
        ]
        
        for invalid in invalid_inputs:
            result = coerce_port(invalid)
            assert result[0] == 999999, f"Invalid port should sort last: {invalid}"
            assert result[1] == 999999, f"Invalid port should sort last: {invalid}"


class TestCoerceGeneric:
    """Test generic value coercion for sorting."""
    
    def test_coerce_none_and_empty(self):
        """Test that None and empty values are handled consistently."""
        empty_inputs = [None, "", "   "]
        
        for empty in empty_inputs:
            result = coerce_generic(empty)
            assert result == (1, ""), f"Empty value should have priority 1: {empty}"
    
    def test_coerce_numeric_values(self):
        """Test coercing numeric values."""
        numeric_cases = [
            (42, (0, 42.0)),
            (3.14, (0, 3.14)),
            ("123", (0, 123.0)),
            ("45.67", (0, 45.67)),
            ("-10", (0, -10.0)),
        ]
        
        for value, expected in numeric_cases:
            result = coerce_generic(value)
            assert result == expected, f"Failed for numeric: {value}"
    
    def test_coerce_text_values(self):
        """Test coercing text values."""
        text_cases = [
            ("apple", (0, "apple")),
            ("Banana", (0, "banana")),  # Case folded
            ("Cherry", (0, "cherry")),
            ("123abc", (0, "123abc")),  # Non-numeric text
        ]
        
        for value, expected in text_cases:
            result = coerce_generic(value)
            assert result == expected, f"Failed for text: {value}"
    
    def test_coerce_case_folding(self):
        """Test that text values are case-folded for consistent sorting."""
        case_variants = ["Apple", "APPLE", "apple", "ApPlE"]
        
        for variant in case_variants:
            result = coerce_generic(variant)
            assert result == (0, "apple"), f"Case folding failed for: {variant}"


class TestSortRows:
    """Test the complete row sorting functionality."""
    
    def get_test_data(self):
        """Helper to create test data and columns."""
        columns = [
            ColumnSpec(title="ID", key="id"),
            ColumnSpec(title="Name", key="name"),
            ColumnSpec(title="Port", key="port", is_port=True),
            ColumnSpec(title="Time", key="time", is_timestamp=True),
            ColumnSpec(title="Value", key="value")
        ]
        
        rows = [
            {"id": "3", "name": "Charlie", "port": "2A", "time": "2023-12-25T12:00:00", "value": "100"},
            {"id": "1", "name": "Alice", "port": "1A", "time": "2023-12-25T10:00:00", "value": "200"},
            {"id": "2", "name": "Bob", "port": "1B", "time": "2023-12-25T11:00:00", "value": "150"},
            {"id": "4", "name": "Diana", "port": "2B", "time": "2023-12-25T13:00:00", "value": "50"},
        ]
        
        return columns, rows
    
    def test_sort_by_single_column_ascending(self):
        """Test sorting by single column ascending."""
        columns, rows = self.get_test_data()
        terms = [SortTerm(col_index=1, ascending=True)]  # Name column
        
        sorted_rows = sort_rows(rows, columns, terms)
        names = [row["name"] for row in sorted_rows]
        assert names == ["Alice", "Bob", "Charlie", "Diana"]
    
    def test_sort_by_single_column_descending(self):
        """Test sorting by single column descending."""
        columns, rows = self.get_test_data()
        terms = [SortTerm(col_index=1, ascending=False)]  # Name column descending
        
        sorted_rows = sort_rows(rows, columns, terms)
        names = [row["name"] for row in sorted_rows]
        assert names == ["Diana", "Charlie", "Bob", "Alice"]
    
    def test_sort_by_timestamp_column(self):
        """Test sorting by timestamp column."""
        columns, rows = self.get_test_data()
        terms = [SortTerm(col_index=3, ascending=False)]  # Time column descending
        
        sorted_rows = sort_rows(rows, columns, terms)
        names = [row["name"] for row in sorted_rows]
        # Diana (13:00), Charlie (12:00), Bob (11:00), Alice (10:00)
        assert names == ["Diana", "Charlie", "Bob", "Alice"]
    
    def test_sort_by_port_column(self):
        """Test sorting by port column."""
        columns, rows = self.get_test_data()
        terms = [SortTerm(col_index=2, ascending=True)]  # Port column ascending
        
        sorted_rows = sort_rows(rows, columns, terms)
        names = [row["name"] for row in sorted_rows]
        # 1A, 1B, 2A, 2B
        assert names == ["Alice", "Bob", "Charlie", "Diana"]
    
    def test_sort_by_multiple_columns(self):
        """Test multi-column sorting with different directions."""
        columns, rows = self.get_test_data()
        # Sort by port ascending, then by time descending
        terms = [
            SortTerm(col_index=2, ascending=True),   # Port first
            SortTerm(col_index=3, ascending=False)   # Then time descending
        ]
        
        # Add more test data to test secondary sort
        rows.append({"id": "5", "name": "Eve", "port": "1A", "time": "2023-12-25T09:00:00", "value": "75"})
        
        sorted_rows = sort_rows(rows, columns, terms)
        names = [row["name"] for row in sorted_rows]
        # Port 1A: Alice (10:00) then Eve (09:00)
        # Port 1B: Bob (11:00)
        # Port 2A: Charlie (12:00)
        # Port 2B: Diana (13:00)
        assert names == ["Alice", "Eve", "Bob", "Charlie", "Diana"]
    
    def test_sort_stable_ordering(self):
        """Test that sorting is stable for equal values."""
        columns = [ColumnSpec(title="Group", key="group"), ColumnSpec(title="Name", key="name")]
        rows = [
            {"group": "A", "name": "First"},
            {"group": "A", "name": "Second"},
            {"group": "B", "name": "Third"},
            {"group": "A", "name": "Fourth"},
        ]
        
        terms = [SortTerm(col_index=0, ascending=True)]  # Sort by group
        sorted_rows = sort_rows(rows, columns, terms)
        
        # All group A items should maintain their relative order
        group_a_names = [row["name"] for row in sorted_rows if row["group"] == "A"]
        assert group_a_names == ["First", "Second", "Fourth"]
    
    def test_sort_empty_rows(self):
        """Test sorting empty row list."""
        columns, _ = self.get_test_data()
        terms = [SortTerm(col_index=1, ascending=True)]
        
        sorted_rows = sort_rows([], columns, terms)
        assert sorted_rows == []
    
    def test_sort_no_terms(self):
        """Test sorting with no sort terms."""
        columns, rows = self.get_test_data()
        
        sorted_rows = sort_rows(rows, columns, [])
        # Should return copy of original rows
        assert len(sorted_rows) == len(rows)
        assert sorted_rows is not rows  # Should be a copy
    
    def test_sort_invalid_column_index(self):
        """Test sorting with invalid column indices."""
        columns, rows = self.get_test_data()
        terms = [
            SortTerm(col_index=99, ascending=True),  # Invalid index
            SortTerm(col_index=1, ascending=True)    # Valid index
        ]
        
        sorted_rows = sort_rows(rows, columns, terms)
        # Should ignore invalid index and sort by valid one
        names = [row["name"] for row in sorted_rows]
        assert names == ["Alice", "Bob", "Charlie", "Diana"]


class TestCLIHelpTextConsistency:
    """Test consistency of help text across commands for sorting and export options."""
    
    def get_command_help_patterns(self):
        """Extract help text patterns from CLI commands."""
        import inspect
        from boxofports import cli
        
        # Find all functions that are CLI commands with table output
        table_commands = []
        
        # Get all functions from the CLI module
        for name, obj in inspect.getmembers(cli, inspect.isfunction):
            # Look for functions that have sort, csv, and json_export parameters
            sig = inspect.signature(obj)
            params = list(sig.parameters.keys())
            
            if 'sort' in params and ('csv' in params or 'json_export' in params):
                table_commands.append((name, obj, sig))
        
        return table_commands
    
    def extract_help_text(self, param):
        """Extract help text from a parameter."""
        if hasattr(param, 'default') and hasattr(param.default, 'help'):
            return param.default.help
        return None
    
    def test_sort_help_text_consistency(self):
        """Test that --sort help text is consistent and concise across commands."""
        table_commands = self.get_command_help_patterns()
        sort_help_texts = []
        
        for name, func, sig in table_commands:
            if 'sort' in sig.parameters:
                help_text = self.extract_help_text(sig.parameters['sort'])
                if help_text:
                    sort_help_texts.append((name, help_text))
        
        # Should have multiple commands with sort option
        assert len(sort_help_texts) >= 5, f"Expected at least 5 commands with --sort, got {len(sort_help_texts)}"
        
        # All sort help texts should follow the pattern
        expected_pattern = r"Sort by column numbers.*['\"].*Use 'a' & 'd' for ascending/descending"
        
        for name, help_text in sort_help_texts:
            assert re.search(expected_pattern, help_text), \
                f"Command {name} has inconsistent --sort help: {help_text}"
            
            # Should be concise (not contain "Default:" explanations)
            assert "Default:" not in help_text, \
                f"Command {name} --sort help should not contain default explanation: {help_text}"
            
            # Should contain example pattern
            assert re.search(r"['\"]\d+.*[dDaA]?.*['\"']", help_text), \
                f"Command {name} --sort help should contain column number examples: {help_text}"
    
    def test_csv_help_text_consistency(self):
        """Test that --csv help text is consistent across commands."""
        table_commands = self.get_command_help_patterns()
        csv_help_texts = []
        
        for name, func, sig in table_commands:
            if 'csv' in sig.parameters:
                help_text = self.extract_help_text(sig.parameters['csv'])
                if help_text:
                    csv_help_texts.append((name, help_text))
        
        # Should have multiple commands with csv option
        assert len(csv_help_texts) >= 5, f"Expected at least 5 commands with --csv, got {len(csv_help_texts)}"
        
        # All CSV help texts should follow the expected pattern
        expected_csv_pattern = r"Export table data to CSV.*filename.*file output.*console output"
        
        for name, help_text in csv_help_texts:
            assert re.search(expected_csv_pattern, help_text), \
                f"Command {name} has inconsistent --csv help: {help_text}"
            
            # Should mention both file and console output modes
            assert "filename" in help_text and "console" in help_text, \
                f"Command {name} --csv help should mention both output modes: {help_text}"
    
    def test_json_help_text_consistency(self):
        """Test that --json/--json-export help text is consistent across commands."""
        table_commands = self.get_command_help_patterns()
        json_help_texts = []
        
        for name, func, sig in table_commands:
            # Check for both 'json_export' and 'json' parameters
            json_param = None
            if 'json_export' in sig.parameters:
                json_param = sig.parameters['json_export']
            elif 'json' in sig.parameters:
                json_param = sig.parameters['json']
            
            if json_param:
                help_text = self.extract_help_text(json_param)
                if help_text and "Export table data to JSON" in help_text:
                    json_help_texts.append((name, help_text))
        
        # Should have multiple commands with JSON export option
        assert len(json_help_texts) >= 5, f"Expected at least 5 commands with --json, got {len(json_help_texts)}"
        
        # All JSON help texts should follow the expected pattern
        expected_json_pattern = r"Export table data to JSON.*filename.*file output.*console output"
        
        for name, help_text in json_help_texts:
            assert re.search(expected_json_pattern, help_text), \
                f"Command {name} has inconsistent --json help: {help_text}"
            
            # Should mention both file and console output modes
            assert "filename" in help_text and "console" in help_text, \
                f"Command {name} --json help should mention both output modes: {help_text}"
    
    def test_export_help_text_similarity(self):
        """Test that CSV and JSON help texts are structurally similar."""
        table_commands = self.get_command_help_patterns()
        
        for name, func, sig in table_commands:
            csv_help = None
            json_help = None
            
            if 'csv' in sig.parameters:
                csv_help = self.extract_help_text(sig.parameters['csv'])
            
            if 'json_export' in sig.parameters:
                json_help = self.extract_help_text(sig.parameters['json_export'])
            elif 'json' in sig.parameters:
                json_help = self.extract_help_text(sig.parameters['json'])
            
            # If both exist, they should have similar structure
            if csv_help and json_help and "Export table data" in csv_help and "Export table data" in json_help:
                # Both should mention filename and console output
                csv_words = set(csv_help.lower().split())
                json_words = set(json_help.lower().split())
                
                # Key concepts should be present in both
                key_concepts = {"export", "table", "data", "filename", "file", "output", "console"}
                
                for concept in key_concepts:
                    assert concept in csv_words, f"Command {name} --csv missing concept: {concept}"
                    assert concept in json_words, f"Command {name} --json missing concept: {concept}"
    
    def test_help_text_conciseness(self):
        """Test that help texts are reasonably concise and useful."""
        table_commands = self.get_command_help_patterns()
        
        for name, func, sig in table_commands:
            for param_name in ['sort', 'csv', 'json_export', 'json']:
                if param_name in sig.parameters:
                    help_text = self.extract_help_text(sig.parameters[param_name])
                    if help_text:
                        # Should be concise (not too long)
                        word_count = len(help_text.split())
                        assert word_count <= 30, \
                            f"Command {name} --{param_name} help too long ({word_count} words): {help_text}"
                        
                        # Should be useful (contain key information)
                        assert len(help_text.strip()) >= 20, \
                            f"Command {name} --{param_name} help too short: {help_text}"


if __name__ == "__main__":
    pytest.main([__file__])