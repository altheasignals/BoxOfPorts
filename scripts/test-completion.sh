#!/usr/bin/env bash
# Test script for bop CLI completion
# "What a long, strange trip completion has been..."

set -e

echo "🎸 Testing BoxOfPorts CLI Tab Completion 🎸"
echo "=============================================="
echo ""

# Source the completion script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPLETION_SCRIPT="${SCRIPT_DIR}/bop-completion.bash"

if [[ ! -f "$COMPLETION_SCRIPT" ]]; then
    echo "❌ Completion script not found at: $COMPLETION_SCRIPT"
    exit 1
fi

source "$COMPLETION_SCRIPT"

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
echo "🎵 Completion tests complete! 🎵"
echo ""
echo "To test interactively in your shell:"
echo "1. Run: source ${COMPLETION_SCRIPT}"
echo "2. Type: bop <TAB><TAB>"
echo "3. Type: bop sms <TAB><TAB>"
echo "4. Type: bop inbox list --type <TAB><TAB>"
echo ""
echo "Keep on truckin' with your tab completions! 🚂"