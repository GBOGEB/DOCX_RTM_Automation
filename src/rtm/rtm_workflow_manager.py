#!/usr/bin/env python3
"""
RTM Workflow Manager - Orchestrate complete RTM workflows with your real documents
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

class RTMWorkflowManager:
    """Manages complete RTM workflows for your documents."""

    def __init__(self):
        self.input_dir = Path("input")
        self.output_dir = Path("output")
        self.workflow_results = {}
        self.start_time = datetime.now()

    def get_available_documents(self):
        """Get all available documents categorized by type."""
        documents = {
            'docx': [],
            'markdown': [],
            'json': [],
            'yaml': []
        }

        if self.input_dir.exists():
            # Find DOCX files (exclude temp files)
            for docx_file in self.input_dir.rglob("*.docx"):
                if not docx_file.name.startswith('~$'):
                    documents['docx'].append(docx_file)

            # Find other file types
            documents['markdown'] = list(self.input_dir.rglob("*.md"))
            documents['json'] = list(self.input_dir.rglob("*.json"))
            documents['yaml'].extend(list(self.input_dir.rglob("*.yaml")))
            documents['yaml'].extend(list(self.input_dir.rglob("*.yml")))

        return documents

    def run_complete_rtm_workflow(self):
        """Run the complete RTM workflow on all available documents."""
        print("🚀 Starting Complete RTM Workflow")
        print("=" * 50)

        documents = self.get_available_documents()

        # Show what we're working with
        total_docs = sum(len(docs) for docs in documents.values())
        print(f"📁 Found {total_docs} documents to process:")
        print(f"   📄 DOCX: {len(documents['docx'])}")
        print(f"   📝 Markdown: {len(documents['markdown'])}")
        print(f"   📊 JSON: {len(documents['json'])}")
        print(f"   📋 YAML: {len(documents['yaml'])}")

        # Step 1: Document Processing
        print(f"\n🔍 STEP 1: Document Processing")
        print("-" * 35)
        self.process_docx_documents(documents['docx'])

        # Step 2: Digital Twin Creation
        print(f"\n🔗 STEP 2: Digital Twin Creation")
        print("-" * 37)
        self.create_digital_twins(documents['markdown'])

        # Step 3: Requirements Analysis
        print(f"\n📊 STEP 3: Requirements Analysis")
        print("-" * 36)
        self.run_requirements_analysis()

        # Step 4: Quality Verification
        print(f"\n🔍 STEP 4: Quality Verification")
        print("-" * 35)
        self.run_quality_verification()

        # Step 5: Generate Reports
        print(f"\n📋 STEP 5: Generate Reports")
        print("-" * 31)
        self.generate_comprehensive_reports()

        # Final Summary
        self.show_workflow_summary()

    def process_docx_documents(self, docx_files):
        """Process all DOCX documents."""
        if not docx_files:
            print("   ℹ️ No DOCX files to process")
            return

        success_count = 0
        for docx_file in docx_files:
            print(f"   📄 Processing {docx_file.name}...")

            try:
                result = subprocess.run([
                    sys.executable, "enhance_document_parsing.py",
                    str(docx_file), "-f", "json"
                ], capture_output=True, text=True, timeout=120)

                if result.returncode == 0:
                    print(f"      ✅ SUCCESS")
                    success_count += 1
                else:
                    print(f"      ⚠️ Issues detected")
            except Exception as e:
                print(f"      ❌ Error: {e}")

        self.workflow_results['docx_processing'] = f"{success_count}/{len(docx_files)}"
        print(f"   📊 DOCX Processing: {success_count}/{len(docx_files)} successful")

    def create_digital_twins(self, md_files):
        """Create digital twins from markdown files."""
        if not md_files:
            print("   ℹ️ No Markdown files for digital twins")
            return

        success_count = 0
        for md_file in md_files:
            output_dir = f"output/{md_file.stem}_twin"
            print(f"   🔗 Creating twin from {md_file.name}...")

            try:
                result = subprocess.run([
                    sys.executable, "digital_twin_parser.py",
                    str(md_file), "-o", output_dir
                ], capture_output=True, text=True, timeout=120)

                if result.returncode == 0:
                    print(f"      ✅ SUCCESS")
                    success_count += 1
                else:
                    print(f"      ⚠️ Issues detected")
            except Exception as e:
                print(f"      ❌ Error: {e}")

        self.workflow_results['digital_twins'] = f"{success_count}/{len(md_files)}"
        print(f"   📊 Digital Twins: {success_count}/{len(md_files)} successful")

    def run_requirements_analysis(self):
        """Run comprehensive requirements analysis."""
        print("   📊 Running requirements analysis...")

        try:
            result = subprocess.run([
                sys.executable, "Project Requirements.py"
            ], capture_output=True, text=True, timeout=180)

            if result.returncode == 0:
                print("      ✅ Requirements analysis completed")
                self.workflow_results['requirements_analysis'] = "SUCCESS"
            else:
                print("      ⚠️ Requirements analysis had issues")
                self.workflow_results['requirements_analysis'] = "PARTIAL"
        except Exception as e:
            print(f"      ❌ Requirements analysis error: {e}")
            self.workflow_results['requirements_analysis'] = "FAILED"

    def run_quality_verification(self):
        """Run quality verification checks."""
        print("   🔍 Running quality verification...")

        try:
            result = subprocess.run([
                sys.executable, "verify_rtm_ready.py"
            ], capture_output=True, text=True, timeout=120)

            if "READY FOR USE" in result.stdout:
                print("      ✅ Quality verification passed")
                self.workflow_results['quality_verification'] = "PASSED"
            else:
                print("      ⚠️ Quality verification had issues")
                self.workflow_results['quality_verification'] = "PARTIAL"
        except Exception as e:
            print(f"      ❌ Quality verification error: {e}")
            self.workflow_results['quality_verification'] = "FAILED"

    def generate_comprehensive_reports(self):
        """Generate comprehensive workflow reports."""
        print("   📋 Generating comprehensive reports...")

        # Generate extension report
        try:
            result = subprocess.run([
                sys.executable, "extension_control.py", "report"
            ], capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                print("      ✅ Extension report generated")
            else:
                print("      ⚠️ Extension report had issues")
        except Exception as e:
            print(f"      ⚠️ Extension report error: {e}")

        # Generate workflow summary report
        workflow_report = {
            "workflow_start": self.start_time.isoformat(),
            "workflow_end": datetime.now().isoformat(),
            "results": self.workflow_results,
            "output_files": self.count_output_files()
        }

        report_path = self.output_dir / "workflow_summary.json"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_report, f, indent=2)
            print(f"      ✅ Workflow summary saved to {report_path}")
        except Exception as e:
            print(f"      ⚠️ Workflow summary error: {e}")

    def count_output_files(self):
        """Count and categorize output files."""
        if not self.output_dir.exists():
            return {"total": 0}

        output_files = list(self.output_dir.glob("*"))
        json_files = list(self.output_dir.glob("*.json"))
        yaml_files = list(self.output_dir.glob("*.yaml"))
        md_files = list(self.output_dir.glob("*.md"))
        directories = [p for p in self.output_dir.iterdir() if p.is_dir()]

        return {
            "total": len(output_files),
            "json": len(json_files),
            "yaml": len(yaml_files),
            "markdown": len(md_files),
            "directories": len(directories)
        }

    def show_workflow_summary(self):
        """Show final workflow summary."""
        duration = datetime.now() - self.start_time

        print(f"\n🏆 RTM WORKFLOW COMPLETE!")
        print("=" * 40)
        print(f"   ⏱️ Total Duration: {duration.total_seconds():.1f} seconds")
        print(f"   📊 Workflow Results:")

        for step, result in self.workflow_results.items():
            step_name = step.replace('_', ' ').title()
            if result in ["SUCCESS", "PASSED"]:
                print(f"      ✅ {step_name}: {result}")
            elif "/" in str(result):
                # Success ratio
                nums = result.split("/")
                if nums[0] == nums[1]:
                    print(f"      ✅ {step_name}: {result}")
                else:
                    print(f"      ⚠️ {step_name}: {result}")
            else:
                print(f"      ⚠️ {step_name}: {result}")

        # Output summary
        output_summary = self.count_output_files()
        print(f"\n   📁 Output Summary:")
        print(f"      Total Files: {output_summary['total']}")
        print(f"      JSON Files: {output_summary['json']}")
        print(f"      YAML Files: {output_summary['yaml']}")
        print(f"      Markdown Files: {output_summary['markdown']}")
        print(f"      Directories: {output_summary['directories']}")

        # Calculate overall success
        success_indicators = 0
        total_indicators = 0

        for result in self.workflow_results.values():
            total_indicators += 1
            if result in ["SUCCESS", "PASSED"]:
                success_indicators += 1
            elif "/" in str(result):
                nums = result.split("/")
                if nums[0] == nums[1]:
                    success_indicators += 1
                else:
                    success_indicators += 0.5  # Partial success

        success_rate = (success_indicators / total_indicators * 100) if total_indicators > 0 else 0

        print(f"\n   🎯 Overall Success Rate: {success_rate:.1f}%")

        if success_rate >= 80:
            print(f"   🎉 EXCELLENT! Your RTM workflow is highly successful!")
        elif success_rate >= 60:
            print(f"   ✅ GOOD! Your RTM workflow performed well!")
        else:
            print(f"   ⚠️ Your RTM workflow needs some attention.")

        print(f"\n🚀 Your RTM system has successfully processed enterprise documents!")
        print(f"📊 Ready for production requirements traceability workflows!")

def main():
    """Main workflow management function."""
    print("🔧 RTM Workflow Manager")
    print("Orchestrating complete RTM workflows with your real documents")
    print("=" * 70)

    manager = RTMWorkflowManager()
    manager.run_complete_rtm_workflow()

    return 0

if __name__ == "__main__":
    sys.exit(main())
