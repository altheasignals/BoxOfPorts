# BoxOfPorts Development Rules

## CSV/JSON Export Requirements for Table Commands

**Rule**: All CLI commands that produce table output MUST include `--csv` and `--json` export options.

### Implementation Requirements

1. **Option Signatures**: All table-producing commands must include these two options:
   ```python
   csv: bool = typer.Option(False, "--csv", help="Export table data as CSV to stdout"),
   json_export: bool = typer.Option(False, "--json", help="Export table data as JSON to stdout"),
   ```

2. **Console Output Behavior**:
   - When `--csv` or `--json` is used, output CSV/JSON directly to console (stdout) for pipeline integration
   - When console output mode is active, suppress ALL other output (tables, messages, summaries)
   - Users can redirect output to files using standard shell redirection: `command --csv > file.csv`

3. **Import Requirements**: Commands must import the table export utilities:
   ```python
   from .table_export import (
       handle_table_export, 
       # Plus appropriate data conversion functions for the command type
   )
   ```

4. **Implementation Pattern**: Use the centralized rendering function:
   ```python
   # Centralized rendering with sorting and export
   console_only_mode = render_and_export_table(
       title="Table Title",
       columns=get_appropriate_columns(),
       rows=table_data,
       profile_name=None,  # Unused for stdout exports
       command_name="",    # Unused for stdout exports
       sort_option=sort,
       csv_filename=None,  # Always None for stdout
       json_filename=None, # Always None for stdout
       export_csv=csv,
       export_json=json_export
   )
   
   # Only show other output if not in console-only export mode
   if not console_only_mode:
       # Additional output like summaries...
   ```

5. **Data Conversion Functions**: Create appropriate data conversion functions in `table_export.py`:
   - `sms_tasks_to_export_data()` - For SMS task tables
   - `sms_results_to_export_data()` - For SMS result tables  
   - `imei_data_to_export_data()` - For IMEI tables
   - `profiles_to_export_data()` - For profile tables
   - `messages_to_export_data()` - For message tables
   - Add new functions as needed for other table types

6. **File Naming Convention**: Default filenames follow the pattern:
   `{profile_name}-{command_name}-{timestamp}.{format}`
   
   Example: `production-inbox-list-20250926_093010.csv`

### Commands Requiring This Feature

✅ **Implemented Commands**:
- `sms send` - Task preview and results tables
- `sms spray` - Task preview and results tables (inherits from send)
- `ops get-imei` - IMEI values table
- `config list` - Profiles table
- `inbox list` - Messages table
- `inbox search` - Search results table
- `inbox stop` - STOP messages table

🔄 **Future Commands**: Any new command that produces a table MUST implement this pattern.

### Testing Requirements

1. **Console Output Testing**:
   ```bash
   # Should output only CSV to stdout
   boxofports inbox list --csv
   
   # Should output only JSON to stdout  
   boxofports inbox list --json
   
   # Should be pipeline-friendly
   boxofports inbox list --csv | grep "1A" | wc -l
   ```

2. **File Output via Shell Redirection**:
   ```bash
   # Redirect CSV output to file
   boxofports inbox list --csv > messages.csv
   
   # Redirect JSON output to file
   boxofports inbox list --json > messages.json
   
   # Append to existing file
   boxofports inbox list --csv >> all-messages.csv
   ```

### Pipeline Integration Examples

The console output mode enables powerful pipeline integration:

```bash
# Get IMEI values as CSV and process with standard tools
boxofports ops get-imei --ports "1A-1D" --csv | grep "123456" | cut -d, -f1

# Export inbox messages as JSON and process with jq
boxofports inbox list --count 100 --json | jq '.[] | select(.type == "stop")'

# Convert CSV to other formats
boxofports config list --csv | csvtojson > profiles.json

# Count messages by type
boxofports inbox list --csv | tail -n +2 | cut -d, -f2 | sort | uniq -c
```

This rule ensures consistent behavior across all BoxOfPorts commands and enables powerful command-line workflows while keeping the CLI "groovy" like the river flowing into the sea. 🎵


## Table Sorting Requirements for All Commands

**Rule**: All CLI commands that produce table output MUST include `--sort` option with column-number syntax and per-column direction markers.

### Sorting Behavior

Tables flow in natural order like a well-traveled road - first by time's arrow, then by lane, then by name:

1. **Default Sorting Policy** (when `--sort` is not provided):
   - If any timestamp column exists → sort by **first timestamp column descending** (most recent first)
   - Else if any port column exists → sort by **first port column ascending** (natural port order: 1A, 1B, 2A, etc.)
   - Else → sort by **second column ascending** (typically names or aliases)
   - Fallback → sort by **first column ascending**

