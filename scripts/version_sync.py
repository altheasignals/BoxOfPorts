#!/usr/bin/env python3
"""
Version Synchronization Script for BoxOfPorts
"Keeping all the versions in harmony, like instruments in a band"

This script reads from version_registry.json and updates all files
throughout the repository to maintain version consistency.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


class VersionSync:
    def __init__(self, registry_path: str = "version_registry.json"):
        self.registry_path = registry_path
        self.repo_root = Path(__file__).parent.parent
        self.registry = self._load_registry()
        self.errors: List[str] = []
        self.updates: List[str] = []
        
    def _load_registry(self) -> Dict[str, Any]:
        """Load the central version registry."""
        registry_file = self.repo_root / self.registry_path
        if not registry_file.exists():
            raise FileNotFoundError(f"Version registry not found: {registry_file}")
            
        with open(registry_file, 'r') as f:
            return json.load(f)
    
    def _update_file(self, file_path: Path, updates: Dict[str, str], description: str = None):
        """Update a file with version replacements."""
        if not file_path.exists():
            self.errors.append(f"File not found: {file_path}")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            for pattern, replacement in updates.items():
                content = re.sub(pattern, replacement, content)
                
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.updates.append(f"Updated {file_path.relative_to(self.repo_root)}" + 
                                  (f" - {description}" if description else ""))
            else:
                print(f"No changes needed: {file_path.relative_to(self.repo_root)}")
                
        except Exception as e:
            self.errors.append(f"Error updating {file_path}: {e}")
    
    def sync_python_version_files(self):
        """Sync Python version files."""
        stable_version = self.registry["versions"]["stable"]
        constants = self.registry["constants"]
        
        # Update __version__.py
        version_file = self.repo_root / "boxofports" / "__version__.py"
        updates = {
            r'__version__ = "[^"]*"': f'__version__ = "{stable_version}"',
            r'__title__ = "[^"]*"': f'__title__ = "{constants["title"]}"',
            r'__command__ = "[^"]*"': f'__command__ = "{constants["command"]}"',
            r'__description__ = "[^"]*"': f'__description__ = "{constants["description"]}"',
            r'__author__ = "[^"]*"': f'__author__ = "{constants["author"]}"',
            r'__author_email__ = "[^"]*"': f'__author_email__ = "{constants["author_email"]}"',
            r'__url__ = "[^"]*"': f'__url__ = "{constants["url"]}"',
            r'__license__ = "[^"]*"': f'__license__ = "{constants["license"]}"',
            r'__api_version__ = "[^"]*"': f'__api_version__ = "{self.registry["versions"]["api"]}"',
            r'__python_requires__ = "[^"]*"': f'__python_requires__ = "{constants["python_requires"]}"',
            r'__inspiration__ = "[^"]*"': f'__inspiration__ = "{constants["inspiration"]}"',
        }
        self._update_file(version_file, updates, "Python version constants")
        
        # Update __init__.py
        init_file = self.repo_root / "boxofports" / "__init__.py"
        init_updates = {
            r'__version__ = "[^"]*"': f'__version__ = "{stable_version}"',
            r'__author__ = "[^"]*"': f'__author__ = "{constants["author"]}"',
            r'__email__ = "[^"]*"': f'__email__ = "{constants["author_email"]}"',
            r'__license__ = "[^"]*"': f'__license__ = "{constants["license"]}"',
        }
        self._update_file(init_file, init_updates, "Package init version")
        
        # Update pyproject.toml with stable version
        pyproject_file = self.repo_root / "pyproject.toml"
        pyproject_updates = {
            r'version = "[^"]*"': f'version = "{stable_version}"',
            r'description = "[^"]*"': f'description = "{constants["description"]}"',
        }
        self._update_file(pyproject_file, pyproject_updates, "Python package version")
    
    def sync_docker_files(self):
        """Sync Docker-related files."""
        stable_version = self.registry["versions"]["stable"]
        
        # Update Dockerfile
        dockerfile = self.repo_root / "Dockerfile"
        dockerfile_updates = {
            r'LABEL version="[^"]*"': f'LABEL version="{stable_version}"',
            r'LABEL org\.opencontainers\.image\.version="[^"]*"': 
                f'LABEL org.opencontainers.image.version="{stable_version}"',
        }
        self._update_file(dockerfile, dockerfile_updates, "Docker version labels")
    
    def sync_installation_scripts(self):
        """Sync installation and utility scripts."""
        stable_version = self.registry["versions"]["stable"]
        
        scripts_dir = self.repo_root / "scripts"
        scripts_to_update = [
            "install-user.sh",
            "install-system.sh", 
            "install-dev.sh",
            "install.sh",
            "install.ps1",
            "retag_by_digest.sh",
            "bop-completion.bash",
            "boxofports-completion.bash"
        ]
        
        version_patterns = {
            r'VERSION="[^"]*"': f'VERSION="{stable_version}"',
            r'version="[^"]*"': f'version="{stable_version}"',
            r'VERSION=[0-9]+\.[0-9]+\.[0-9]+': f'VERSION={stable_version}',
            r'v[0-9]+\.[0-9]+\.[0-9]+': f'v{stable_version}',
            r'[0-9]+\.[0-9]+\.[0-9]+ \(example': f'{stable_version} (example',
        }
        
        for script_name in scripts_to_update:
            script_path = scripts_dir / script_name
            if script_path.exists():
                self._update_file(script_path, version_patterns, f"Script version references")
    
    def sync_bop_wrapper(self):
        """Sync bop wrapper version."""
        # Use development version for bop wrapper to keep it in sync with main releases
        bop_version = self.registry["versions"]["development"]
        
        # Update main bop script version header
        bop_script = self.repo_root / "scripts" / "bop"
        bop_updates = {
            r'# bop \(Docker wrapper\) v[0-9]+\.[0-9]+\.[0-9]+': f'# bop (Docker wrapper) v{bop_version}',
            r'echo "bop \(Docker wrapper\) v[^"]*"': f'echo "bop (Docker wrapper) v{bop_version}"',
        }
        self._update_file(bop_script, bop_updates, "Bop wrapper version")
        
        # Update the registry to keep bop_wrapper version in sync
        self.registry["bop_wrapper"]["version"] = bop_version
        
        # Update docker/bop if it exists
        docker_bop = self.repo_root / "docker" / "bop"
        if docker_bop.exists():
            self._update_file(docker_bop, bop_updates, "Docker bop wrapper version")
    
    def sync_documentation(self):
        """Sync documentation files."""
        stable_version = self.registry["versions"]["stable"]
        dev_version = self.registry["versions"]["development"]
        
        docs_dir = self.repo_root / "docs"
        doc_patterns = {
            # Update version examples in documentation
            r'1\.2\.0(?=\s|$|,|\.|\)|\]|\})': stable_version,
            r'1\.2\.1(?=\s|$|,|\.|\)|\]|\})': dev_version,
            r'version [0-9]+\.[0-9]+\.[0-9]+': f'version {stable_version}',
            r'Version [0-9]+\.[0-9]+\.[0-9]+': f'Version {stable_version}',
        }
        
        # Update specific documentation files
        doc_files = [
            "README.md",
            "docs/VERSIONING.md", 
            "docs/ROLLBACK.md",
            "docs/DISTRIBUTION.md",
        ]
        
        for doc_file in doc_files:
            doc_path = self.repo_root / doc_file
            if doc_path.exists():
                self._update_file(doc_path, doc_patterns, "Documentation version examples")
    
    def sync_workflows(self):
        """Sync GitHub workflow files."""
        stable_version = self.registry["versions"]["stable"]
        
        workflows_dir = self.repo_root / ".github" / "workflows"
        
        # Update workflow files with version examples
        workflow_patterns = {
            r'target_version: [0-9]+\.[0-9]+\.[0-9]+': f'target_version: {stable_version}',
            r'version: [0-9]+\.[0-9]+\.[0-9]+': f'version: {stable_version}',
            r'1\.2\.0(?=\s|\)|,|"|\')': stable_version,
        }
        
        workflow_files = [
            "promote-stable.yml",
            "publish-on-tag.yml", 
            "bump-version.yml",
            "version-lint.yml"
        ]
        
        for workflow_file in workflow_files:
            workflow_path = workflows_dir / workflow_file
            if workflow_path.exists():
                self._update_file(workflow_path, workflow_patterns, "Workflow version references")
    
    def update_registry_timestamp(self):
        """Update the registry timestamp to mark when sync was performed."""
        self.registry["_meta"]["updated"] = datetime.now(timezone.utc).isoformat()
        
        registry_file = self.repo_root / self.registry_path
        with open(registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
        
        self.updates.append(f"Updated registry timestamp: {registry_file.name}")
    
    def sync_all(self):
        """Perform complete version synchronization."""
        print("🎵 Starting comprehensive version synchronization...")
        print(f"Stable version: {self.registry['versions']['stable']}")
        print(f"Development version: {self.registry['versions']['development']}")
        print()
        
        # Sync all categories
        self.sync_python_version_files()
        self.sync_docker_files() 
        self.sync_installation_scripts()
        self.sync_bop_wrapper()
        self.sync_documentation()
        self.sync_workflows()
        
        # Update timestamp
        self.update_registry_timestamp()
        
        # Report results
        print("\n🎯 Synchronization Results:")
        print(f"✅ Updates made: {len(self.updates)}")
        for update in self.updates:
            print(f"  • {update}")
        
        if self.errors:
            print(f"\n⚠️ Errors encountered: {len(self.errors)}")
            for error in self.errors:
                print(f"  • {error}")
            return False
        else:
            print("\n🌊 All versions synchronized successfully!")
            print("The rhythm stays tight, all instruments in harmony.")
            return True


def main():
    """Main execution function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        print("🔍 Dry run mode - no files will be modified")
        return
    
    sync = VersionSync()
    success = sync.sync_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()