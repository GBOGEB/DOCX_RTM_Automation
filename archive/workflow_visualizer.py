#!/usr/bin/env python3
"""
Workflow Visualizer - Generate ASCII diagrams and workflow visualization
"""

from pathlib import Path
import json
from datetime import datetime

def generate_ascii_title():
    """Generate ASCII art title"""
    return """
 ██████╗ ████████╗███╗   ███╗     █████╗ ██╗   ██╗████████╗ ██████╗
 ██╔══██╗╚══██╔══╝████╗ ████║    ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗
 ██████╔╝   ██║   ██╔████╔██║    ███████║██║   ██║   ██║   ██║   ██║
 ██╔══██╗   ██║   ██║╚██╔╝██║    ██╔══██║██║   ██║   ██║   ██║   ██║
 ██║  ██║   ██║   ██║ ╚═╝ ██║    ██║  ██║╚██████╔╝   ██║   ╚██████╔╝
 ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝    ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝
    RTM AUTOMATION - Document Processing Pipeline
"""

def generate_workflow_diagram():
    """Generate workflow process diagram"""
    return """
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RTM PROCESSING WORKFLOW                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    INPUT    │───▶│  VALIDATE   │───▶│   PROCESS   │───▶│   OUTPUT    │
│             │    │             │    │             │    │             │
│ • DOCX File │    │ • Check ext │    │ • Extract   │    │ • JSON Data │
│ • RTM Data  │    │ • Verify    │    │ • Analyze   │    │ • Text File │
│ • Tables    │    │ • Size OK   │    │ • Convert   │    │ • Summary   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│input/       │    │Validation   │    │Pipeline     │    │output/      │
│*.docx       │    │Engine       │    │Processing   │    │*.json       │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
"""

def generate_project_tree():
    """Generate project structure tree"""
    return """
DOCX_RTM_Automation_v1.0/
├── 🐍 Python Scripts
│   ├── main.py                    # Main pipeline execution
│   ├── document_converter.py      # DOCX processing engine
│   ├── find_output_files.py       # Output file analyzer
│   ├── project_scanner.py         # Project structure analyzer
│   ├── setup_project.py           # Git/GitHub setup script
│   ├── quick_setup.py             # Quick configuration helper
│   ├── fix_main_pipeline.py       # Pipeline troubleshooter
│   └── workflow_visualizer.py     # This visualization script
│
├── 📚 Documentation
│   ├── README.md                  # Comprehensive project guide
│   ├── git_workflow_guide.md      # Git workflow documentation
│   └── .gitignore                 # Git ignore rules
│
├── 📁 Directories
│   ├── input/                     # Input DOCX files
│   │   └── MASTER_1805_1144.docx  # Sample RTM document
│   ├── output/                    # Generated output files
│   │   ├── *.txt                  # Extracted text content
│   │   ├── *.json                 # Structured data
│   │   └── *_summary.json         # Conversion summaries
│   ├── pipeline/                  # Processing pipeline modules
│   ├── utils/                     # Utility functions
│   ├── config/                    # Configuration files
│   ├── docs/                      # Additional documentation
│   └── tests/                     # Test files
│
└── 🔧 Configuration
    ├── .venv/                     # Virtual environment
    ├── requirements.txt           # Python dependencies
    └── .git/                      # Git repository data
"""

def generate_git_workflow():
    """Generate Git workflow diagram"""
    return """
┌─────────────────────────────────────────────────────────────────────────────┐
│                            GIT WORKFLOW                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    INIT     │───▶│     ADD     │───▶│   COMMIT    │───▶│    PUSH     │
│             │    │             │    │             │    │             │
│ git init    │    │ git add .   │    │ git commit  │    │ git push    │
│ setup repo  │    │ stage files │    │ save state  │    │ to GitHub   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Local Repo  │    │ Staged Area │    │ Local Hist  │    │ Remote Repo │
│ .git/       │    │ Ready files │    │ Commits     │    │ GitHub      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

Commands Reference:
• git status                    # Check current state
• git add *.py                  # Add Python files
• git commit -m "message"       # Create commit
• git push origin main          # Push to GitHub
• git pull origin main          # Get latest changes
"""

