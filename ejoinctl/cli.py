"""CLI interface for ejoinctl using Typer."""

import hashlib
import random
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .config import config_manager, parse_host_port
from .http import create_sync_client, EjoinHTTPError
from .ports import parse_port_spec, format_ports_for_api
from .store import initialize_store, get_store
from .templating import render_sms_template, parse_template_variables

app = typer.Typer(help="CLI tool for EJOIN Multi-WAN Router HTTP API v2.2")
sms_app = typer.Typer(help="SMS operations")
ops_app = typer.Typer(help="Device operations") 
status_app = typer.Typer(help="Status monitoring")
inbox_app = typer.Typer(help="Inbox management")

app.add_typer(sms_app, name="sms")
app.add_typer(ops_app, name="ops") 
app.add_typer(status_app, name="status")
app.add_typer(inbox_app, name="inbox")

console = Console()


@app.callback()
def main(
    ctx: typer.Context,
    host: Optional[str] = typer.Option(None, "--host", help="Device IP address"),
    port: Optional[int] = typer.Option(None, "--port", help="Device port"),
    user: Optional[str] = typer.Option(None, "--user", help="Device username"),
    password: Optional[str] = typer.Option(None, "--pass", "--password", help="Device password"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Enable verbose logging"),
):
    """ejoinctl - CLI tool for EJOIN Multi-WAN Router."""
    try:
        config = config_manager.get_config()
        
        # Override config with command line arguments if provided
        if host:
            # Parse host:port format if provided
            host_part, port_part = parse_host_port(host, config.port)
            config.host = host_part
            config.port = port_part
        if port:
            config.port = port
        if user:
            config.username = user
        if password:
            config.password = password
        
        # Initialize store
        initialize_store(config.db_path)
        
        # Store config in context for subcommands
        ctx.ensure_object(dict)
        ctx.obj['config'] = config
        ctx.obj['verbose'] = verbose
        
    except Exception as e:
        console.print(f"[red]Error initializing ejoinctl: {e}[/red]")
        raise typer.Exit(1)


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
    config = ctx.obj['config']
    
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
                console.print(f"[red]SMS send failed: {e}[/red]")
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
    all_sims: bool = typer.Option(False, "--all-sims", help="Get all SIM card status"),
):
    """Subscribe to device/port status notifications."""
    config = ctx.obj['config']
    
    try:
        client = create_sync_client(config)
        params = {
            "url": callback,
            "period": period,
        }
        if all_sims:
            params["all_sims"] = "1"
        
        response = client.get_json("/goip_get_status.html", params=params)
        console.print(f"[green]Status subscription configured successfully[/green]")
        console.print(f"Callback URL: {callback}")
        console.print(f"Report period: {period} seconds")
        console.print(f"All SIMs: {'Yes' if all_sims else 'No'}")
        
    except EjoinHTTPError as e:
        console.print(f"[red]Failed to subscribe to status: {e}[/red]")
        raise typer.Exit(1)


@ops_app.command("lock")
def ops_lock(
    ctx: typer.Context,
    ports: str = typer.Option(..., "--ports", help="Ports to lock"),
):
    """Lock specified ports."""
    config = ctx.obj['config']
    
    try:
        port_list = parse_port_spec(ports)
        client = create_sync_client(config)
        
        request_data = {
            "type": "command",
            "op": "lock", 
            "ports": format_ports_for_api(port_list)
        }
        
        response = client.post_json("/goip_send_cmd.html", json=request_data)
        console.print(f"[green]Lock command sent to ports: {', '.join(port_list)}[/green]")
        
    except Exception as e:
        console.print(f"[red]Lock operation failed: {e}[/red]")
        raise typer.Exit(1)


@ops_app.command("unlock")
def ops_unlock(
    ctx: typer.Context,
    ports: str = typer.Option(..., "--ports", help="Ports to unlock"),
):
    """Unlock specified ports."""
    config = ctx.obj['config']
    
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


@app.command("test-connection")
def test_connection(ctx: typer.Context):
    """Test connection to the EJOIN device."""
    config = ctx.obj['config']
    
    try:
        console.print(f"[blue]Testing connection to {config.base_url}[/blue]")
        console.print(f"Username: {config.username}")
        
        client = create_sync_client(config)
        # Try a simple status request
        response = client.get_json("/goip_get_status.html", params={"period": "0"})
        
        console.print("[green]✓ Connection successful![/green]")
        console.print(f"Device appears to be responding normally")
        
    except EjoinHTTPError as e:
        console.print(f"[red]✗ Connection failed: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Unexpected error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()