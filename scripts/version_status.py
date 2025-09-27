#!/usr/bin/env python3
"""
Version Status Checker for BoxOfPorts
"Like checking the tuning of all instruments before the show"

This script checks version consistency across all files and shows the current state.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any


class VersionChecker:
    def __init__(self, registry_path: str = "version_registry.json"):
        self.registry_path = registry_path
        self.repo_root = Path(__file__).parent.parent
        self.registry = self._load_registry()
        
    def _load_registry(self) -> Dict[str, Any]:
        """Load the central version registry."""
        registry_file = self.repo_root / self.registry_path
        if not registry_file.exists():
            raise FileNotFoundError(f"Version registry not found: {registry_file}")
            
        with open(registry_file, 'r') as f:
            return json.load(f)
    
    def _extract_version_from_file(self, file_path: Path, patterns: List[str]) -> List[str]:
        """Extract versions from a file using regex patterns."""
        if not file_path.exists():
            return []
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            versions = []
            for pattern in patterns:
                matches = re.findall(pattern, content)
                versions.extend(matches)
                
            return versions
        except Exception:
            return []
    
    def check_python_versions(self) -> Dict[str, List[str]]:
        """Check Python version files."""
        results = {}
        
        # Check __version__.py
        version_file = self.repo_root / "boxofports" / "__version__.py"
        results["__version__.py"] = self._extract_version_from_file(
            version_file, [r'__version__ = "([^"]*)"']
        )
        
        # Check __init__.py  
        init_file = self.repo_root / "boxofports" / "__init__.py"
        results["__init__.py"] = self._extract_version_from_file(
            init_file, [r'__version__ = "([^"]*)"']
        )
        
        # Check pyproject.toml
        pyproject_file = self.repo_root / "pyproject.toml"
        results["pyproject.toml"] = self._extract_version_from_file(
            pyproject_file, [r'version = "([^"]*)"']
        )
        
        return results
    
    def check_docker_versions(self) -> Dict[str, List[str]]:
        """Check Docker version references."""
        results = {}
        
        # Check Dockerfile
        dockerfile = self.repo_root / "Dockerfile"
        results["Dockerfile"] = self._extract_version_from_file(
            dockerfile, [
                r'LABEL version="([^"]*)"',
                r'LABEL org\.opencontainers\.image\.version="([^"]*)"'
            ]
        )
        
        return results
    
    def check_bop_versions(self) -> Dict[str, List[str]]:
        """Check bop wrapper versions."""
        results = {}
        
        # Check main bop script
        bop_script = self.repo_root / "scripts" / "bop"
        results["scripts/bop"] = self._extract_version_from_file(
            bop_script, [r'bop \(Docker wrapper\) v([^"]*)"']
        )
        
        # Check docker/bop
        docker_bop = self.repo_root / "docker" / "bop"
        results["docker/bop"] = self._extract_version_from_file(
            docker_bop, [r'bop \(Docker wrapper\) v([^"]*)"']
        )
        
        return results
    
    def display_version_summary(self):
        """Display a comprehensive version summary."""
        print("🎵 BoxOfPorts Version Status")
        print("=" * 50)
        print()
        
        # Central registry
        print("📋 CENTRAL REGISTRY:")
        print(f"  Stable version:      {self.registry['versions']['stable']}")
        print(f"  Development version: {self.registry['versions']['development']}")
        print(f"  API version:         {self.registry['versions']['api']}")
        print(f"  Bop wrapper:         {self.registry['bop_wrapper']['version']}")
        print(f"  Last updated:        {self.registry['_meta']['updated']}")
        print()
        
        # Docker tags
        print("🐳 DOCKER TAG MAPPING:")
        docker_info = self.registry['docker']
        print(f"  {docker_info['image_name']}:stable  → {self.registry['versions']['stable']}")
        print(f"  {docker_info['image_name']}:latest  → {self.registry['versions']['development']}")
        print()
        
        # File versions
        print("📁 FILE VERSIONS:")
        
        # Python versions
        python_versions = self.check_python_versions()
        print("  Python Package:")
        for file_name, versions in python_versions.items():
            version_str = ", ".join(versions) if versions else "Not found"
            status = "✅" if versions and versions[0] == self.registry['versions']['stable'] else "⚠️"
            print(f"    {status} {file_name:<20} {version_str}")
        
        # Docker versions
        docker_versions = self.check_docker_versions()
        print("\n  Docker:")
        for file_name, versions in docker_versions.items():
            version_str = ", ".join(versions) if versions else "Not found"
            status = "✅" if versions and versions[0] == self.registry['versions']['stable'] else "⚠️"
            print(f"    {status} {file_name:<20} {version_str}")
        
        # Bop versions
        bop_versions = self.check_bop_versions()
        print("\n  Bop Wrapper:")
        for file_name, versions in bop_versions.items():
            version_str = ", ".join(versions) if versions else "Not found"
            expected = self.registry['bop_wrapper']['version']
            status = "✅" if versions and versions[0] == expected else "⚠️"
            print(f"    {status} {file_name:<20} {version_str}")
        
        print()
        
        # Check consistency
        all_python_consistent = all(
            versions and versions[0] == self.registry['versions']['stable'] 
            for versions in python_versions.values()
        )
        
        all_bop_consistent = all(
            versions and versions[0] == self.registry['bop_wrapper']['version']
            for versions in bop_versions.values() if versions
        )
        
        print("🎯 CONSISTENCY STATUS:")
        if all_python_consistent and all_bop_consistent:
            print("  ✅ All versions are synchronized")
            print("  🌊 The harmony flows perfectly!")
        else:
            print("  ⚠️  Version inconsistencies detected")
            print("  💡 Run 'python3 scripts/version_sync.py' to fix")
        
        print()


def main():
    """Main execution function."""
    checker = VersionChecker()
    checker.display_version_summary()


if __name__ == "__main__":
    main()