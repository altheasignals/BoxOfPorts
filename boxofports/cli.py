"""CLI interface for BoxOfPorts using Typer."""

import hashlib
import random
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .config import config_manager, parse_host_port, EjoinConfig
from .http import create_sync_client, EjoinHTTPError
from .ports import parse_port_spec, format_ports_for_api
from .store import initialize_store, get_store
from .templating import render_sms_template, parse_template_variables
from .__version__ import get_full_version_info

app = typer.Typer(help="BoxOfPorts - SMS Gateway Management CLI for EJOIN Router Operators")
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
        
    except Exception as e:
        console.print(f"[yellow]🎵 Hey now! Gateway configuration needed for this command[/yellow]")
        console.print("")
        console.print("[blue]→ Quick setup with a profile:[/blue]")
        console.print("   bop config add-profile mygateway \\")
        console.print("     --host 192.168.1.100 --user admin --password yourpass")
        console.print("")
        console.print("[blue]→ Or set environment variables:[/blue]")
        console.print("   export EJOIN_HOST=192.168.1.100")
        console.print("   export EJOIN_USER=admin")
        console.print("   export EJOIN_PASSWORD=yourpass")
        console.print("")
        console.print("[blue]→ Or use CLI options:[/blue]")
        console.print("   bop --host 192.168.1.100 --user admin --password yourpass <command>")
        console.print("")
        console.print("[dim]Run 'bop config --help' for more configuration options[/dim]")
        raise typer.Exit(1)


def version_callback(value: bool):
    """Print version information and exit."""
    if value:
        console.print(get_full_version_info())
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    host: Optional[str] = typer.Option(None, "--host", help="Device IP address"),
    port: Optional[int] = typer.Option(None, "--port", help="Device port"),
    user: Optional[str] = typer.Option(None, "--user", help="Device username"),
    password: Optional[str] = typer.Option(None, "--pass", "--password", help="Device password"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Enable verbose logging"),
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, is_eager=True, help="Show version information"),
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
    config_free_commands = {'completion', 'config'}
    
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
    ports: str = typer.Option(..., "--ports", help="Ports to send from (e.g., '1A,2B' or '4-8')"),
    repeat: int = typer.Option(1, "--repeat", help="Number of times to repeat"),
    intvl_ms: int = typer.Option(500, "--intvl-ms", help="Interval between SMS in milliseconds"),
    timeout: int = typer.Option(30, "--timeout", help="Timeout in seconds"),
    vars: List[str] = typer.Option([], "--var", help="Template variables (key=value)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be sent without sending"),
):
    """Send test SMS with template support and per-port routing."""
    config = get_config_or_exit(ctx)
    
    try:
        # Parse ports and template variables
        port_list = parse_port_spec(ports)
        template_vars = parse_template_variables(vars) if vars else {}
        
        console.print(f"[blue]Sending SMS to {to} via {len(port_list)} ports[/blue]")
        
        if dry_run:
            console.print("[yellow]DRY RUN - Not actually sending[/yellow]")
        
        # Create tasks
        tasks = []
        tid_base = random.randint(1000, 9999)
        
        for repeat_idx in range(repeat):
            for port_idx, port in enumerate(port_list):
                tid = tid_base + (repeat_idx * len(port_list)) + port_idx
                
                # Render template for this port
                rendered_text = render_sms_template(text, port, port_idx, **template_vars)
                
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
        
        # Show preview table
        table = Table(title="SMS Tasks")
        table.add_column("TID", style="cyan")
        table.add_column("Port", style="green")
        table.add_column("To", style="yellow")
        table.add_column("Text", style="white")
        table.add_column("Status", style="blue")
        
        for task in tasks[:10]:  # Show first 10 tasks
            table.add_row(
                str(task['tid']),
                task['from'],
                task['to'],
                task['sms'][:50] + "..." if len(task['sms']) > 50 else task['sms'],
                "DRY RUN" if dry_run else "PENDING"
            )
        
        if len(tasks) > 10:
            table.add_row("...", "...", "...", f"... and {len(tasks) - 10} more", "...")
        
        console.print(table)
        
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
                
                # Update table with results
                result_table = Table(title="SMS Send Results")
                result_table.add_column("TID", style="cyan")
                result_table.add_column("Status", style="blue")
                
                for status in response.get('status', []):
                    tid = status['tid']
                    status_text = status['status']
                    result_table.add_row(str(tid), status_text)
                    
                    # Update local storage
                    store.update_task_status(tid, status_text)
                
                console.print(result_table)
                
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
    ports: str = typer.Option(..., "--ports", help="Ports to spray from"),
    intvl_ms: int = typer.Option(250, "--intvl-ms", help="Interval between SMS"),
):
    """Spray the same number via multiple ports quickly."""
    # This is essentially the same as send but with different defaults
    ctx.invoke(sms_send, ctx, to=to, text=text, ports=ports, repeat=1, intvl_ms=intvl_ms, timeout=30, vars=[], dry_run=False)


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
        
        console.print(f"[green]✓ Webhook subscription configured[/green]")
        console.print(f"[yellow]ℹ  This REPLACES any previous webhook subscription[/yellow]")
        console.print("")
        console.print(f"📡 Callback URL: {callback}")
        console.print(f"⏰ Reports every: {period} seconds")
        console.print(f"📱 Includes: All SIM card statuses, signal levels, carrier info")
        console.print("")
        console.print(f"[dim]The device will now send comprehensive status reports to your callback URL[/dim]")
        console.print(f"[dim]To stop notifications: bop status subscribe --callback '' --period 0[/dim]")
        
    except EjoinHTTPError as e:
        console.print(f"[red]The music stoped — {e}[/red]")
        raise typer.Exit(1)


