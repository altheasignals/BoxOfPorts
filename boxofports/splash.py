"""Splash screen and taglines for BoxOfPorts welcome message."""

import random
from rich.console import Console

# All taglines (combining standard + vibe taglines from the original splash.py)
ALL_TAGLINES = [
    # Standard (professional) taglines
    "It's just a box of ports — let it flow.",
    "Messages ripple — ports respond.",
    "Send the signal — hear the song.",
    "This is the box you build your network in.",
    "Signals drift — this box holds steady.",
    "Every port a path, every signal a song.",
    "Build your system, and watch it grow.",
    "There is a gateway — the signal shines through.",
    "It's just a box of ports — but it's yours.",
    "Port by port, the signal finds its way.",
    
    # Vibe taglines (formerly behind --vibe flag)
    "Trouble ahead, trouble behind... port locked.",
    "You know this space is getting hot... (retrying port)",
    "This port's been here so long it's got to calling out your name.",
    "Waiting for the signal to blow you back again...",
    "Don't you push me, 'cause I'm close to the edge (of rate limit).",
]

def get_random_tagline() -> str:
    """Get a random tagline from the complete collection."""
    return random.choice(ALL_TAGLINES)

def print_ascii_banner(console: Console):
    """Print ASCII banner using rich formatting."""
    console.print("""[bold blue]
 ██████╗  ██████╗ ██╗  ██╗ ██████╗ ███████╗██████╗  ██████╗ ██████╗ ████████╗███████╗
 ██╔══██╗██╔═══██╗╚██╗██╔╝██╔═══██╗██╔════╝██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝
 ██████╔╝██║   ██║ ╚███╔╝ ██║   ██║█████╗  ██████╔╝██║   ██║██████╔╝   ██║   ███████╗
 ██╔══██╗██║   ██║ ██╔██╗ ██║   ██║██╔══╝  ██╔═══╝ ██║   ██║██╔══██╗   ██║   ╚════██║
 ██████╔╝╚██████╔╝██╔╝ ██╗╚██████╔╝██║     ██║     ╚██████╔╝██║  ██║   ██║   ███████║
 ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝[/bold blue]""")

def show_welcome_message(console: Console):
    """Show the complete welcome message with banner and tagline."""
    # Print the ASCII banner
    print_ascii_banner(console)
    
    # Show tagline
    tagline = get_random_tagline()
    console.print(f"\n[italic dim]  {tagline}[/italic dim]\n")