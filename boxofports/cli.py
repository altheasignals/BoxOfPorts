"""CLI interface for BoxOfPorts using Typer."""

import hashlib
import random
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .__version__ import get_full_version_info
from .config import EjoinConfig, config_manager, parse_host_port
from .http import EjoinHTTPError, create_sync_client
from .ports import format_ports_for_api, parse_port_spec
from .store import get_store, initialize_store
from .table_export import (
    get_imei_columns,
    get_inbox_delivery_reports_columns,
    get_inbox_messages_columns,
    get_profiles_columns,
    get_sms_send_results_columns,
    get_sms_send_tasks_columns,
    handle_table_export,
    imei_data_to_export_data,
    messages_to_export_data,
    profiles_to_export_data,
    render_and_export_table,
    sms_results_to_export_data,
    sms_tasks_to_export_data,
)
from .templating import parse_template_variables, render_sms_template
from .splash import show_welcome_message

app = typer.Typer(
    help="BoxOfPorts - SMS Gateway Management CLI for EJOIN Router Operators",
    no_args_is_help=False,
    invoke_without_command=True
)
sms_app = typer.Typer(help="SMS operations")
ops_app = typer.Typer(help="Device operations")
status_app = typer.Typer(help="Status monitoring")
inbox_app = typer.Typer(help="Inbox management")
config_app = typer.Typer(help="Profile and configuration management")

app.add_typer(sms_app, name="sms")
app.add_typer(ops_app, name="ops")
app.add_typer(status_app, name="status")
app.add_typer(inbox_app, name="inbox")
app.add_typer(config_app, name="config")

console = Console()


def get_config_or_exit(ctx: typer.Context) -> EjoinConfig:
    """Get configuration for commands that require gateway connection.
    
    Provides helpful guidance if no configuration is available.
    """
    try:
        config = config_manager.get_config()

        # Override with CLI options if provided
        cli_host = ctx.obj.get('cli_host')
        cli_port = ctx.obj.get('cli_port')
        cli_user = ctx.obj.get('cli_user')
        cli_password = ctx.obj.get('cli_password')

        if cli_host:
            host_part, port_part = parse_host_port(cli_host, config.port)
            config.host = host_part
            config.port = port_part
        if cli_port:
            config.port = cli_port
        if cli_user:
            config.username = cli_user
        if cli_password:
            config.password = cli_password

        # Initialize store if not already done
        if 'store_initialized' not in ctx.obj:
            initialize_store(config.db_path)
            ctx.obj['store_initialized'] = True

        return config

    except Exception:
        console.print("[yellow]🎵 Hey now! Gateway configuration needed for this command[/yellow]")
        console.print("")
        
        # Show welcome message with splash screen
        show_welcome_message(console)
        
        console.print("[bold blue]✨ New to BoxOfPorts? Start here:[/bold blue]")
        console.print("   [cyan]boxofports welcome[/cyan]                [dim]# Complete onboarding guide[/dim]")
        console.print("")
        
        console.print("[blue]→ Quick setup with a profile:[/blue]")
        console.print("   [cyan]boxofports config add-profile mygateway \\[/cyan]")
        console.print("   [cyan]  --host 192.168.1.100 --user admin --password yourpass[/cyan]")
        console.print("")
        console.print("[blue]→ Or set environment variables:[/blue]")
        console.print("   [cyan]export EJOIN_HOST=192.168.1.100[/cyan]")
        console.print("   [cyan]export EJOIN_USER=admin[/cyan]")
        console.print("   [cyan]export EJOIN_PASSWORD=yourpass[/cyan]")
        console.print("")
        console.print("[blue]→ Or use CLI options:[/blue]")
        console.print("   [cyan]boxofports --host 192.168.1.100 --user admin --password yourpass <command>[/cyan]")
        console.print("")
        console.print("[dim]Run 'boxofports config --help' for more configuration options[/dim]")
        raise typer.Exit(1)


def version_callback(value: bool):
    """Print version information and exit."""
    if value:
        console.print(get_full_version_info())
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    host: str | None = typer.Option(None, "--host", help="Device IP address"),
    port: int | None = typer.Option(None, "--port", help="Device port"),
    user: str | None = typer.Option(None, "--user", help="Device username"),
    password: str | None = typer.Option(None, "--pass", "--password", help="Device password"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Enable verbose logging"),
    version: bool | None = typer.Option(None, "--version", callback=version_callback, is_eager=True, help="Show version information"),
):
    """BoxOfPorts - SMS Gateway Management CLI for EJOIN Router Operators."""

    # Initialize minimal context - store CLI options for lazy config loading
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['cli_host'] = host
    ctx.obj['cli_port'] = port
    ctx.obj['cli_user'] = user
    ctx.obj['cli_password'] = password

    # Commands that don't need gateway configuration
    command_name = ctx.invoked_subcommand
    config_free_commands = {'completion', 'config', 'help-tree', 'welcome'}

    # If no subcommand provided, show welcome message
    if command_name is None:
        # Show the beautiful splash screen with random tagline
        show_welcome_message(console)
        
        console.print("[bold green]✨ Welcome to BoxOfPorts — SMS Gateway Management CLI ✨[/bold green]")
        console.print("[dim]For EJOIN Router Operators[/dim]\n")
        
        console.print("🎯 [bold blue]Essential First Steps:[/bold blue]")
        console.print("")
        
        console.print("[yellow]1. Explore Commands:[/yellow]")
        console.print("   [cyan]boxofports help-tree[/cyan]              [dim]# Visual tree of all commands[/dim]")
        console.print("")
        
        console.print("[yellow]2. Set Up Your Gateway Profile:[/yellow]")
        console.print("   [cyan]boxofports config add-profile mygateway[/cyan] \\")
        console.print("   [cyan]     --host 192.168.1.100 --user admin --password yourpass[/cyan]")
        console.print("   [dim]# Save credentials once, use everywhere![/dim]")
        console.print("")
        
        console.print("[yellow]3. Enable Shell Completion (Highly Recommended):[/yellow]")
        console.print("   [cyan]boxofports --install-completion[/cyan]    [dim]# TAB completion for all commands[/dim]")
        console.print("   [dim]# Restart terminal, then try: boxofports <TAB>[/dim]")
        console.print("")
        
        console.print("[yellow]4. Test Your Setup:[/yellow]")
        console.print("   [cyan]boxofports test-connection[/cyan]         [dim]# Verify gateway connectivity[/dim]")
        console.print("")
        
        console.print("[yellow]5. Send Your First Test Message:[/yellow]")
        console.print("   [cyan]boxofports sms send --to \"+1234567890\"[/cyan] \\")
        console.print("   [cyan]     --text \"Hello from BoxOfPorts!\" --ports \"1A\"[/cyan]")
        console.print("")
        
        console.print("🚀 [bold blue]Quick Reference:[/bold blue]")
        console.print("   [cyan]boxofports --help[/cyan]                  [dim]# Show all commands[/dim]")
        console.print("   [cyan]boxofports welcome[/cyan]                 [dim]# Show this welcome message again[/dim]")
        console.print("   [cyan]boxofports <command> --help[/cyan]         [dim]# Get help for any command[/dim]")
        console.print("   [cyan]boxofports config list[/cyan]             [dim]# List your profiles[/dim]")
        console.print("   [cyan]boxofports inbox list[/cyan]              [dim]# Check received messages[/dim]")
        console.print("")
        
        console.print("📚 [bold blue]Why BoxOfPorts?[/bold blue]")
        console.print("   • [green]Profile Management[/green] - Save gateway credentials securely")
        console.print("   • [green]Template System[/green] - Dynamic SMS with Jinja2 templating")
        console.print("   • [green]Data Export[/green] - CSV/JSON export for all table commands")
        console.print("   • [green]Inbox Management[/green] - Filter, search, and analyze messages")
        console.print("   • [green]Port Operations[/green] - Lock/unlock, IMEI management")
        console.print("")
        
        console.print("[dim]🎵 Ready to let your signals ripple through the network? 🎵[/dim]")
        raise typer.Exit(0)

    if command_name in config_free_commands:
        # These commands work without gateway config
        return

    # Don't initialize gateway configuration here - let individual commands handle it
    # This allows config commands to work without gateway config


