#!/usr/bin/env python3
"""
Manual Version Registry Update Script for BoxOfPorts
"Sometimes you need to tune the instruments by hand"

This script allows manual updates to the version registry and syncs all files.
Usage: python3 scripts/update_version_registry.py [--stable VERSION] [--dev VERSION] [--sync-only]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def update_registry(stable_version=None, dev_version=None, sync_only=False):
    """Update the version registry and optionally sync files."""
    repo_root = Path(__file__).parent.parent
    registry_file = repo_root / "version_registry.json"
    
    if not registry_file.exists():
        print("❌ Version registry not found!")
        return False
    
    # Load current registry
    with open(registry_file, 'r') as f:
        registry = json.load(f)
    
    current_stable = registry["versions"]["stable"]
    current_dev = registry["versions"]["development"]
    
    print(f"🎵 Current versions:")
    print(f"  Stable:      {current_stable}")
    print(f"  Development: {current_dev}")
    print()
    
    changes_made = False
    
    # Update versions if provided
    if stable_version:
        print(f"📝 Updating stable version: {current_stable} → {stable_version}")
        registry["versions"]["stable"] = stable_version
        registry["release_info"]["stable"]["version"] = stable_version
        registry["release_info"]["stable"]["released"] = datetime.now(timezone.utc).isoformat()
        changes_made = True
    
    if dev_version:
        print(f"📝 Updating development version: {current_dev} → {dev_version}")
        registry["versions"]["development"] = dev_version
        registry["release_info"]["development"]["version"] = dev_version
        registry["release_info"]["development"]["released"] = datetime.now(timezone.utc).isoformat()
        changes_made = True
    
    # Update timestamp
    registry["_meta"]["updated"] = datetime.now(timezone.utc).isoformat()
    
    # Save registry
    if changes_made or sync_only:
        with open(registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
        
        if changes_made:
            print("✅ Registry updated successfully")
        
        # Run version sync
        print("\n🔄 Running version synchronization...")
        import subprocess
        result = subprocess.run([sys.executable, "scripts/version_sync.py"], 
                               cwd=repo_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Version synchronization completed")
            print(result.stdout)
        else:
            print("❌ Version synchronization failed")
            print(result.stderr)
            return False
    else:
        print("ℹ️  No changes specified")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Update BoxOfPorts version registry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update stable version to 1.3.0
  python3 scripts/update_version_registry.py --stable 1.3.0
  
  # Update development version to 1.2.5
  python3 scripts/update_version_registry.py --dev 1.2.5
  
  # Update both versions
  python3 scripts/update_version_registry.py --stable 1.3.0 --dev 1.3.1
  
  # Just sync files without changing versions
  python3 scripts/update_version_registry.py --sync-only
"""
    )
    
    parser.add_argument("--stable", help="New stable version (e.g., 1.3.0)")
    parser.add_argument("--dev", help="New development version (e.g., 1.2.5)")
    parser.add_argument("--sync-only", action="store_true", 
                       help="Only sync files, don't update versions")
    
    args = parser.parse_args()
    
    if not args.stable and not args.dev and not args.sync_only:
        parser.print_help()
        sys.exit(1)
    
    # Validate version formats
    import re
    version_pattern = r'^\d+\.\d+\.\d+$'
    
    if args.stable and not re.match(version_pattern, args.stable):
        print("❌ Invalid stable version format. Use X.Y.Z (e.g., 1.3.0)")
        sys.exit(1)
    
    if args.dev and not re.match(version_pattern, args.dev):
        print("❌ Invalid development version format. Use X.Y.Z (e.g., 1.2.5)")
        sys.exit(1)
    
    success = update_registry(args.stable, args.dev, args.sync_only)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()