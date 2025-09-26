#!/usr/bin/env python3
"""
Test script for CSV/JSON export functionality in BoxOfPorts CLI

This script tests the new --csv and --json export options to ensure they work correctly
in both console output mode (for pipelines) and file output mode.
"""

import os
import tempfile
import subprocess
import json
import csv
from pathlib import Path


def run_command(cmd):
    """Run a command and return stdout, stderr, and exit code."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1


def test_console_csv_output():
    """Test that --csv outputs CSV to console without other output."""
    print("🧪 Testing console CSV output...")
    
    # This should output only CSV data to stdout
    stdout, stderr, code = run_command("boxofports config list --csv")
    
    if code != 0:
        print(f"   ❌ Command failed with code {code}: {stderr}")
        return False
    
    # Check if output looks like CSV (has headers)
    lines = stdout.strip().split('\n')
    if len(lines) < 1:
        print("   ❌ No output received")
        return False
    
    # First line should be CSV headers
    first_line = lines[0]
    if ',' not in first_line or 'Name' not in first_line:
        print(f"   ❌ Output doesn't look like CSV headers: {first_line}")
        return False
    
    print("   ✅ Console CSV output looks correct")
    return True


def test_console_json_output():
    """Test that --json outputs JSON to console without other output."""
    print("🧪 Testing console JSON output...")
    
    # This should output only JSON data to stdout
    stdout, stderr, code = run_command("boxofports config list --json")
    
    if code != 0:
        print(f"   ❌ Command failed with code {code}: {stderr}")
        return False
    
    # Try to parse as JSON
    try:
        data = json.loads(stdout)
        if not isinstance(data, list):
            print(f"   ❌ JSON output is not a list: {type(data)}")
            return False
    except json.JSONDecodeError as e:
        print(f"   ❌ Output is not valid JSON: {e}")
        print(f"   Output was: {stdout[:100]}...")
        return False
    
    print("   ✅ Console JSON output looks correct")
    return True


def test_file_csv_output():
    """Test that --csv filename.csv creates a file and shows normal output."""
    print("🧪 Testing file CSV output...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_file = os.path.join(tmpdir, "test_profiles.csv")
        
        # This should create a file and show normal output
        stdout, stderr, code = run_command(f"boxofports config list --csv {csv_file}")
        
        if code != 0:
            print(f"   ❌ Command failed with code {code}: {stderr}")
            return False
        
        # Check if file was created
        if not os.path.exists(csv_file):
            print(f"   ❌ CSV file was not created: {csv_file}")
            return False
        
        # Check if file has content
        with open(csv_file, 'r') as f:
            content = f.read().strip()
            if not content or ',' not in content:
                print(f"   ❌ CSV file doesn't contain valid CSV data")
                return False
        
        # Check if stdout contains confirmation message
        if "CSV export written to:" not in stdout and "✓" not in stdout:
            print(f"   ❌ Normal output doesn't contain expected confirmation")
            return False
        
        print("   ✅ File CSV output works correctly")
        return True


def test_file_json_output():
    """Test that --json filename.json creates a file and shows normal output."""
    print("🧪 Testing file JSON output...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = os.path.join(tmpdir, "test_profiles.json")
        
        # This should create a file and show normal output
        stdout, stderr, code = run_command(f"boxofports config list --json {json_file}")
        
        if code != 0:
            print(f"   ❌ Command failed with code {code}: {stderr}")
            return False
        
        # Check if file was created
        if not os.path.exists(json_file):
            print(f"   ❌ JSON file was not created: {json_file}")
            return False
        
        # Check if file has valid JSON content
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    print(f"   ❌ JSON file doesn't contain list data")
                    return False
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON file doesn't contain valid JSON: {e}")
            return False
        
        # Check if stdout contains confirmation message
        if "JSON export written to:" not in stdout and "✓" not in stdout:
            print(f"   ❌ Normal output doesn't contain expected confirmation")
            return False
        
        print("   ✅ File JSON output works correctly")
        return True


def main():
    """Run all tests."""
    print("🎵 Testing BoxOfPorts CSV/JSON Export Functionality 🎵")
    print("=" * 60)
    
    tests = [
        test_console_csv_output,
        test_console_json_output,
        test_file_csv_output,
        test_file_json_output,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   💥 Test crashed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The export functionality is working like a Garcia solo!")
        return 0
    else:
        print("😞 Some tests failed. The music needs some tuning...")
        return 1


if __name__ == "__main__":
    exit(main())