@sms_app.command("send")
def sms_send(
    ctx: typer.Context,
    to: str = typer.Option(..., "--to", help="Recipient phone number"),
    text: str = typer.Option(..., "--text", help="SMS text (supports templates)"),
    ports: str = typer.Option(..., "--ports", "--port", help="Ports to send from (e.g., '1A,2B', '4-8', or 'ports.csv')"),
    repeat: int = typer.Option(1, "--repeat", help="Number of times to repeat"),
    intvl_ms: int = typer.Option(500, "--intvl-ms", help="Interval between SMS in milliseconds"),
    timeout: int = typer.Option(30, "--timeout", help="Timeout in seconds"),
    vars: list[str] = typer.Option([], "--var", help="Template variables (key=value)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be sent without sending"),
    sort: str | None = typer.Option(None, "--sort", help="Sort by column numbers, e.g. '2,1d,4'. Use 'a' & 'd' for ascending/descending."),
    csv: bool = typer.Option(False, "--csv", help="Export table data as CSV to stdout"),
    json_export: bool = typer.Option(False, "--json", help="Export table data as JSON to stdout"),
):
    """Send test SMS with template support and per-port routing."""
    config = get_config_or_exit(ctx)

    try:
        # Get device alias for consistent usage throughout command
        device_alias = config.device_alias or config.host

        # Parse ports and template variables
        port_list = parse_port_spec(ports)
        template_vars = parse_template_variables(vars) if vars else {}
        
        # Prepare profile-based template variables
        current_profile_name = config_manager.get_current_profile()
        profile_template_vars = {
            'devicename': device_alias,
            'profilename': current_profile_name or 'default',
            'hostport': f"{config.host}:{config.port}"
        }
        
        # Check if we're in console-only export mode
        console_only_mode = csv or json_export

        if not console_only_mode:
            console.print(f"[blue]Sending SMS to {to} via {len(port_list)} ports[/blue]")

            if dry_run:
                console.print("[yellow]DRY RUN - Not actually sending[/yellow]")

        # Create tasks
        tasks = []
        tid_base = random.randint(1000, 9999)

        for repeat_idx in range(repeat):
            for port_idx, port in enumerate(port_list):
                tid = tid_base + (repeat_idx * len(port_list)) + port_idx

                # Render template for this port with profile variables
                rendered_text = render_sms_template(text, port, port_idx, profile_template_vars, **template_vars)

                task = {
                    "tid": tid,
                    "from": format_ports_for_api([port]),
                    "to": to,
                    "sms": rendered_text,
                    "intvl": str(intvl_ms),
                    "tmo": timeout,
                }
                tasks.append(task)

                # Store task info locally
                if not dry_run:
                    store = get_store()
                    text_hash = hashlib.md5(rendered_text.encode()).hexdigest()[:8]
                    store.save_sms_task(
                        tid=tid,
                        ports=[port],
                        to_number=to,
                        text_hash=text_hash,
                        template_text=text,
                        template_vars=template_vars
                    )

        # Prepare task data for display and export
        current_profile = config_manager.get_current_profile()
        task_data = sms_tasks_to_export_data(tasks, device_alias=device_alias)
        
        # Show preview table with centralized rendering
        render_console_only = render_and_export_table(
            title="SMS Tasks",
            columns=get_sms_send_tasks_columns(),
            rows=task_data,
            profile_name=current_profile,
            command_name="sms-send-tasks",
            sort_option=sort,
            csv_filename=None,
            json_filename=None,
            export_csv=csv,
            export_json=json_export
        )

        # Return early if in console-only export mode (acts like dry-run for pipeline integration)
        if render_console_only:
            return

        if not dry_run:
            # Actually send the SMS
            client = create_sync_client(config)
            request_data = {
                "type": "send-sms",
                "task_num": len(tasks),
                "tasks": tasks
            }

            try:
                response = client.post_json("/goip_post_sms.html", json=request_data)

                # Update local storage and prepare results data
                for status in response.get('status', []):
                    tid = status['tid']
                    status_text = status['status']
                    # Update local storage
                    store.update_task_status(tid, status_text)
                
                # Show results table with centralized rendering
                results_data = sms_results_to_export_data(response.get('status', []), device_alias=device_alias)
                results_console_only = render_and_export_table(
                    title="SMS Send Results",
                    columns=get_sms_send_results_columns(),
                    rows=results_data,
                    profile_name=current_profile,
                    command_name="sms-send-results",
                    sort_option=sort,
                    csv_filename=None,
                    json_filename=None,
                    export_csv=csv,
                    export_json=json_export
                )

            except EjoinHTTPError as e:
                console.print(f"[red]Message undeliverable — {e}[/red]")
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@sms_app.command("spray")
def sms_spray(
    ctx: typer.Context,
    to: str = typer.Option(..., "--to", help="Recipient phone number"),
    text: str = typer.Option(..., "--text", help="SMS text (supports templates)"),
    ports: str = typer.Option(..., "--ports", "--port", help="Ports to spray from (supports CSV files)"),
    intvl_ms: int = typer.Option(250, "--intvl-ms", help="Interval between SMS"),
    sort: str | None = typer.Option(None, "--sort", help="Sort by column numbers, e.g. '2,1d,4'. Use 'a' & 'd' for ascending/descending."),
    csv: bool = typer.Option(False, "--csv", help="Export table data as CSV to stdout"),
    json_export: bool = typer.Option(False, "--json", help="Export table data as JSON to stdout"),
):
    """Spray the same number via multiple ports quickly."""
    # This is essentially the same as send but with different defaults
    ctx.invoke(sms_send, to=to, text=text, ports=ports, repeat=1, intvl_ms=intvl_ms, timeout=30, vars=[], dry_run=False, sort=sort, csv=csv, json_export=json_export)


@status_app.command("subscribe")
def status_subscribe(
    ctx: typer.Context,
    callback: str = typer.Option(..., "--callback", help="Callback URL for status reports"),
    period: int = typer.Option(60, "--period", help="Report period in seconds"),
):
    """Subscribe to device/port status notifications.
    
    NOTE: This REPLACES any existing webhook subscription.
    The device can only send notifications to ONE callback URL at a time.
    """
    config = get_config_or_exit(ctx)

    try:
        client = create_sync_client(config)
        params = {
            "url": callback,
            "period": period,
        }

        response = client.get_json("/goip_get_status.html", params=params)

        console.print("[green]✓ Webhook subscription configured[/green]")
        console.print("[yellow]ℹ  This REPLACES any previous webhook subscription[/yellow]")
        console.print("")
        console.print(f"📡 Callback URL: {callback}")
        console.print(f"⏰ Reports every: {period} seconds")
        console.print("📱 Includes: All SIM card statuses, signal levels, carrier info")
        console.print("")
        console.print("[dim]The device will now send comprehensive status reports to your callback URL[/dim]")
        console.print("[dim]To stop notifications: boxofports status subscribe --callback '' --period 0[/dim]")

    except EjoinHTTPError as e:
        console.print(f"[red]The music stoped — {e}[/red]")
        raise typer.Exit(1)


@ops_app.command("lock")
def ops_lock(
    ctx: typer.Context,
    ports: str = typer.Option(..., "--ports", "--port", help="Ports to lock (supports CSV files)"),
):
    """Lock specified ports."""
    config = get_config_or_exit(ctx)

    try:
        port_list = parse_port_spec(ports)
        client = create_sync_client(config)

        request_data = {
            "type": "command",
            "op": "lock",
            "ports": format_ports_for_api(port_list)
        }

        response = client.post_json("/goip_send_cmd.html", json=request_data)
        console.print(f"[green]Ports locked in — {', '.join(port_list)}[/green]")

    except Exception as e:
        console.print(f"[red]Lock operation failed: {e}[/red]")
        raise typer.Exit(1)


