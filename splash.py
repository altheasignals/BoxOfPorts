#!/usr/bin/env python3

import random
import subprocess
import sys

# 🎨 Main (professional) taglines
standard_taglines = [
    "It’s just a box of ports — let it flow.",
    "Messages ripple — ports respond.",
    "Send the signal — hear the song.",
    "This is the box you build your network in.",
    "Signals drift — this box holds steady.",
    "Every port a path, every signal a song.",
    "Build your system, and watch it grow.",
    "There is a gateway — the signal shines through.",
    "It’s just a box of ports — but it’s yours.",
    "Port by port, the signal finds its way."
]

# 🌀 Easter egg taglines for --vibe mode
vibe_taglines = [
    "Trouble ahead, trouble behind... port locked.",
    "You know this space is getting hot... (retrying port)",
    "This port’s been here so long it’s got to calling out your name.",
    "Waiting for the signal to blow you back again...",
    "Don’t you push me, ‘cause I’m close to the edge (of rate limit)."
]

def get_tagline(vibe=False):
    taglines = standard_taglines + vibe_taglines if vibe else standard_taglines
    return random.choice(taglines)

def print_ascii_banner():
    try:
        # Use toilet to render "BoxOfPorts" in large ASCII text
        subprocess.run(['toilet', '--gay', 'BoxOfPorts'], check=True)
    except FileNotFoundError:
        print("[!] 'toilet' command not found. Please install it with 'apt install toilet' or 'brew install toilet'.")
        sys.exit(1)

def main():
    vibe_mode = '--vibe' in sys.argv
    tagline = get_tagline(vibe=vibe_mode)

    print_ascii_banner()
    print(f"\n  {tagline}\n")

if __name__ == "__main__":
    main()

