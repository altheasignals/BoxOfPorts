#!/usr/bin/env bash
# Test script for BoxOfPorts CLI completion (both boxofports and boxofports)
# "What a long, strange trip completion has been..."

set -e

echo "🎸 Testing BoxOfPorts CLI Tab Completion 🎸"
echo "=============================================="
echo ""

# Source the completion scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOP_COMPLETION_SCRIPT="${SCRIPT_DIR}/bop-completion.bash"
BOXOFPORTS_COMPLETION_SCRIPT="${SCRIPT_DIR}/boxofports-completion.bash"

if [[ ! -f "$BOP_COMPLETION_SCRIPT" ]]; then
    echo "❌ Docker wrapper completion script not found at: $BOP_COMPLETION_SCRIPT"
    exit 1
fi

if [[ ! -f "$BOXOFPORTS_COMPLETION_SCRIPT" ]]; then
    echo "❌ Local CLI completion script not found at: $BOXOFPORTS_COMPLETION_SCRIPT"
    exit 1
fi

echo "📋 Testing Docker wrapper (bop) completion..."
source "$BOP_COMPLETION_SCRIPT"

# Function to test completion
test_completion() {
    local test_name="$1"
    shift
    
    # Properly set up completion arrays
    declare -a COMP_WORDS=("$@")
    COMP_CWORD=${#COMP_WORDS[@]}
    COMP_LINE="${COMP_WORDS[*]} "
    
    # Clear previous results
    COMPREPLY=()
    
    # Call completion function
    _bop_completion
    
    local actual_count=${#COMPREPLY[@]}
    if [[ $actual_count -gt 0 ]]; then
        echo "✅ $test_name: ${COMPREPLY[*]}"
    else
        echo "❌ $test_name: No completions found"
    fi
}

echo "Testing main commands..."
test_completion "Main commands" "bop"

echo ""
echo "Testing subcommands..."
test_completion "SMS subcommands" "bop" "sms"
test_completion "Inbox subcommands" "bop" "inbox"
test_completion "Config subcommands" "bop" "config"
test_completion "Ops subcommands" "bop" "ops"
test_completion "Status subcommands" "bop" "status"

echo ""
echo "Testing command options..."
test_completion "SMS send options" "bop" "sms" "send"
test_completion "Inbox list options" "bop" "inbox" "list"

echo ""
echo "Testing value completions..."
test_completion "Message types" "bop" "inbox" "list" "--type"
test_completion "Port examples" "bop" "sms" "send" "--ports"

echo ""
echo "📋 Testing local CLI (boxofports) completion..."
source "$BOXOFPORTS_COMPLETION_SCRIPT"

# Function to test boxofports completion
test_boxofports_completion() {
    local test_name="$1"
    shift
    
    # Properly set up completion arrays
    declare -a COMP_WORDS=("$@")
    COMP_CWORD=${#COMP_WORDS[@]}
    COMP_LINE="${COMP_WORDS[*]} "
    
    # Clear previous results
    COMPREPLY=()
    
    # Call completion function
    _boxofports_completion
    
    local actual_count=${#COMPREPLY[@]}
    if [[ $actual_count -gt 0 ]]; then
        echo "✅ $test_name: ${COMPREPLY[*]}"
    else
        echo "❌ $test_name: No completions found"
    fi
}

echo "Testing boxofports main commands..."
test_boxofports_completion "Main commands" "boxofports"

echo ""
echo "Testing boxofports subcommands..."
test_boxofports_completion "SMS subcommands" "boxofports" "sms"
test_boxofports_completion "Config subcommands" "boxofports" "config"

echo ""
echo "🎵 Completion tests complete! 🎵"
echo ""
echo "To test interactively in your shell:"
echo "Docker wrapper (bop):"
echo "1. Run: source ${BOP_COMPLETION_SCRIPT}"
echo "2. Type: bop <TAB><TAB>"
echo "3. Type: boxofports sms <TAB><TAB>"
echo ""
echo "Local CLI (boxofports):"
echo "1. Run: source ${BOXOFPORTS_COMPLETION_SCRIPT}"
echo "2. Type: boxofports <TAB><TAB>"
echo "3. Type: boxofports inbox list --type <TAB><TAB>"
echo ""
echo "Keep on truckin' with your tab completions! 🚂"
