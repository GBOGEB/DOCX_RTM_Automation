#!/usr/bin/env python3
"""
System Status Verification Script

Verify that all components of the RTM Automation system are working correctly.
"""

import json
import yaml
import platform
import shutil
from pathlib import Path

def main():
    """Verify system status and output files."""
    print("🔍 RTM Automation System Verification")
    print("=" * 45)

    # Show system information
    print(f"\n💻 System Information:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Python: {platform.python_version()}")
    print(f"   Architecture: {platform.machine()}")

    # Check disk space (Windows compatible)
    try:
        total, used, free = shutil.disk_usage(".")
        total_gb = total // (1024**3)
        free_gb = free // (1024**3)
        print(f"   Disk Space: {free_gb}GB free of {total_gb}GB total")
    except Exception as e:
        print(f"   Disk Space: Unable to check ({e})")

    # Check output files
    output_files = [
        "output/sample_document_enhanced.md",
        "output/sample_document_enhanced.json",
        "output/sample_document_enhanced.yaml",
        "output/integration_test_enhanced.json",
        "output/requirements.json"
    ]

    print(f"\n📁 Output Files Status:")
    valid_files = 0
    for file_path in output_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"  ✅ {file_path} ({size:,} bytes)")
            valid_files += 1

            # Validate JSON files
            if file_path.endswith('.json'):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    metadata = data.get('metadata', {})
                    requirements = metadata.get('requirements_found', [])
                    print(f"     - Requirements found: {len(requirements)}")
                    if requirements:
                        print(f"     - {', '.join(requirements[:3])}")
                except Exception as e:
                    print(f"     ⚠️ Error reading JSON: {e}")
        else:
            print(f"  ❌ {file_path} (missing)")

    # Check available input files
    print(f"\n📄 Available Input Files:")
    input_dirs = ["input", "input/docx", "input/markdown"]
    total_files = 0

    for dir_name in input_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            files = list(dir_path.glob("*.*"))
            valid_files_in_dir = [f for f in files if f.suffix.lower() in
                          ['.docx', '.doc', '.md', '.markdown', '.json', '.yaml', '.yml']]
            total_files += len(valid_files_in_dir)

            if valid_files_in_dir:
                print(f"  📂 {dir_name}/ ({len(valid_files_in_dir)} files)")
                for f in valid_files_in_dir[:3]:  # Show first 3
                    print(f"     - {f.name}")
                if len(valid_files_in_dir) > 3:
                    print(f"     - ... and {len(valid_files_in_dir) - 3} more")

    # Check dependencies
    print(f"\n🔧 Dependencies Status:")
    dependencies = []

    try:
        import markdown
        dependencies.append(f"✅ markdown v{getattr(markdown, '__version__', 'unknown')}")
    except ImportError:
        dependencies.append("❌ markdown (missing)")

    try:
        from docx import Document
        dependencies.append("✅ python-docx")
    except ImportError:
        dependencies.append("❌ python-docx (missing)")

    try:
        import yaml
        dependencies.append("✅ PyYAML")
    except ImportError:
        dependencies.append("❌ PyYAML (missing)")

    for dep in dependencies:
        print(f"  {dep}")

    print(f"\n📊 System Summary:")
    print(f"  - Total processable input files: {total_files}")
    print(f"  - Output files generated: {valid_files}/{len(output_files)}")
    print(f"  - Dependencies available: {len([d for d in dependencies if d.startswith('✅')])}/{len(dependencies)}")

    # Calculate overall status
    missing_deps = len([d for d in dependencies if d.startswith('❌')])
    missing_outputs = len(output_files) - valid_files

    if missing_deps == 0 and missing_outputs <= 1:
        status = "✅ EXCELLENT"
        color = "🟢"
    elif missing_deps <= 1 and missing_outputs <= 2:
        status = "✅ GOOD"
        color = "🟡"
    else:
        status = "⚠️ NEEDS ATTENTION"
        color = "🔴"

    print(f"  - Integration status: {color} {status}")

    print(f"\n🚀 Suggested Next Steps:")
    print("=" * 30)

    # Check for specific files and suggest actions
    output_dir = Path("output")

    if (output_dir / "requirements.json").exists():
        print("✅ Requirements document processed successfully!")
        print("   Next: Generate visualization:")
        print("   python src/visualizers/req_visualizer.py output/requirements.json -o output/requirements_chart.png")

    if (output_dir / "sample_document_enhanced.json").exists():
        print("✅ Sample document available!")
        print("   Next: Create digital twin:")
        print("   python digital_twin_parser.py input/sample/sample_document.md -o output/digital_twin")

    # General suggestions
    print("\n📋 General Options:")
    print("   1. Process more DOCX files:")
    print("      python enhance_document_parsing.py input/MASTER_1805_1144.docx -f json")
    print("   2. Run interactive mode:")
    print("      python enhance_document_parsing.py --interactive")
    print("   3. Check code quality:")
    print("      python run_code_quality_checks.py")
    print("   4. Run full test suite:")
    print("      python test_all_features.bat")

    # Show missing dependencies if any
    if missing_deps > 0:
        print(f"\n⚠️ Missing Dependencies:")
        for dep in dependencies:
            if dep.startswith('❌'):
                dep_name = dep.split(' ')[1]
                if dep_name == "python-docx":
                    print(f"   Install: pip install python-docx")
                elif dep_name == "markdown":
                    print(f"   Install: pip install markdown")
                elif dep_name == "PyYAML":
                    print(f"   Install: pip install PyYAML")

    print(f"\n{'='*45}")
    print(f"System Status: {status}")
    print(f"{'='*45}")

if __name__ == "__main__":
    main()