@ops_app.command("unlock")
def ops_unlock(
    ctx: typer.Context,
    ports: str = typer.Option(..., "--ports", "--port", help="Ports to unlock (supports CSV files)"),
):
    """Unlock specified ports."""
    config = get_config_or_exit(ctx)

    try:
        port_list = parse_port_spec(ports)
        client = create_sync_client(config)

        request_data = {
            "type": "command",
            "op": "unlock",
            "ports": format_ports_for_api(port_list)
        }

        response = client.post_json("/goip_send_cmd.html", json=request_data)
        console.print(f"[green]Unlock command sent to ports: {', '.join(port_list)}[/green]")

    except Exception as e:
        console.print(f"[red]Unlock operation failed: {e}[/red]")
        raise typer.Exit(1)


@ops_app.command("set-imei")
def ops_set_imei(
    ctx: typer.Context,
    ports: str = typer.Option(..., "--ports", "--port", help="Ports to set IMEI for (e.g., '1A,2B', '1-4', '*', or 'ports.csv')"),
    imeis: str = typer.Option(..., "--imeis", help="IMEI values (comma-separated list or CSV file with 'imei' column)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done without executing"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompts"),
    wait_timeout: int = typer.Option(90, "--wait-timeout", help="Reboot wait timeout in seconds"),
):
    """Set IMEI values — alter the cosmic cellular frequencies.
    
    This command handles the complete IMEI change workflow:
    1. Set IMEI values for specified ports
    2. Save configuration  
    3. Reboot device
    4. Wait for reboot completion
    5. Unlock affected SIM slots
    
    Both --ports and --imeis support CSV files with appropriate columns.
    """
    config = get_config_or_exit(ctx)

    try:
        from boxofports.api_models import IMEIPortChange
        from boxofports.csv_port_parser import (
            CSVPortParseError,
            expand_csv_imeis_if_needed,
            extract_port_and_slot,
        )

        # Parse ports using the standard port parsing system
        try:
            port_list = parse_port_spec(ports)
        except Exception as e:
            console.print(f"[red]Invalid port specification: {e}[/red]")
            raise typer.Exit(1)

        # Parse IMEIs - can be CSV file or comma-separated list
        try:
            imei_list = expand_csv_imeis_if_needed(imeis)
            if imei_list is None:
                # Parse as comma-separated list
                imei_list = [imei.strip() for imei in imeis.split(',') if imei.strip()]
        except CSVPortParseError as e:
            console.print(f"[red]IMEI parsing failed: {e}[/red]")
            raise typer.Exit(1)

        if not imei_list:
            console.print("[red]No valid IMEIs found[/red]")
            raise typer.Exit(1)

        # Validate we have the right number of ports and IMEIs
        if len(port_list) != len(imei_list):
            console.print("[red]Port and IMEI count mismatch:[/red]")
            console.print(f"  Ports: {len(port_list)}")
            console.print(f"  IMEIs: {len(imei_list)}")
            console.print("[yellow]Please provide exactly one IMEI for each port.[/yellow]")
            raise typer.Exit(1)

        # Extract port numbers and slots, create IMEI changes
        changes = []
        default_slot_used = False

        for port_str, imei_value in zip(port_list, imei_list, strict=False):
            try:
                port_num, slot_num = extract_port_and_slot(port_str)

                # Track if we're using default slot 1
                if slot_num == 1 and not ('.' in port_str or port_str.upper().endswith(('A', 'B', 'C', 'D'))):
                    default_slot_used = True

                change = IMEIPortChange(port=port_num, slot=slot_num, imei=imei_value)
                changes.append(change)

            except ValueError as e:
                console.print(f"[red]Invalid port format '{port_str}': {e}[/red]")
                raise typer.Exit(1)
            except Exception as e:
                console.print(f"[red]Invalid IMEI change for port '{port_str}': {e}[/red]")
                raise typer.Exit(1)

        # Warn about default slot usage and ask for confirmation if not forced
        if default_slot_used and not force:
            console.print("[yellow]⚠️  Some ports don't specify a slot - defaulting to slot 1[/yellow]")
            console.print("[dim]Ports can specify slots as: 1A, 1B, 1C, 1D or 1.01, 1.02, 1.03, 1.04[/dim]")

            if not typer.confirm("\nProceed with slot 1 as default?"):
                console.print("[dim]Operation cancelled[/dim]")
                return

        # Display summary
        console.print("\n[blue]📱 IMEI Change Summary[/blue]")
        console.print(f"Ports to modify: {len(changes)}")

        table = Table(title="IMEI Changes")
        table.add_column("Port", style="cyan")
        table.add_column("Slot", style="dim")
        table.add_column("New IMEI", style="green")

        for change in changes:
            table.add_row(
                f"{change.port}.{change.slot:02d}",
                str(change.slot),
                change.imei
            )

        console.print(table)

        if dry_run:
            console.print("\n[yellow]🔍 Dry run completed - no changes made[/yellow]")
            return

        # Confirmation
        if not force:
            console.print("\n[bold red]⚠ WARNING: This will reboot the device![/bold red]")
            console.print("[yellow]All connections will be temporarily interrupted (~90 seconds)[/yellow]")

            if not typer.confirm("\nProceed with IMEI changes?"):
                console.print("[dim]Operation cancelled[/dim]")
                return

        # Execute IMEI workflow
        client = create_sync_client(config)

        console.print("\n[blue]🎵 Starting the IMEI transformation dance...[/blue]")

        # Step 1: Set IMEI values
        console.print("[blue]Step 1/5: Setting IMEI values...[/blue]")
        changes_data = [change.dict() for change in changes]
        response = client.set_imei_batch(changes_data)
        console.print("[green]✓ IMEI values configured[/green]")

        # Step 2: Save configuration
        console.print("[blue]Step 2/5: Saving configuration...[/blue]")
        response = client.save_config()
        console.print("[green]✓ Configuration saved[/green]")

        # Step 3: Reboot device
        console.print("[blue]Step 3/5: Rebooting device...[/blue]")
        response = client.reboot_device()
        console.print("[green]✓ Reboot initiated[/green]")

        # Step 4: Wait for reboot
        console.print(f"[blue]Step 4/5: Waiting for reboot (up to {wait_timeout}s)...[/blue]")

        import time
        with console.status("[yellow]Device rebooting..."):
            if client.wait_for_reboot(timeout=wait_timeout):
                console.print("[green]✓ Device is back online[/green]")
            else:
                console.print("[yellow]⚠ Timeout waiting for device - continuing with unlock[/yellow]")

        # Give a bit more time for services to stabilize
        console.print("[dim]Waiting for services to stabilize...[/dim]")
        time.sleep(5)

        # Step 5: Unlock SIM slots
        console.print("[blue]Step 5/5: Unlocking SIM slots...[/blue]")
        slots_data = [{"port": change.port, "slot": change.slot} for change in changes]
        response = client.unlock_sims(slots_data)
        console.print("[green]✓ SIM slots unlocked[/green]")

        console.print("\n[green]🎉 IMEI transformation completed successfully![/green]")
        console.print("[dim]New IMEI values should be active. Check with: boxofports ops get-imei --ports <ports>[/dim]")

    except Exception as e:
        console.print(f"[red]IMEI workflow failed — the cosmic frequencies got tangled: {e}[/red]")
        raise typer.Exit(1)


@ops_app.command("get-imei")
def ops_get_imei(
    ctx: typer.Context,
    ports: str = typer.Option(..., "--ports", "--port", help="Ports to get IMEI for (e.g., '3A', '1A,2B,3A', or 'ports.csv')"),
    sort: str | None = typer.Option(None, "--sort", help="Sort by column numbers, e.g. '2d,3a'. Use 'a' & 'd' for ascending/descending."),
    csv: bool = typer.Option(False, "--csv", help="Export table data as CSV to stdout"),
    json_export: bool = typer.Option(False, "--json", help="Export table data as JSON to stdout"),
):
    """Get IMEI values for specified ports — check the cellular signatures."""
    config = get_config_or_exit(ctx)
    device_alias = config.device_alias or config.host

    try:
        # Check if we're in console-only export mode
        console_only_mode = csv or json_export
        
        client = create_sync_client(config)

        if not console_only_mode:
            console.print(f"[blue]Getting IMEI values for ports: {ports}[/blue]")

        response = client.get_port_imei(ports)

        if response.get("code") == 0:
            # Parse the response to extract IMEI values
            port_imeis = response.get("ports", {})
            current_profile = config_manager.get_current_profile()
            
            # Prepare data for export - use both found and requested ports
            all_port_imeis = {}
            if port_imeis:
                all_port_imeis.update(port_imeis)
            else:
                # If no ports returned, include requested ports with "Not found"
                from boxofports.ports import parse_port_spec
                requested_ports = parse_port_spec(ports)
                for port in requested_ports:
                    all_port_imeis[port] = "Not found"
                    
            # Convert to export data format
            imei_export_data = imei_data_to_export_data(all_port_imeis, device_alias=device_alias)
            
            # Show table with centralized rendering
            imei_console_only = render_and_export_table(
                title="Port IMEI Values",
                columns=get_imei_columns(),
                rows=imei_export_data,
                profile_name=current_profile,
                command_name="ops-get-imei",
                sort_option=sort,
                csv_filename=None,
                json_filename=None,
                export_csv=csv,
                export_json=json_export
            )
            
            # Show success message if not in console-only mode
            if not imei_console_only:
                console.print("[green]✓ IMEI values retrieved[/green]")
        else:
            console.print(f"[red]✗ Failed to get IMEI values: {response.get('reason', 'Unknown error')}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]IMEI query failed — the frequencies are unclear: {e}[/red]")
        raise typer.Exit(1)


@ops_app.command("imei-template")
def ops_imei_template(
    ctx: typer.Context,
    output: str = typer.Option("imei_template.csv", "--output", "-o", help="Output file path"),
    ports: str = typer.Option(None, "--ports", "--port", help="Ports to include in template (e.g., '1A,2B,3A' or CSV file)"),
    format: str = typer.Option("csv", "--format", help="Template format: csv or json"),
):
    """Generate IMEI change template file — prepare the cosmic playlist."""

    try:
        import json

        from boxofports.imei_import import export_imei_template_csv
        from boxofports.ports import parse_port_spec

        # Parse ports if specified
        port_list = None
        if ports:
            port_list = parse_port_spec(ports)

        if format.lower() == "csv":
            if not output.lower().endswith('.csv'):
                output += '.csv'
            export_imei_template_csv(output, port_list)
            console.print(f"[green]✓ CSV template created: {output}[/green]")

        elif format.lower() == "json":
            if not output.lower().endswith('.json'):
                output += '.json'

            # Create JSON template
            template_data = []

            if port_list:
                from boxofports.imei_import import _parse_port_to_number
                for port in port_list:
                    port_num = _parse_port_to_number(port)
                    template_data.append({
                        "port": port_num,
                        "slot": 1,
                        "imei": "123456789012345"
                    })
            else:
                # Default template
                for i in range(1, 4):
                    template_data.append({
                        "port": i,
                        "slot": 1,
                        "imei": "123456789012345"
                    })

            with open(output, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2)

            console.print(f"[green]✓ JSON template created: {output}[/green]")
        else:
            console.print("[red]Invalid format. Use 'csv' or 'json'[/red]")
            raise typer.Exit(1)

        console.print("[dim]Edit the file with your actual IMEI values, then use: boxofports ops set-imei --file <filename>[/dim]")

    except Exception as e:
        console.print(f"[red]Template creation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("completion")
def completion():
    """Shell completion setup guide and instructions."""
    console.print("[bold blue]🔧 BoxOfPorts Shell Completion Setup[/bold blue]\n")
    
    console.print("[yellow]Shell completion enables TAB completion for commands, options, and values.[/yellow]\n")
    
    console.print("[green]✨ Quick Install (Recommended):[/green]")
    console.print("   [cyan]boxofports --install-completion[/cyan]")
    console.print("   [dim]↳ Automatically installs completion for your current shell[/dim]\n")
    
    console.print("[green]🔍 View Completion Script:[/green]")
    console.print("   [cyan]boxofports --show-completion[/cyan]")
    console.print("   [dim]↳ Shows the completion script for manual installation[/dim]\n")
    
    console.print("[green]🛠 Manual Installation:[/green]")
    console.print("   [bold]For Bash users:[/bold]")
    console.print("   [cyan]boxofports --show-completion >> ~/.bashrc[/cyan]")
    console.print("   [cyan]source ~/.bashrc[/cyan]")
    console.print("")
    console.print("   [bold]For Zsh users:[/bold]")
    console.print("   [cyan]boxofports --show-completion >> ~/.zshrc[/cyan]")
    console.print("   [cyan]source ~/.zshrc[/cyan]\n")
    
    console.print("[blue]📋 After Installation:[/blue]")
    console.print("   1. Restart your terminal or run [cyan]source ~/.bashrc[/cyan] (or [cyan]~/.zshrc[/cyan])")
    console.print("   2. Test with: [cyan]boxofports <TAB>[/cyan]")
    console.print("   3. Try: [cyan]boxofports sms <TAB>[/cyan] or [cyan]boxofports --<TAB>[/cyan]\n")
    
    console.print("[dim]💡 Completion provides suggestions for commands, options, port numbers, and file paths.[/dim]")


@app.command("welcome")
def welcome():
    """Show welcome message with onboarding guidance."""
    # Show the beautiful splash screen with random tagline
    show_welcome_message(console)
    
    console.print("[bold green]✨ Welcome to BoxOfPorts — SMS Gateway Management CLI ✨[/bold green]")
    console.print("[dim]For EJOIN Router Operators[/dim]\n")
    
    console.print("🎯 [bold blue]Essential First Steps:[/bold blue]")
    console.print("")
    
    console.print("[yellow]1. Explore Commands:[/yellow]")
    console.print("   [cyan]boxofports help-tree[/cyan]              [dim]# Visual tree of all commands[/dim]")
    console.print("")
    
    console.print("[yellow]2. Set Up Your Gateway Profile:[/yellow]")
    console.print("   [cyan]boxofports config add-profile mygateway[/cyan] \\")
    console.print("   [cyan]     --host 192.168.1.100 --user admin --password yourpass[/cyan]")
    console.print("   [dim]# Save credentials once, use everywhere![/dim]")
    console.print("")
    
    console.print("[yellow]3. Enable Shell Completion (Highly Recommended):[/yellow]")
    console.print("   [cyan]boxofports --install-completion[/cyan]    [dim]# TAB completion for all commands[/dim]")
    console.print("   [dim]# Restart terminal, then try: boxofports <TAB>[/dim]")
    console.print("")
    
    console.print("[yellow]4. Test Your Setup:[/yellow]")
    console.print("   [cyan]boxofports test-connection[/cyan]         [dim]# Verify gateway connectivity[/dim]")
    console.print("")
    
    console.print("[yellow]5. Send Your First Test Message:[/yellow]")
    console.print("   [cyan]boxofports sms send --to \"+1234567890\"[/cyan] \\")
    console.print("   [cyan]     --text \"Hello from BoxOfPorts!\" --ports \"1A\"[/cyan]")
    console.print("")
    
    console.print("🚀 [bold blue]Quick Reference:[/bold blue]")
    console.print("   [cyan]boxofports --help[/cyan]                  [dim]# Show all commands[/dim]")
    console.print("   [cyan]boxofports <command> --help[/cyan]         [dim]# Get help for any command[/dim]")
    console.print("   [cyan]boxofports config list[/cyan]             [dim]# List your profiles[/dim]")
    console.print("   [cyan]boxofports inbox list[/cyan]              [dim]# Check received messages[/dim]")
    console.print("")
    
    console.print("📚 [bold blue]Why BoxOfPorts?[/bold blue]")
    console.print("   • [green]Profile Management[/green] - Save gateway credentials securely")
    console.print("   • [green]Template System[/green] - Dynamic SMS with Jinja2 templating")
    console.print("   • [green]Data Export[/green] - CSV/JSON export for all table commands")
    console.print("   • [green]Inbox Management[/green] - Filter, search, and analyze messages")
    console.print("   • [green]Port Operations[/green] - Lock/unlock, IMEI management")
    console.print("")
    
    console.print("[dim]🎵 Ready to let your signals ripple through the network? 🎵[/dim]")


@app.command("help-tree")
def help_tree():
    """Show complete command tree structure — the scaffolding of possibilities."""
    console.print("[bold blue]🌳 BoxOfPorts Command Tree Structure[/bold blue]\n")
    
    console.print("[cyan]boxofports[/cyan] [dim](SMS Gateway Management CLI)[/dim]")
    console.print("├── [yellow]Root Commands:[/yellow]")
    console.print("│   ├── [green]welcome[/green]              [dim]— Show welcome message & onboarding[/dim]")
    console.print("│   ├── [green]test-connection[/green]       [dim]— Test gateway connectivity[/dim]")
    console.print("│   ├── [green]completion[/green]            [dim]— Shell completion setup guide[/dim]")
    console.print("│   └── [green]help-tree[/green]             [dim]— Show this command tree[/dim]")
    console.print("│")
    console.print("├── [yellow]📱 sms[/yellow] [dim](SMS Operations)[/dim]")
    console.print("│   ├── [green]send[/green]                  [dim]— Send SMS with template support[/dim]")
    console.print("│   └── [green]spray[/green]                 [dim]— Spray SMS across multiple ports[/dim]")
    console.print("│")
    console.print("├── [yellow]📥 inbox[/yellow] [dim](Inbox Management)[/dim]")
    console.print("│   ├── [green]list[/green]                  [dim]— List received messages[/dim]")
    console.print("│   ├── [green]search[/green]                [dim]— Search messages by content[/dim]")
    console.print("│   ├── [green]stop[/green]                  [dim]— Show STOP/unsubscribe messages[/dim]")
    console.print("│   ├── [green]summary[/green]               [dim]— Inbox statistics and overview[/dim]")
    console.print("│   └── [green]show[/green]                  [dim]— Show detailed message information[/dim]")
    console.print("│")
    console.print("├── [yellow]🔧 ops[/yellow] [dim](Device Operations)[/dim]")
    console.print("│   ├── [green]lock[/green]                  [dim]— Lock specified ports[/dim]")
    console.print("│   ├── [green]unlock[/green]                [dim]— Unlock specified ports[/dim]")
    console.print("│   ├── [green]get-imei[/green]              [dim]— Get IMEI values from ports[/dim]")
    console.print("│   ├── [green]set-imei[/green]              [dim]— Set IMEI values for ports[/dim]")
    console.print("│   └── [green]imei-template[/green]         [dim]— Generate IMEI change template[/dim]")
    console.print("│")
    console.print("├── [yellow]📊 status[/yellow] [dim](Status Monitoring)[/dim]")
    console.print("│   └── [green]subscribe[/green]             [dim]— Subscribe to status notifications[/dim]")
    console.print("│")
    console.print("└── [yellow]⚙️ config[/yellow] [dim](Profile & Configuration Management)[/dim]")
    console.print("    ├── [green]add-profile[/green]          [dim]— Add new server profile[/dim]")
    console.print("    ├── [green]list[/green]                 [dim]— List all configured profiles[/dim]")
    console.print("    ├── [green]show[/green]                 [dim]— Show profile details[/dim]")
    console.print("    ├── [green]switch[/green]               [dim]— Switch to profile[/dim]")
    console.print("    ├── [green]current[/green]              [dim]— Show current profile[/dim]")
    console.print("    ├── [green]edit-profile[/green]         [dim]— Edit current profile settings[/dim]")
    console.print("    └── [green]remove[/green]               [dim]— Remove profile[/dim]")
    console.print("")
    console.print("[blue]🎯 Usage Examples:[/blue]")
    console.print("   [cyan]boxofports sms send --help[/cyan]       [dim]— Get detailed help for any command[/dim]")
    console.print("   [cyan]boxofports config list --csv[/cyan]     [dim]— Export data to CSV/JSON formats[/dim]")
    console.print("   [cyan]boxofports inbox list --sort 2d[/cyan]  [dim]— Sort output by columns[/dim]")
    console.print("")
    console.print("[blue]💡 Navigation Tips:[/blue]")
    console.print("   • Use [cyan]--help[/cyan] with any command for detailed options")
    console.print("   • Install shell completion with [cyan]boxofports --install-completion[/cyan]")
    console.print("   • All table commands support [cyan]--csv[/cyan] and [cyan]--json[/cyan] export")
    console.print("   • Use [cyan]--sort[/cyan] option to arrange output by columns")
    console.print("")
    console.print("[dim]🎵 \"Box of rain will ease the pain and love will see you through...\" 🎵[/dim]")


@app.command("test-connection")
def test_connection(ctx: typer.Context):
    """Test connection to the EJOIN device."""
    config = get_config_or_exit(ctx)

    try:
        console.print(f"[blue]Testing connection to {config.base_url}[/blue]")
        console.print(f"Username: {config.username}")

        client = create_sync_client(config)
        # Try a simple status request
        response = client.get_json("/goip_get_status.html", params={"period": "0"})

        console.print("[green]✓ Connection successful — not fade away[/green]")
        console.print("Device is awake and responding")

    except EjoinHTTPError as e:
        console.print(f"[red]✗ Signal drift detected — {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ This darkness has got to give — {e}[/red]")
        raise typer.Exit(1)


# ==============================================================================
# Configuration/Profile Management Commands
# ==============================================================================

@config_app.command("add-profile")
def config_add_profile(
    name: str = typer.Argument(..., help="Profile name"),
    host: str = typer.Option(..., "--host", help="Device IP address (supports host:port format)"),
    port: int | None = typer.Option(None, "--port", help="Device port (overrides port in host)"),
    user: str = typer.Option("root", "--user", help="Device username"),
    password: str = typer.Option(..., "--password", help="Device password"),
    alias: str | None = typer.Option(None, "--alias", help="Device alias to display in tables/exports (defaults to first word of profile name)"),
):
    """Add a new server profile."""
    try:
        # Parse host:port format if provided
        host_part, port_part = parse_host_port(host, 80)
        if port:
            port_part = port

        # Set alias to provided value or default to first word of profile name
        device_alias = alias or name.split()[0]

        profile_config = EjoinConfig(
            host=host_part,
            port=port_part,
            username=user,
            password=password,
            device_alias=device_alias
        )

        config_manager.add_profile(name, profile_config)

        console.print(f"[green]✓ Profile '{name}' ready — nothing left to do but smile, smile, smile[/green]")
        console.print(f"  Host: {profile_config.host}:{profile_config.port}")
        console.print(f"  User: {profile_config.username}")
        console.print(f"  Device Alias: {profile_config.device_alias} — will ripple through all tables")

        # Ask if user wants to switch to this profile
        if config_manager.get_current_profile() is None:
            config_manager.switch_profile(name)
            console.print("[blue]→ Set as current profile (first profile created)[/blue]")

    except Exception as e:
        console.print(f"[red]Error adding profile: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("list")
def config_list_profiles(
    sort: str | None = typer.Option(None, "--sort", help="Sort by column numbers, e.g. '2,5d,1a'. Use 'a' & 'd' for ascending/descending."),
    csv: bool = typer.Option(False, "--csv", help="Export table data as CSV to stdout"),
    json_export: bool = typer.Option(False, "--json", help="Export table data as JSON to stdout"),
):
    """List all configured profiles."""
    profiles = config_manager.list_profiles()
    current = config_manager.get_current_profile()

    if not profiles:
        console.print("[yellow]No profiles configured yet[/yellow]")
        console.print("Use 'boxofports config add-profile' to create one")
        return

    # Prepare data for export and display
    current_profile = config_manager.get_current_profile()
    profiles_data = []
    for profile_name in profiles:
        profile_config = config_manager.get_profile_config(profile_name)
        if profile_config:
            status = "→ CURRENT" if profile_name == current else ""
            profiles_data.append({
                "name": profile_name,
                "device_alias": profile_config.device_alias,
                "host_port": f"{profile_config.host}:{profile_config.port}",
                "username": profile_config.username,
                "status": status
            })

    profiles_export_data = profiles_to_export_data(profiles_data)
    
    # Show table with centralized rendering
    config_console_only = render_and_export_table(
        title="Server Profiles",
        columns=get_profiles_columns(),
        rows=profiles_export_data,
        profile_name=current_profile,
        command_name="config-list",
        sort_option=sort,
        csv_filename=None,
        json_filename=None,
        export_csv=csv,
        export_json=json_export
    )


@config_app.command("switch")
def config_switch_profile(
    name: str = typer.Argument(..., help="Profile name to switch to")
):
    """Switch to a different profile."""
    if config_manager.switch_profile(name):
        console.print(f"[green]✓ Switched to profile '{name}' — might as well[/green]")

        # Show profile details
        profile_config = config_manager.get_profile_config(name)
        if profile_config:
            console.print(f"  Host: {profile_config.host}:{profile_config.port}")
            console.print(f"  User: {profile_config.username}")
    else:
        console.print(f"[red]Error: Profile '{name}' not found[/red]")
        console.print("Use 'boxofports config list' to see available profiles")
        raise typer.Exit(1)


@config_app.command("show")
def config_show_profile(
    name: str | None = typer.Argument(None, help="Profile name (default: current profile)")
):
    """Show details of a profile."""
    if name is None:
        name = config_manager.get_current_profile()
        if name is None:
            console.print("[yellow]No current profile set[/yellow]")
            console.print("Specify a profile name or use 'boxofports config switch <name>'")
            return

    profile_config = config_manager.get_profile_config(name)
    if profile_config is None:
        console.print(f"[red]Profile '{name}' not found[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]Profile: {name}[/bold]")
    console.print(f"Host: {profile_config.host}")
    console.print(f"Port: {profile_config.port}")
    console.print(f"Username: {profile_config.username}")
    console.print(f"Password: {'*' * len(profile_config.password)}")
    console.print(f"Base URL: {profile_config.base_url}")

    if name == config_manager.get_current_profile():
        console.print("[blue]→ This is the current active profile[/blue]")


@config_app.command("remove")
def config_remove_profile(
    name: str = typer.Argument(..., help="Profile name to remove")
):
    """Remove a profile."""
    # Store the current profile before removal to detect automatic switching
    old_current = config_manager.get_current_profile()

    if config_manager.remove_profile(name):
        console.print(f"[green]✓ Profile '{name}' He is gone [/green]")

        # Check if we need to suggest a new current profile or show automatic switch
        profiles = config_manager.list_profiles()
        current = config_manager.get_current_profile()

        if current and current != old_current:
            # Automatic switch occurred (only one profile remains)
            console.print(f"[blue]→ Automatically switched to '{current}' (only remaining profile)[/blue]")
            profile_config = config_manager.get_profile_config(current)
            if profile_config:
                console.print(f"  Host: {profile_config.host}:{profile_config.port}")
                console.print(f"  User: {profile_config.username}")
        elif not current and profiles:
            console.print("[yellow]Consider switching to another profile:[/yellow]")
            for profile in profiles[:3]:
                console.print(f"  boxofports config switch {profile}")
    else:
        console.print(f"[red]Error: Profile '{name}' not found[/red]")
        raise typer.Exit(1)


@config_app.command("edit-profile")
def config_edit_profile(
    host: str | None = typer.Option(None, "--host", help="Device IP address (supports host:port format)"),
    port: int | None = typer.Option(None, "--port", help="Device port (overrides port in host)"),
    user: str | None = typer.Option(None, "--user", help="Device username"),
    password: str | None = typer.Option(None, "--password", help="Device password"),
    alias: str | None = typer.Option(None, "--alias", help="Device alias to display in tables/exports"),
):
    """Edit the currently active profile — fine-tune your cosmic connection."""
    current_profile = config_manager.get_current_profile()

    if not current_profile:
        console.print("[yellow]No current profile set to edit[/yellow]")
        profiles = config_manager.list_profiles()
        if profiles:
            console.print("Switch to a profile first:")
            for profile in profiles[:3]:
                console.print(f"  boxofports config switch {profile}")
        else:
            console.print("No profiles exist. Use 'boxofports config add-profile' to create one.")
        raise typer.Exit(1)

    try:
        # Get current profile configuration
        current_config = config_manager.get_profile_config(current_profile)
        if not current_config:
            console.print(f"[red]Error: Current profile '{current_profile}' configuration not found[/red]")
            raise typer.Exit(1)

        # Track what's being changed
        changes = []

        # Start with current values
        new_host = current_config.host
        new_port = current_config.port
        new_user = current_config.username
        new_password = current_config.password
        new_alias = current_config.device_alias

        # Apply changes if provided
        if host is not None:
            # Parse host:port format if provided
            host_part, port_part = parse_host_port(host, current_config.port)
            new_host = host_part
            new_port = port_part
            changes.append(f"Host: {current_config.host} → {new_host}")
            if port_part != current_config.port:
                changes.append(f"Port: {current_config.port} → {new_port}")

        if port is not None:
            new_port = port
            if port != current_config.port:
                changes.append(f"Port: {current_config.port} → {new_port}")

        if user is not None:
            new_user = user
            if user != current_config.username:
                changes.append(f"Username: {current_config.username} → {new_user}")

        if password is not None:
            new_password = password
            changes.append(f"Password: {'*' * len(current_config.password)} → {'*' * len(new_password)}")

        if alias is not None:
            new_alias = alias
            if alias != current_config.device_alias:
                changes.append(f"Device Alias: {current_config.device_alias} → {new_alias}")

        # Check if any changes were made
        if not changes:
            console.print(f"[yellow]No changes specified for profile '{current_profile}'[/yellow]")
            console.print("[dim]Use --help to see available options[/dim]")
            return

        # Show what will change
        console.print(f"[blue]Editing profile '{current_profile}':[/blue]")
        for change in changes:
            console.print(f"  {change}")

        # Create updated configuration
        updated_config = EjoinConfig(
            host=new_host,
            port=new_port,
            username=new_user,
            password=new_password,
            device_alias=new_alias,
            # Preserve other settings
            connect_timeout=current_config.connect_timeout,
            read_timeout=current_config.read_timeout,
            max_retries=current_config.max_retries,
            db_path=current_config.db_path,
            webhook_host=current_config.webhook_host,
            webhook_port=current_config.webhook_port,
        )

        # Save the updated profile
        config_manager.add_profile(current_profile, updated_config)

        console.print(f"[green]✓ Profile '{current_profile}' updated — the frequencies are aligned[/green]")
        console.print(f"  Host: {updated_config.host}:{updated_config.port}")
        console.print(f"  User: {updated_config.username}")
        console.print(f"  Device Alias: {updated_config.device_alias} — will ripple through all tables")

    except Exception as e:
        console.print(f"[red]Error editing profile: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("current")
def config_current_profile():
    """Show the current active profile."""
    current = config_manager.get_current_profile()
    if current:
        console.print(f"[blue]Current profile: {current}[/blue]")

        profile_config = config_manager.get_profile_config(current)
        if profile_config:
            console.print(f"  {profile_config.host}:{profile_config.port} ({profile_config.username})")
    else:
        console.print("[yellow]No current profile set[/yellow]")
        profiles = config_manager.list_profiles()
        if profiles:
            console.print("Available profiles:")
            for profile in profiles:
                console.print(f"  boxofports config switch {profile}")
        else:
            console.print("No profiles configured. Use 'boxofports config add-profile' to create one.")


# ==============================================================================
# Inbox Management Commands
# ==============================================================================

@inbox_app.command("list")
def inbox_list(
    ctx: typer.Context,
    start_id: int = typer.Option(1, "--start-id", help="Starting SMS ID"),
    count: int = typer.Option(50, "--count", help="Number of messages to show (0=all)"),
    message_type: str | None = typer.Option(None, "--type", help="Filter by message type (regular, stop, system, delivery_report)"),
    ports: str | None = typer.Option(None, "--ports", "--port", help="Filter by port(s) (e.g., '1A', '1A,2B', or 'ports.csv')"),
    sender: str | None = typer.Option(None, "--sender", help="Filter by sender number"),
    contains: str | None = typer.Option(None, "--contains", help="Filter by text content"),
    no_delivery_reports: bool = typer.Option(False, "--no-delivery-reports", help="Exclude delivery reports"),
    delivery_reports_only: bool = typer.Option(False, "--delivery-reports-only", help="Show only delivery reports"),
    status: int | None = typer.Option(None, "--status", help="Filter delivery reports by status code (0, 128, 132, 134, etc.)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    sort: str | None = typer.Option(None, "--sort", help="Sort by column numbers, e.g. '6d,4,2'. Use 'a' & 'd' for ascending/descending."),
    csv: bool = typer.Option(False, "--csv", help="Export table data as CSV to stdout"),
    json_export: bool = typer.Option(False, "--json-export", help="Export table data as JSON to stdout"),
):
    """List received SMS messages from the inbox."""
    import json

    from .api_models import MessageType, SMSInboxFilter
    from .inbox import SMSInboxService

    config = get_config_or_exit(ctx)
    device_alias = config.device_alias or config.host
    
    # Check if we're in console-only export mode
    console_only_mode = csv or json_export

    try:
        inbox_service = SMSInboxService(config)

        # Build filter criteria
        filter_criteria = SMSInboxFilter(
            exclude_delivery_reports=no_delivery_reports,
            delivery_reports_only=delivery_reports_only,
            delivery_status_code=status
        )

        if message_type:
            try:
                filter_criteria.message_type = MessageType(message_type)
            except ValueError:
                console.print(f"[red]Invalid message type: {message_type}[/red]")
                console.print(f"Valid types: {', '.join([t.value for t in MessageType])}")
                raise typer.Exit(1)

        if ports:
            # Handle CSV files and comma-separated port filtering
            try:
                from boxofports.csv_port_parser import (
                    CSVPortParseError,
                    expand_csv_ports_if_needed,
                )
                csv_ports = expand_csv_ports_if_needed(ports)
                if csv_ports is not None:
                    # CSV file - create a list of ports for filtering
                    filter_criteria.ports = csv_ports
                else:
                    # Parse as comma-separated or single port specification
                    port_list = parse_port_spec(ports)
                    if len(port_list) == 1:
                        filter_criteria.port = port_list[0]
                    else:
                        filter_criteria.ports = port_list
            except CSVPortParseError as e:
                console.print(f"[red]Port CSV parsing failed: {e}[/red]")
                raise typer.Exit(1)
            except Exception as e:
                console.print(f"[red]Port parsing failed: {e}[/red]")
                raise typer.Exit(1)
        if sender:
            filter_criteria.sender = sender
        if contains:
            filter_criteria.contains_text = contains

        # Get messages
        all_messages = inbox_service.get_messages(start_id=start_id, count=count)
        messages = inbox_service.filter_messages(all_messages, filter_criteria)

        if json_output:
            # Output as JSON
            json_data = [{
                "id": msg.id,
                "type": msg.message_type.value,
                "port": msg.port,
                "timestamp": msg.timestamp.isoformat(),
                "sender": msg.sender,
                "recipient": msg.recipient,
                "content": msg.content,
                "is_delivery_report": msg.is_delivery_report,
                "keywords": msg.contains_keywords,
                "delivery_status_code": msg.delivery_status_code,
                "delivery_phone_number": msg.delivery_phone_number
            } for msg in messages]
            console.print(json.dumps(json_data, indent=2))
            return

        if not messages:
            if not console_only_mode:
                console.print("[yellow]No messages found matching the criteria[/yellow]")
            return

        # Check if we have any delivery reports to determine table layout
        has_delivery_reports = any(msg.is_delivery_report for msg in messages)
        current_profile = config_manager.get_current_profile()
        
        # Determine message type for export formatting and column selection
        export_message_type = "standard"
        if has_delivery_reports and all(msg.is_delivery_report for msg in messages):
            export_message_type = "delivery_reports"

        # Convert messages to export data format
        messages_export_data = messages_to_export_data(messages, export_message_type, device_alias=device_alias)
        
        # Select appropriate columns based on message type
        if export_message_type == "delivery_reports":
            columns = get_inbox_delivery_reports_columns()
        else:
            columns = get_inbox_messages_columns()
        
        # Show table with centralized rendering
        inbox_console_only = render_and_export_table(
            title=f"SMS Inbox ({len(messages)} messages)",
            columns=columns,
            rows=messages_export_data,
            profile_name=current_profile,
            command_name="inbox-list",
            sort_option=sort,
            csv_filename=None,
            json_filename=None,
            export_csv=csv,
            export_json=json_export
        )

        # Show summary if not in console-only export mode
        if not inbox_console_only and len(messages) > 0:
            types_count = {}
            for msg in messages:
                types_count[msg.message_type.value] = types_count.get(msg.message_type.value, 0) + 1

            summary_parts = [f"{count} {type_name}" for type_name, count in types_count.items()]
            console.print(f"\n[dim]Summary: {', '.join(summary_parts)}[/dim]")

    except Exception as e:
        console.print(f"[red]Error retrieving inbox: {e}[/red]")
        raise typer.Exit(1)


@inbox_app.command("search")
def inbox_search(
    ctx: typer.Context,
    text: str = typer.Argument(..., help="Text to search for"),
    start_id: int = typer.Option(1, "--start-id", help="Starting SMS ID"),
    count: int = typer.Option(0, "--count", help="Max messages to search (0=all)"),
    show_details: bool = typer.Option(False, "--details", help="Show full message details"),
    sort: str | None = typer.Option(None, "--sort", help="Sort by column numbers, e.g. '6d,5a'. Use 'a' & 'd' for ascending/descending."),
    csv: bool = typer.Option(False, "--csv", help="Export table data as CSV to stdout"),
    json_export: bool = typer.Option(False, "--json-export", help="Export table data as JSON to stdout"),
):
    """Search for messages containing specific text."""
    from .inbox import SMSInboxService

    config = get_config_or_exit(ctx)
    device_alias = config.device_alias or config.host
    
    # Check for console-only export mode
    console_only_mode = csv or json_export

    try:
        inbox_service = SMSInboxService(config)
        messages = inbox_service.get_messages_containing(text, start_id=start_id)

        if not messages:
            if not console_only_mode:
                console.print(f"[yellow]No messages found containing '{text}'[/yellow]")
            return

        if not console_only_mode and not show_details:
            console.print(f"[blue]Found {len(messages)} messages containing '{text}'[/blue]")

        if show_details:
            # Show detailed view
            for i, msg in enumerate(messages[:10]):
                console.print(f"\n[bold]Message {i+1}:[/bold]")
                console.print(f"  ID: {msg.id}")
                console.print(f"  Type: {msg.message_type.value}")
                console.print(f"  Port: {msg.port}")
                console.print(f"  From: {msg.sender}")
                console.print(f"  Time: {msg.timestamp}")
                console.print(f"  Content: {msg.content}")
                if msg.contains_keywords:
                    console.print(f"  Keywords: {', '.join(msg.contains_keywords)}")
        else:
            # Show compact table with centralized rendering
            current_profile = config_manager.get_current_profile()
            messages_export_data = messages_to_export_data(messages, "search", device_alias=device_alias)
            
            # Export search results table if requested (only when showing table, not details)
            render_console_only = render_and_export_table(
                title=f"Search Results for '{text}'",
                columns=get_inbox_messages_columns(),
                rows=messages_export_data,
                profile_name=current_profile,
                command_name="inbox-search",
                sort_option=sort,
                csv_filename=None,
                json_filename=None,
                export_csv=csv,
                export_json=json_export
            )

            # Only show message count if not in console-only export mode
            if not console_only_mode and len(messages) > 20:
                console.print(f"[dim]... and {len(messages) - 20} more messages[/dim]")

    except Exception as e:
        console.print(f"[red]Error searching inbox: {e}[/red]")
        raise typer.Exit(1)


@inbox_app.command("stop")
def inbox_stop(
    ctx: typer.Context,
    start_id: int = typer.Option(1, "--start-id", help="Starting SMS ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    sort: str | None = typer.Option(None, "--sort", help="Sort by column numbers, e.g. '6d,4'. Use 'a' & 'd' for ascending/descending."),
    csv: bool = typer.Option(False, "--csv", help="Export table data as CSV to stdout"),
    json_export: bool = typer.Option(False, "--json-export", help="Export table data as JSON to stdout"),
):
    """Show all STOP/unsubscribe messages."""
    import json

    from .inbox import SMSInboxService

    config = get_config_or_exit(ctx)
    device_alias = config.device_alias or config.host
    
    # Check for console-only export mode
    console_only_mode = csv or json_export

    try:
        inbox_service = SMSInboxService(config)
        messages = inbox_service.get_stop_messages(start_id=start_id)

        if not messages:
            if not console_only_mode:
                console.print("[green]No STOP messages found[/green]")
            return

        if not console_only_mode:
            console.print(f"[red]Found {len(messages)} STOP messages[/red]")

        if json_output:
            json_data = [{
                "id": msg.id,
                "port": msg.port,
                "timestamp": msg.timestamp.isoformat(),
                "sender": msg.sender,
                "content": msg.content
            } for msg in messages]
            console.print(json.dumps(json_data, indent=2))
            return

        # Show table with centralized rendering
        current_profile = config_manager.get_current_profile()
        messages_export_data = messages_to_export_data(messages, "stop", device_alias=device_alias)
        
        render_console_only = render_and_export_table(
            title="🛑 STOP Messages",
            columns=get_inbox_messages_columns(),
            rows=messages_export_data,
            profile_name=current_profile,
            command_name="inbox-stop",
            sort_option=sort,
            csv_filename=None,
            json_filename=None,
            export_csv=csv,
            export_json=json_export
        )

        # Only show warning message if not in console-only export mode
        if not console_only_mode:
            console.print(f"\n[bold red]⚠️  {len(messages)} users have requested to stop receiving messages[/bold red]")

    except Exception as e:
        console.print(f"[red]Error retrieving STOP messages: {e}[/red]")
        raise typer.Exit(1)


@inbox_app.command("summary")
def inbox_summary(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show inbox statistics and summary."""
    import json

    from .inbox import SMSInboxService

    config = get_config_or_exit(ctx)

    try:
        inbox_service = SMSInboxService(config)
        summary = inbox_service.get_inbox_summary()

        if json_output:
            # Convert set to list for JSON serialization
            summary_copy = summary.copy()
            if isinstance(summary_copy.get("recent_senders"), set):
                summary_copy["recent_senders"] = list(summary_copy["recent_senders"])
            console.print(json.dumps(summary_copy, indent=2))
            return

        # Display formatted summary
        console.print("[bold]📧 SMS Inbox Summary[/bold]\n")

        console.print(f"Total Messages: [cyan]{summary['total_messages']}[/cyan]")

        if summary['total_messages'] > 0:
            console.print(f"Regular Messages: [green]{summary['regular_messages']}[/green]")
            console.print(f"Delivery Reports: [blue]{summary['delivery_reports']}[/blue]")
            console.print(f"STOP Messages: [red]{summary['stop_messages']}[/red]")

            # Message types breakdown
            console.print("\n[bold]By Type:[/bold]")
            for msg_type, count in summary['by_type'].items():
                if count > 0:
                    console.print(f"  {msg_type}: {count}")

            # Port breakdown
            if summary['by_port']:
                console.print("\n[bold]By Port:[/bold]")
                for port, count in sorted(summary['by_port'].items()):
                    console.print(f"  Port {port}: {count} messages")

            # Date range
            if summary['date_range']:
                console.print("\n[bold]Date Range:[/bold]")
                console.print(f"  Earliest: {summary['date_range']['earliest']}")
                console.print(f"  Latest: {summary['date_range']['latest']}")

            # Recent senders
            if summary['recent_senders']:
                console.print(f"\n[bold]Recent Senders ({len(summary['recent_senders'])}):[/bold]")
                for sender in list(summary['recent_senders'])[:10]:
                    console.print(f"  {sender}")
                if len(summary['recent_senders']) > 10:
                    console.print(f"  ... and {len(summary['recent_senders']) - 10} more")

    except Exception as e:
        console.print(f"[red]Error getting inbox summary: {e}[/red]")
        raise typer.Exit(1)


@inbox_app.command("show")
def inbox_show(
    ctx: typer.Context,
    message_id: int = typer.Argument(..., help="Message ID to show details for"),
    start_id: int = typer.Option(1, "--start-id", help="Starting SMS ID for search"),
):
    """Show detailed information about a specific message."""
    from .inbox import SMSInboxService

    config = get_config_or_exit(ctx)

    try:
        inbox_service = SMSInboxService(config)
        messages = inbox_service.get_messages(start_id=start_id)

        # Find message with the specified ID
        message = None
        for msg in messages:
            if msg.id == message_id:
                message = msg
                break

        if not message:
            console.print(f"[red]Message with ID {message_id} not found[/red]")
            return

        # Display detailed message info
        console.print(f"[bold]📱 Message Details (ID: {message.id})[/bold]\n")

        console.print(f"[bold]Type:[/bold] {message.message_type.value}")
        console.print(f"[bold]Port:[/bold] {message.port}")
        console.print(f"[bold]Timestamp:[/bold] {message.timestamp}")
        console.print(f"[bold]From:[/bold] {message.sender}")

        if message.recipient:
            console.print(f"[bold]To:[/bold] {message.recipient}")

        console.print(f"[bold]Is Delivery Report:[/bold] {'Yes' if message.is_delivery_report else 'No'}")

        if message.contains_keywords:
            console.print(f"[bold]Keywords:[/bold] {', '.join(message.contains_keywords)}")

        console.print("\n[bold]Content:[/bold]")
        console.print(f"[white]{message.content}[/white]")

        if message.raw_content != message.content:
            console.print("\n[bold]Raw Content:[/bold]")
            console.print(f"[dim]{message.raw_content}[/dim]")

    except Exception as e:
        console.print(f"[red]Error showing message: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