def generate_usage_examples():
    """Generate usage examples"""
    return """
┌─────────────────────────────────────────────────────────────────────────────┐
│                            USAGE EXAMPLES                                  │
└─────────────────────────────────────────────────────────────────────────────┘

🚀 Quick Start:
   python setup_project.py        # Initial Git setup
   python project_scanner.py      # Analyze project
   python main.py                 # Run RTM pipeline
   python find_output_files.py    # Check results

🔧 Development:
   python fix_main_pipeline.py    # Fix pipeline issues
   python quick_setup.py          # Quick configuration
   python document_converter.py   # Test converter

🐛 Troubleshooting:
   git status                     # Check Git state
   python -c "import docx"        # Test python-docx
   ls input/*.docx                # Check input files
   ls output/                     # Check output files

📊 Analysis:
   python project_scanner.py      # Full project scan
   python find_output_files.py    # Output analysis
   git log --oneline              # Git history
"""

def display_all_diagrams():
    """Display all workflow diagrams"""
    print(generate_ascii_title())
    print("\n" + "="*80)
    print("WORKFLOW VISUALIZATION")
    print("="*80)

    print(generate_workflow_diagram())
    print("\n" + "="*80)
    print("PROJECT STRUCTURE")
    print("="*80)
    print(generate_project_tree())

    print("\n" + "="*80)
    print("GIT WORKFLOW")
    print("="*80)
    print(generate_git_workflow())

    print("\n" + "="*80)
    print("USAGE EXAMPLES")
    print("="*80)
    print(generate_usage_examples())

def save_workflow_documentation():
    """Save all workflow diagrams to a file"""
    content = f"""# RTM Automation Workflow Documentation
Generated: {datetime.now().isoformat()}

{generate_ascii_title()}

## Workflow Diagram
{generate_workflow_diagram()}

## Project Structure
{generate_project_tree()}

## Git Workflow
{generate_git_workflow()}

## Usage Examples
{generate_usage_examples()}
"""

    try:
        with open("workflow_documentation.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Workflow documentation saved to: workflow_documentation.md")
        return True
    except Exception as e:
        print(f"❌ Failed to save workflow documentation: {e}")
        return False

def create_project_status():
    """Create a project status overview"""
    project_root = Path(".")

    # Count files by type
    python_files = list(project_root.glob("*.py"))
    doc_files = list(project_root.glob("*.md"))
    input_files = list(project_root.glob("input/*.docx"))
    output_files = list(project_root.glob("output/*"))

    status = f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROJECT STATUS                                   │
└─────────────────────────────────────────────────────────────────────────────┘

📊 File Counts:
   🐍 Python Scripts: {len(python_files)}
   📚 Documentation: {len(doc_files)}
   📄 Input Files: {len(input_files)}
   📁 Output Files: {len(output_files)}

🔧 Key Components:
   {'✅' if Path('main.py').exists() else '❌'} main.py - Main pipeline
   {'✅' if Path('document_converter.py').exists() else '❌'} document_converter.py - Core processor
   {'✅' if Path('setup_project.py').exists() else '❌'} setup_project.py - Git setup
   {'✅' if Path('README.md').exists() else '❌'} README.md - Documentation
   {'✅' if Path('.gitignore').exists() else '❌'} .gitignore - Git rules

📁 Directory Structure:
   {'✅' if Path('input').exists() else '❌'} input/ directory
   {'✅' if Path('output').exists() else '❌'} output/ directory
   {'✅' if Path('.git').exists() else '❌'} Git repository
   {'✅' if Path('.venv').exists() else '❌'} Virtual environment

🎯 Ready to Run:
   {'✅' if len(input_files) > 0 else '⚠️ '} Input files available
   {'✅' if Path('main.py').exists() else '❌'} Pipeline executable
   {'✅' if Path('.git').exists() else '⚠️ '} Git initialized
"""

    return status

def main():
    """Main function to display workflow visualization"""
    print("🎨 RTM Automation Workflow Visualizer")
    print("=" * 50)

    # Display all diagrams
    display_all_diagrams()

    # Show project status
    print("\n" + "="*80)
    print("PROJECT STATUS")
    print("="*80)
    print(create_project_status())

    # Offer to save documentation
    print("\n" + "="*80)
    response = input("Save workflow documentation to file? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        save_workflow_documentation()

    print("\n🎉 Workflow visualization complete!")
    print("\nNext steps:")
    print("1. Review the workflow diagrams above")
    print("2. Follow the usage examples")
    print("3. Run: python setup_project.py")
    print("4. Start processing: python main.py")

if __name__ == "__main__":
    main()
