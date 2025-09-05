#!/usr/bin/env python3
"""
VS Code Terminal Configuration Helper
Automatically detects and configures Git Bash terminal for VS Code to fix exit code 256 issue.
"""

import json
import os
import platform
import shutil
from pathlib import Path
from datetime import datetime


class VSCodeTerminalFixer:
    """Fix VS Code terminal configuration for Git Bash."""
    
    def __init__(self):
        self.vscode_dir = Path(".vscode")
        self.settings_file = self.vscode_dir / "settings.json"
        self.git_paths = self._get_git_bash_paths()
    
    def _get_git_bash_paths(self):
        """Get potential Git Bash installation paths."""
        if platform.system() != "Windows":
            return []
        
        potential_paths = [
            "C:\\Program Files\\Git\\git-bash.exe",
            "C:\\Program Files\\Git\\bin\\bash.exe", 
            "C:\\Program Files (x86)\\Git\\git-bash.exe",
            "C:\\Program Files (x86)\\Git\\bin\\bash.exe",
            os.path.expandvars("${USERPROFILE}\\AppData\\Local\\Programs\\Git\\git-bash.exe"),
            os.path.expandvars("${USERPROFILE}\\AppData\\Local\\Programs\\Git\\bin\\bash.exe"),
            "C:\\Program Files\\Git\\usr\\bin\\bash.exe",
            "C:\\Program Files (x86)\\Git\\usr\\bin\\bash.exe"
        ]
        
        return potential_paths
    
    def detect_git_bash(self):
        """Detect available Git Bash installation."""
        print("🔍 Detecting Git Bash installation...")
        
        for path in self.git_paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                print(f"✅ Found Git Bash at: {expanded_path}")
                return expanded_path
        
        print("❌ No Git Bash installation found in standard locations")
        return None
    
    def create_backup(self):
        """Create backup of existing settings."""
        if self.settings_file.exists():
            backup_path = str(self.settings_file) + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.settings_file, backup_path)
            print(f"📋 Backup created: {backup_path}")
            return backup_path
        return None
    
    def load_existing_settings(self):
        """Load existing VS Code settings."""
        if not self.settings_file.exists():
            return {}
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  Error reading existing settings: {e}")
            return {}
    
    def create_terminal_profiles(self, detected_git_path=None):
        """Create comprehensive terminal profiles for Windows."""
        profiles = {
            "PowerShell": {
                "source": "PowerShell",
                "icon": "terminal-powershell"
            },
            "Command Prompt": {
                "path": [
                    "${env:windir}\\Sysnative\\cmd.exe",
                    "${env:windir}\\System32\\cmd.exe"
                ],
                "args": [],
                "icon": "terminal-cmd"
            }
        }
        
        # Add Git Bash profiles
        if detected_git_path:
            profiles["Git Bash"] = {
                "path": detected_git_path,
                "icon": "terminal-bash"
            }
        
        # Add fallback Git Bash profiles
        git_bash_profiles = {
            "Git Bash (git-bash.exe)": {
                "path": "C:\\Program Files\\Git\\git-bash.exe",
                "icon": "terminal-bash"
            },
            "Git Bash (bash.exe)": {
                "path": "C:\\Program Files\\Git\\bin\\bash.exe",
                "args": ["--login", "-i"],
                "icon": "terminal-bash"
            },
            "Git Bash (User Install)": {
                "path": "${env:USERPROFILE}\\AppData\\Local\\Programs\\Git\\git-bash.exe",
                "icon": "terminal-bash"
            },
            "Git Bash (x86)": {
                "path": "C:\\Program Files (x86)\\Git\\git-bash.exe",
                "icon": "terminal-bash"
            }
        }
        
        # Only add profiles that don't duplicate the detected one
        for name, config in git_bash_profiles.items():
            if not detected_git_path or config["path"] != detected_git_path:
                profiles[name] = config
        
        return profiles
    
    def fix_terminal_configuration(self):
        """Fix VS Code terminal configuration."""
        print("🔧 Fixing VS Code Terminal Configuration")
        print("=" * 50)
        
        # Ensure .vscode directory exists
        self.vscode_dir.mkdir(exist_ok=True)
        
        # Create backup
        self.create_backup()
        
        # Detect Git Bash
        detected_git = self.detect_git_bash()
        
        # Load existing settings
        settings = self.load_existing_settings()
        
        # Create terminal profiles
        terminal_profiles = self.create_terminal_profiles(detected_git)
        
        # Update settings
        settings.update({
            "terminal.integrated.profiles.windows": terminal_profiles,
            "terminal.integrated.defaultProfile.windows": "Git Bash" if detected_git else "PowerShell",
            "terminal.integrated.detectLocale": "off",
            "terminal.integrated.shell.windows": None,
            "terminal.integrated.shellArgs.windows": None
        })
        
        # Add additional helpful settings if not present
        default_settings = {
            "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
            "python.terminal.activateEnvironment": True,
            "files.associations": {
                "*.json": "json",
                "*.yaml": "yaml", 
                "*.yml": "yaml"
            },
            "editor.formatOnSave": True,
            "files.autoSave": "afterDelay",
            "git.enableSmartCommit": True,
            "git.confirmSync": False,
            "workbench.startupEditor": "none"
        }
        
        for key, value in default_settings.items():
            if key not in settings:
                settings[key] = value
        
        # Save settings
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        
        print(f"✅ VS Code settings updated: {self.settings_file}")
        
        # Print summary
        self._print_summary(detected_git, terminal_profiles)
        
        return True
    
    def _print_summary(self, detected_git, profiles):
        """Print configuration summary."""
        print("\n📊 Configuration Summary:")
        print("-" * 30)
        
        if detected_git:
            print(f"🎯 Primary Git Bash: {detected_git}")
            print(f"🏠 Default terminal: Git Bash")
        else:
            print("⚠️  No Git Bash detected - using PowerShell as default")
        
        print(f"📝 Terminal profiles created: {len(profiles)}")
        for name in profiles.keys():
            print(f"   • {name}")
        
        print("\n🛠️  Troubleshooting Tips:")
        print("   • If terminal still fails, try 'Developer: Reload Window' in VS Code")
        print("   • Check VS Code Developer Tools console for specific errors")
        print("   • Ensure Git for Windows is properly installed")
        print("   • Try running VS Code as Administrator if permission issues persist")


def main():
    """Main function."""
    print("🚀 VS Code Git Bash Terminal Configuration Fixer")
    print("=" * 60)
    print("This script fixes the common VS Code terminal exit code 256 issue")
    print("by configuring proper Git Bash terminal profiles.\n")
    
    if platform.system() != "Windows":
        print("ℹ️  This fix is specifically for Windows. Current OS:", platform.system())
        print("The configuration will still be created but may not be needed.")
    
    fixer = VSCodeTerminalFixer()
    
    try:
        success = fixer.fix_terminal_configuration()
        if success:
            print("\n🎉 Configuration completed successfully!")
            print("💡 Restart VS Code or reload the window to apply changes.")
        else:
            print("\n❌ Configuration failed.")
            return 1
    except Exception as e:
        print(f"\n💥 Error during configuration: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())