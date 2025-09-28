#!/usr/bin/env python3
"""
Manual Version Registry Update Script for BoxOfPorts
"Sometimes you need to tune the instruments by hand"

This script allows manual updates to the version registry and syncs all files.
Usage: python3 scripts/update_version_registry.py [--stable VERSION] [--dev VERSION] [--sync-only]
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def trigger_publish_workflow(version, github_token):
    """Trigger the publish-on-tag workflow for a specific version."""
    print(f"🚀 Triggering publish-on-tag workflow for v{version}...")
    
    try:
        # Trigger the workflow_dispatch for publish-on-tag.yml
        trigger_cmd = [
            'curl', '-s', '-X', 'POST',
            '-H', f'Authorization: token {github_token}',
            '-H', 'Accept: application/vnd.github.v3+json',
            '-H', 'Content-Type: application/json',
            f'https://api.github.com/repos/altheasignals/boxofports/actions/workflows/publish-on-tag.yml/dispatches',
            '-d', json.dumps({
                'ref': 'main',
                'inputs': {
                    'version': version
                }
            })
        ]
        
        result = subprocess.run(trigger_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to trigger workflow: {result.stderr}")
            return False
            
        # A successful dispatch returns empty response with 204 status
        print(f"✅ Workflow dispatch request sent successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error triggering workflow: {e}")
        return False


def promote_github_release(version):
    """Promote a GitHub release from prerelease to stable (non-prerelease)."""
    print(f"🏷️ Attempting to promote GitHub release v{version} to stable...")
    
    # Check if GITHUB_TOKEN is available
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("⚠️  No GITHUB_TOKEN found - skipping GitHub release promotion")
        print("   To enable GitHub release promotion, set GITHUB_TOKEN environment variable")
        return True  # Not a failure, just skip
    
    try:
        # First, check if the release exists
        check_cmd = [
            'curl', '-s', '-H', f'Authorization: token {github_token}',
            f'https://api.github.com/repos/altheasignals/boxofports/releases/tags/v{version}'
        ]
        
        result = subprocess.run(check_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to check GitHub release: {result.stderr}")
            return False
            
        release_data = json.loads(result.stdout)
        if 'id' not in release_data:
            print(f"⚠️  No GitHub release found for v{version}")
            print(f"   Attempting to trigger publish-on-tag workflow to create release...")
            
            # Try to trigger the publish-on-tag workflow
            workflow_success = trigger_publish_workflow(version, github_token)
            if workflow_success:
                print(f"   Workflow triggered successfully - waiting for release creation...")
                # Wait a bit for the workflow to complete
                import time
                time.sleep(10)
                
                # Try to check for the release again
                result = subprocess.run(check_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    release_data = json.loads(result.stdout)
                    if 'id' in release_data:
                        print(f"✅ Release created successfully by workflow")
                    else:
                        print(f"❌ Release still not found after workflow trigger")
                        return False
                else:
                    print(f"❌ Failed to verify release creation after workflow")
                    return False
            else:
                print(f"❌ Could not trigger workflow - manual intervention required")
                return False
            
        release_id = release_data['id']
        current_prerelease = release_data.get('prerelease', True)
        
        if not current_prerelease:
            print(f"✅ Release v{version} is already marked as stable (non-prerelease)")
            return True
            
        # Update the release to set prerelease: false
        update_cmd = [
            'curl', '-s', '-X', 'PATCH',
            '-H', f'Authorization: token {github_token}',
            '-H', 'Content-Type: application/json',
            f'https://api.github.com/repos/altheasignals/boxofports/releases/{release_id}',
            '-d', json.dumps({'prerelease': False})
        ]
        
        result = subprocess.run(update_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to update GitHub release: {result.stderr}")
            return False
            
        updated_data = json.loads(result.stdout)
        if updated_data.get('prerelease') == False:
            print(f"✅ Successfully promoted GitHub release v{version} to stable")
            print(f"   Release is now available via GitHub's /releases/latest API")
            return True
        else:
            print(f"❌ Failed to update release prerelease status")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse GitHub API response: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error promoting GitHub release: {e}")
        return False


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
        
        # Also promote the corresponding GitHub release
        print("\n🔄 Promoting corresponding GitHub release...")
        github_success = promote_github_release(stable_version)
        if not github_success:
            print("⚠️  GitHub release promotion failed, but registry update will continue")
    
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