@ops_app.command("lock")
def ops_lock(
    ctx: typer.Context,
    ports: str = typer.Option(..., "--ports", help="Ports to lock"),
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
    ports: str = typer.Option(..., "--ports", help="Ports to unlock"),
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


@app.command("completion")
def completion(
    shell: str = typer.Option("bash", "--shell", help="Shell type (bash, zsh)"),
    install: bool = typer.Option(False, "--install", help="Install completion for current user"),
):
    """Generate shell completion script or install completion."""
    import os
    from pathlib import Path
    
    completion_script = '''#!/usr/bin/env bash
# BoxOfPorts (bop) CLI completion script
# "Such a long long time to be gone, and a short time to be there"

_bop_completion() {
    local cur prev
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main commands
    local main_commands="sms ops status inbox config test-connection completion"
    
    case ${COMP_CWORD} in
        1)
            COMPREPLY=($(compgen -W "${main_commands} --host --port --user --password --verbose --version --help" -- ${cur}))
            ;;
        2)
            case "${prev}" in
                sms) COMPREPLY=($(compgen -W "send spray" -- ${cur})) ;;
                ops) COMPREPLY=($(compgen -W "lock unlock" -- ${cur})) ;;
                status) COMPREPLY=($(compgen -W "subscribe" -- ${cur})) ;;
                inbox) COMPREPLY=($(compgen -W "list search stop summary show" -- ${cur})) ;;
                config) COMPREPLY=($(compgen -W "add-profile list switch show remove current" -- ${cur})) ;;
                completion) COMPREPLY=($(compgen -W "--shell --install" -- ${cur})) ;;
            esac
            ;;
        *)
            # Context-aware completions for options
            case "${prev}" in
                --shell) COMPREPLY=($(compgen -W "bash zsh" -- ${cur})) ;;
                --type) COMPREPLY=($(compgen -W "regular stop system delivery_report" -- ${cur})) ;;
                --ports) COMPREPLY=($(compgen -W "1A 1B 1C 1D 2A 2B 1A-1D 1.01 2.02" -- ${cur})) ;;
            esac
            ;;
    esac
}

complete -F _bop_completion bop

# ZSH compatibility
if [[ -n ${ZSH_VERSION-} ]]; then
    autoload -U +X bashcompinit && bashcompinit
    complete -F _bop_completion bop
fi'''
    
    if install:
        # Install completion for current user
        user_shell = os.path.basename(os.environ.get('SHELL', 'bash'))
        home = Path.home()
        
        if user_shell == 'zsh' or shell == 'zsh':
            # Try common zsh completion directories
            for comp_dir in [
                home / ".zsh" / "completions",
                home / ".oh-my-zsh" / "completions",
                Path("/usr/local/share/zsh/site-functions"),
            ]:
                try:
                    comp_dir.mkdir(parents=True, exist_ok=True)
                    comp_file = comp_dir / "_bop"
                    comp_file.write_text(completion_script)
                    console.print(f"[green]✓ Zsh completion installed to {comp_file}[/green]")
                    console.print("[dim]Restart your shell or open a new terminal to activate completion[/dim]")
                    console.print("[dim]If completion doesn't work, try: exec zsh[/dim]")
                    return
                except (PermissionError, OSError):
                    continue
        
        else:  # bash
            # Try common bash completion directories
            for comp_dir in [
                home / ".bash_completion.d",
                Path("/usr/local/etc/bash_completion.d"),
                Path("/etc/bash_completion.d"),
            ]:
                try:
                    comp_dir.mkdir(parents=True, exist_ok=True)
                    comp_file = comp_dir / "bop"
                    comp_file.write_text(completion_script)
                    console.print(f"[green]✓ Bash completion installed to {comp_file}[/green]")
                    console.print("[dim]Restart your shell or open a new terminal to activate completion[/dim]")
                    console.print("[dim]If completion doesn't work, try: exec bash[/dim]")
                    return
                except (PermissionError, OSError):
                    continue
        
        # Fallback: save to home directory
        fallback_file = home / ".bop-completion.bash"
        fallback_file.write_text(completion_script)
        console.print(f"[yellow]✓ Completion saved to {fallback_file}[/yellow]")
        console.print(f"[dim]Add this line to your shell config (~/.bashrc or ~/.zshrc):[/dim]")
        console.print(f"[cyan]source {fallback_file}[/cyan]")
        console.print("[dim]Then restart your shell or run: exec $SHELL[/dim]")
    
    else:
        # Just print the completion script
        console.print(completion_script)


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
        console.print(f"Device is awake and responding")
        
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
    port: Optional[int] = typer.Option(None, "--port", help="Device port (overrides port in host)"),
    user: str = typer.Option("root", "--user", help="Device username"),
    password: str = typer.Option(..., "--password", help="Device password"),
):
    """Add a new server profile."""
    try:
        # Parse host:port format if provided
        host_part, port_part = parse_host_port(host, 80)
        if port:
            port_part = port
        
        profile_config = EjoinConfig(
            host=host_part,
            port=port_part,
            username=user,
            password=password
        )
        
        config_manager.add_profile(name, profile_config)
        
        console.print(f"[green]✓ Profile '{name}' ready — nothing left to do but smile, smile, smile[/green]")
        console.print(f"  Host: {profile_config.host}:{profile_config.port}")
        console.print(f"  User: {profile_config.username}")
        
        # Ask if user wants to switch to this profile
        if config_manager.get_current_profile() is None:
            config_manager.switch_profile(name)
            console.print(f"[blue]→ Set as current profile (first profile created)[/blue]")
        
    except Exception as e:
        console.print(f"[red]Error adding profile: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("list")
def config_list_profiles():
    """List all configured profiles."""
    profiles = config_manager.list_profiles()
    current = config_manager.get_current_profile()
    
    if not profiles:
        console.print("[yellow]No profiles configured yet[/yellow]")
        console.print("Use 'bop config add-profile' to create one")
        return
    
    table = Table(title="Server Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Host:Port", style="green")
    table.add_column("Username", style="yellow")
    table.add_column("Status", style="blue")
    
    for profile_name in profiles:
        profile_config = config_manager.get_profile_config(profile_name)
        if profile_config:
            status = "→ CURRENT" if profile_name == current else ""
            table.add_row(
                profile_name,
                f"{profile_config.host}:{profile_config.port}",
                profile_config.username,
                status
            )
    
    console.print(table)


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
        console.print("Use 'bop config list' to see available profiles")
        raise typer.Exit(1)


@config_app.command("show")
def config_show_profile(
    name: Optional[str] = typer.Argument(None, help="Profile name (default: current profile)")
):
    """Show details of a profile."""
    if name is None:
        name = config_manager.get_current_profile()
        if name is None:
            console.print("[yellow]No current profile set[/yellow]")
            console.print("Specify a profile name or use 'bop config switch <name>'")
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
            console.print(f"[yellow]Consider switching to another profile:[/yellow]")
            for profile in profiles[:3]:
                console.print(f"  bop config switch {profile}")
    else:
        console.print(f"[red]Error: Profile '{name}' not found[/red]")
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
                console.print(f"  bop config switch {profile}")
        else:
            console.print("No profiles configured. Use 'bop config add-profile' to create one.")


# ==============================================================================
# Inbox Management Commands 
# ==============================================================================

@inbox_app.command("list")
def inbox_list(
    ctx: typer.Context,
    start_id: int = typer.Option(1, "--start-id", help="Starting SMS ID"),
    count: int = typer.Option(50, "--count", help="Number of messages to show (0=all)"),
    message_type: Optional[str] = typer.Option(None, "--type", help="Filter by message type (regular, stop, system, delivery_report)"),
    port: Optional[str] = typer.Option(None, "--port", help="Filter by port (e.g., 1A, 2B)"),
    sender: Optional[str] = typer.Option(None, "--sender", help="Filter by sender number"),
    contains: Optional[str] = typer.Option(None, "--contains", help="Filter by text content"),
    no_delivery_reports: bool = typer.Option(False, "--no-delivery-reports", help="Exclude delivery reports"),
    delivery_reports_only: bool = typer.Option(False, "--delivery-reports-only", help="Show only delivery reports"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List received SMS messages from the inbox."""
    from .inbox import SMSInboxService
    from .api_models import MessageType, SMSInboxFilter
    import json
    
    config = get_config_or_exit(ctx)
    
    try:
        inbox_service = SMSInboxService(config)
        
        # Build filter criteria
        filter_criteria = SMSInboxFilter(
            exclude_delivery_reports=no_delivery_reports,
            delivery_reports_only=delivery_reports_only
        )
        
        if message_type:
            try:
                filter_criteria.message_type = MessageType(message_type)
            except ValueError:
                console.print(f"[red]Invalid message type: {message_type}[/red]")
                console.print(f"Valid types: {', '.join([t.value for t in MessageType])}")
                raise typer.Exit(1)
        
        if port:
            filter_criteria.port = port
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
                "keywords": msg.contains_keywords
            } for msg in messages]
            console.print(json.dumps(json_data, indent=2))
            return
        
        if not messages:
            console.print("[yellow]No messages found matching the criteria[/yellow]")
            return
        
        # Display table
        table = Table(title=f"SMS Inbox ({len(messages)} messages)")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Type", style="blue", width=10)
        table.add_column("Port", style="green", width=6)
        table.add_column("From", style="yellow", width=15)
        table.add_column("Time", style="magenta", width=16)
        table.add_column("Content", style="white")
        
        for msg in messages:
            # Format message type with emoji
            type_display = {
                MessageType.REGULAR: "📱 Regular",
                MessageType.STOP: "🛑 STOP",
                MessageType.SYSTEM: "⚙️ System",
                MessageType.DELIVERY_REPORT: "✅ Delivery",
                MessageType.KEYWORD: "🔍 Keyword"
            }.get(msg.message_type, msg.message_type.value)
            
            # Truncate long content
            content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
            
            # Format timestamp
            time_str = msg.timestamp.strftime("%m-%d %H:%M")
            
            table.add_row(
                str(msg.id),
                type_display,
                msg.port,
                msg.sender[-12:] if len(msg.sender) > 12 else msg.sender,  # Show last 12 chars
                time_str,
                content
            )
        
        console.print(table)
        
        # Show summary
        if len(messages) > 0:
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
):
    """Search for messages containing specific text."""
    from .inbox import SMSInboxService
    
    config = get_config_or_exit(ctx)
    
    try:
        inbox_service = SMSInboxService(config)
        messages = inbox_service.get_messages_containing(text, start_id=start_id)
        
        if not messages:
            console.print(f"[yellow]No messages found containing '{text}'[/yellow]")
            return
        
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
            # Show compact table
            table = Table(title=f"Search Results for '{text}'")
            table.add_column("ID", style="cyan")
            table.add_column("Port", style="green")
            table.add_column("From", style="yellow")
            table.add_column("Time", style="magenta")
            table.add_column("Content", style="white")
            
            for msg in messages[:20]:  # Limit to first 20
                content = msg.content[:60] + "..." if len(msg.content) > 60 else msg.content
                table.add_row(
                    str(msg.id),
                    msg.port,
                    msg.sender[-10:],
                    msg.timestamp.strftime("%m-%d %H:%M"),
                    content
                )
            
            console.print(table)
            
            if len(messages) > 20:
                console.print(f"[dim]... and {len(messages) - 20} more messages[/dim]")
    
    except Exception as e:
        console.print(f"[red]Error searching inbox: {e}[/red]")
        raise typer.Exit(1)


@inbox_app.command("stop")
def inbox_stop(
    ctx: typer.Context,
    start_id: int = typer.Option(1, "--start-id", help="Starting SMS ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show all STOP/unsubscribe messages."""
    from .inbox import SMSInboxService
    import json
    
    config = get_config_or_exit(ctx)
    
    try:
        inbox_service = SMSInboxService(config)
        messages = inbox_service.get_stop_messages(start_id=start_id)
        
        if not messages:
            console.print("[green]No STOP messages found[/green]")
            return
        
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
        
        table = Table(title="🛑 STOP Messages")
        table.add_column("ID", style="cyan")
        table.add_column("Port", style="green")
        table.add_column("From", style="yellow")
        table.add_column("Time", style="magenta")
        table.add_column("Content", style="red")
        
        for msg in messages:
            table.add_row(
                str(msg.id),
                msg.port,
                msg.sender,
                msg.timestamp.strftime("%m-%d %H:%M:%S"),
                msg.content
            )
        
        console.print(table)
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
    from .inbox import SMSInboxService
    import json
    
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
                console.print(f"\n[bold]Date Range:[/bold]")
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
        
        console.print(f"\n[bold]Content:[/bold]")
        console.print(f"[white]{message.content}[/white]")
        
        if message.raw_content != message.content:
            console.print(f"\n[bold]Raw Content:[/bold]")
            console.print(f"[dim]{message.raw_content}[/dim]")
    
    except Exception as e:
        console.print(f"[red]Error showing message: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
