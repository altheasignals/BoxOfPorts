# BoxOfPorts Development Rules

## CSV/JSON Export Requirements for Table Commands

**Rule**: All CLI commands that produce table output MUST include `--csv` and `--json` export options.

### Implementation Requirements

1. **Option Signatures**: All table-producing commands must include these two options:
   ```python
   csv: Optional[str] = typer.Option(None, "--csv", help="Export table data to CSV (filename for file output, empty for console output)"),
   json_export: Optional[str] = typer.Option(None, "--json", help="Export table data to JSON (filename for file output, empty for console output)"),
   ```

2. **Console vs File Output Behavior**:
   - When `--csv` or `--json` is used WITHOUT a filename (empty string), output CSV/JSON directly to console (stdout) for pipeline integration
   - When console output mode is active, suppress ALL other output (tables, messages, summaries) 
   - When `--csv filename.csv` or `--json filename.json` is used WITH a filename, save to file and show normal output plus export confirmation

3. **Import Requirements**: Commands must import the table export utilities:
   ```python
   from .table_export import (
       handle_table_export, 
       # Plus appropriate data conversion functions for the command type
   )
   ```

4. **Implementation Pattern**: Follow this pattern in all table-producing commands:
   ```python
   # Export table if requested
   console_only_mode = False
   if csv is not None or json_export is not None:
       current_profile = config_manager.get_current_profile()
       export_data = convert_data_to_export_format(table_data)
       console_only_mode = handle_table_export(
           data=export_data,
           profile_name=current_profile,
           command_name="command-name",
           csv_filename=csv if csv != "" else None,
           json_filename=json_export if json_export != "" else None,
           export_csv=(csv is not None),
           export_json=(json_export is not None)
       )
   
   # Only show table and other output if not in console-only export mode
   if not console_only_mode:
       console.print(table)
       # Other console output...
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

2. **File Output Testing**:
   ```bash
   # Should create file and show normal output + confirmation
   boxofports inbox list --csv messages.csv
   
   # Should create file with custom name
   boxofports inbox list --json my-messages.json
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

*"Let it be known there is a fountain... that ripples your data to all the tools!"* - Ripple (1970)