2. **Custom Sorting Syntax**: `--sort "column_numbers_with_directions"`
   - Column numbers are **1-based** (matching table display)
   - Default direction is **ascending** (`a`)
   - Add `d` suffix for **descending** order
   - Multiple columns separated by commas: `"2,1d,4a"`
   - Invalid tokens are ignored gracefully with dim warnings

### Column Number Reference

#### SMS Commands (`sms send`, `sms spray`)
**Task Preview Table**:
1. TID | 2. Device Alias | 3. Port | 4. To | 5. Text | 6. Status

**Results Table**:
1. TID | 2. Device Alias | 3. Status

#### Operations Commands
**IMEI Table** (`ops get-imei`):
1. Device Alias | 2. Port | 3. IMEI

#### Configuration Commands
**Profiles Table** (`config list`):
1. Name | 2. Device Alias | 3. Host:Port | 4. Username | 5. Status

#### Inbox Commands (`inbox list`, `inbox search`, `inbox stop`)
**Standard Messages Table**:
1. ID | 2. Device Alias | 3. Type | 4. Port | 5. From | 6. Time | 7. Content

**Delivery Reports Table**:
1. ID | 2. Device Alias | 3. Type | 4. Port | 5. Time | 6. To | 7. Status

### Implementation Requirements

1. **Option Signature**: All table-producing commands must include:
   ```python
   sort: Optional[str] = typer.Option(
       None,
       "--sort", 
       help="Sort by column numbers: '2,1d,4a'. Use 'a' for ascending (default) or 'd' for descending. Default: time desc → port asc → second column asc."
   ),
   ```

2. **Import Requirements**: Commands must import the centralized rendering:
   ```python
   from .table_export import (
       render_and_export_table,
       get_sms_send_tasks_columns,  # Or appropriate column spec function
   )
   ```

3. **Implementation Pattern**: Replace manual Rich table creation with centralized rendering:
   ```python
   # Build data in export format
   table_data = convert_data_to_export_format(raw_data)
   columns = get_appropriate_columns_for_table_type()
   
   # Centralized rendering with sorting and export
   console_only_mode = render_and_export_table(
       title="Table Title",
       columns=columns,
       rows=table_data,
       profile_name=config_manager.get_current_profile(),
       command_name="command-identifier",
       sort_option=sort,
       csv_filename=csv if csv != "" else None,
       json_filename=json_export if json_export != "" else None,
       export_csv=(csv is not None),
       export_json=(json_export is not None)
   )
   
   # Skip other output if console-only export mode
   if console_only_mode:
       return
   ```

### Sorting Examples

```bash
# Default sorting (follows natural order policy)
boxofports inbox list

# Sort by Time descending (column 6), then Port ascending (column 4) 
boxofports inbox list --sort "6d,4"

# Sort IMEI table by Port descending
boxofports ops get-imei --sort "2d"

# Sort profiles by Status ascending, then Name descending
boxofports config list --sort "5,1d"

# Complex multi-column sort with pipeline export
boxofports inbox list --sort "6d,4a,2" --csv | head -n 20
```

### Pipeline Integration with Sorting

Sorting applies consistently to both display and export modes, ensuring data flows predictably:

```bash
# Export sorted data directly to pipeline
boxofports inbox list --sort "6d" --csv | grep "urgent" | cut -d, -f5,7

# Time-sorted messages for analysis
boxofports inbox list --count 100 --sort "6d" --json | jq '.[:10] | .[].Time'

# Port-ordered IMEI data
boxofports ops get-imei --sort "2" --csv | tail -n +2 | cut -d, -f2 | sort -V | uniq -c

# Profile statistics with custom sorting
boxofports config list --sort "2,5d" --csv | awk -F, '{print $2, $5}' | sort | uniq -c
```

### Data Type Handling

**Timestamps**: Parsed from ISO format, epoch seconds, or common date patterns. Unparseable values sort last.

**Ports**: Intelligently sorted as `1A < 1B < 1C < 1D < 2A < 2B...` with numeric board precedence and alphabetic slot ordering.

**Generic Values**: Numbers sort numerically, text sorts case-insensitively, empty/null values cluster appropriately.

### Testing Requirements

1. **Default Sorting Verification**:
   ```bash
   # Inbox should show latest messages first
   boxofports inbox list | head -n 5
   
   # IMEI should show ports in natural order
   boxofports ops get-imei --ports "2D,1A,1C,2A"
   ```

2. **Custom Sorting Verification**:
   ```bash
   # Verify multi-column sorts work correctly
   boxofports inbox list --sort "4,6d" 
   
   # Verify invalid tokens are ignored gracefully
   boxofports config list --sort "99,invalid,2d"
   ```

3. **Export Consistency**:
   ```bash
   # Display and export should have identical ordering
   boxofports inbox list --sort "6d,4" > display.txt
   boxofports inbox list --sort "6d,4" --csv > export.csv
   ```

This ensures all data flows like music through the command line - structured, predictable, and harmoniously ordered. 🎵


