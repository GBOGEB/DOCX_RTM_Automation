#!/usr/bin/env python3
"""
RTM Pipeline Executor - Complete pipeline to run all RTM system results
"""

import json
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RTMPipelineExecutor:
    """Complete RTM pipeline execution orchestrator."""

    def __init__(self):
        """Initialize the pipeline executor."""
        self.pipeline_steps = [
            {
                "name": "System Status Check",
                "command": "python main_organized.py status",
                "description": "Verify system health and organization",
                "required": True,
            },
            {
                "name": "JSON Ecosystem Analysis",
                "command": "python -c \"import sys; sys.path.insert(0, 'src'); from analyzers.json_file_analyzer_safe import main; main()\"",
                "description": "Analyze 189 JSON files ecosystem",
                "required": True,
            },
            {
                "name": "Import System Verification",
                "command": "python test_organized_imports.py",
                "description": "Test 100% import success rate",
                "required": True,
            },
            {
                "name": "Enhanced Document Parsing",
                "command": "python .ariana/enhance_document_parsing.py",
                "description": "Run enhanced document parsing demo",
                "required": False,
            },
            {
                "name": "Parsing Issues Diagnostic",
                "command": "python fix_parsing_issues.py",
                "description": "Check and fix parsing dependencies",
                "required": False,
            },
            {
                "name": "System Perfection Verification",
                "command": "python verify_rtm_still_perfect.py",
                "description": "Comprehensive system verification",
                "required": True,
            },
            {
                "name": "Growth Celebration",
                "command": "python rtm_growth_celebration.py",
                "description": "Document 187→189 file evolution",
                "required": False,
            },
            {
                "name": "Ultimate Success Report",
                "command": "python ultimate_success_report.py",
                "description": "Generate comprehensive achievement report",
                "required": False,
            },
            {
                "name": "Execution Success Celebration",
                "command": "python execution_success_celebration.py",
                "description": "Document perfect execution results",
                "required": False,
            },
            {
                "name": "Final Victory Celebration",
                "command": "python final_victory_celebration.py",
                "description": "Ultimate dual-excellence celebration",
                "required": False,
            },
        ]

        self.results = []

    def execute_step(self, step: dict) -> dict:
        """Execute a single pipeline step."""
        step_name = step["name"]
        command = step["command"]

        print(f"\n🚀 Executing: {step_name}")
        print(f"📝 Description: {step['description']}")
        print(f"💻 Command: {command}")
        print("=" * 60)

        start_time = time.time()

        try:
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            end_time = time.time()
            execution_time = end_time - start_time

            step_result = {
                "step_name": step_name,
                "command": command,
                "description": step["description"],
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "return_code": result.returncode,
                "status": "success" if result.returncode == 0 else "failed",
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            if result.returncode == 0:
                print(f"✅ SUCCESS - Completed in {execution_time:.2f}s")
                if result.stdout:
                    print("📄 Output preview:")
                    # Show first few lines of output
                    output_lines = result.stdout.split("\n")[:10]
                    for line in output_lines:
                        if line.strip():
                            print(f"   {line}")
                    if len(result.stdout.split("\n")) > 10:
                        print("   ... (output truncated, see full results)")
            else:
                print(f"❌ FAILED - Return code: {result.returncode}")
                if result.stderr:
                    print("⚠️ Error output:")
                    error_lines = result.stderr.split("\n")[:5]
                    for line in error_lines:
                        if line.strip():
                            print(f"   {line}")

            return step_result

        except subprocess.TimeoutExpired:
            print("⏰ TIMEOUT - Step exceeded 5 minute limit")
            return {
                "step_name": step_name,
                "command": command,
                "status": "timeout",
                "error": "Command timed out after 5 minutes",
            }
        except Exception as e:
            print(f"❌ ERROR - {str(e)}")
            return {
                "step_name": step_name,
                "command": command,
                "status": "error",
                "error": str(e),
            }

    def run_pipeline(self, skip_optional: bool = False) -> dict:
        """Run the complete RTM pipeline."""

        print("🎯 RTM PIPELINE EXECUTOR")
        print("=" * 50)
        print(f"📊 Total steps: {len(self.pipeline_steps)}")
        print(f"⚙️ Skip optional: {skip_optional}")
        print(f"🕒 Started at: {datetime.now().isoformat()}")
        print("=" * 50)

        pipeline_start = time.time()

        for i, step in enumerate(self.pipeline_steps, 1):
            # Skip optional steps if requested
            if skip_optional and not step.get("required", False):
                print(
                    f"\n⏭️ Skipping optional step {i}/{len(self.pipeline_steps)}: {step['name']}"
                )
                continue

            print(f"\n📍 Step {i}/{len(self.pipeline_steps)}")

            # Execute the step
            result = self.execute_step(step)
            self.results.append(result)

            # Short pause between steps
            time.sleep(1)

        pipeline_end = time.time()
        total_time = pipeline_end - pipeline_start

        # Generate pipeline summary
        summary = self._generate_pipeline_summary(total_time)

        # Save results
        self._save_pipeline_results(summary)

        return summary

    def _generate_pipeline_summary(self, total_time: float) -> dict:
        """Generate pipeline execution summary."""

        successful_steps = [r for r in self.results if r.get("status") == "success"]
        failed_steps = [
            r for r in self.results if r.get("status") in ["failed", "error", "timeout"]
        ]

        summary = {
            "pipeline_execution": {
                "timestamp": datetime.now().isoformat(),
                "total_execution_time": total_time,
                "total_steps": len(self.pipeline_steps),
                "executed_steps": len(self.results),
                "successful_steps": len(successful_steps),
                "failed_steps": len(failed_steps),
                "success_rate": (
                    (len(successful_steps) / len(self.results)) * 100
                    if self.results
                    else 0
                ),
            },
            "step_results": self.results,
            "summary_metrics": {
                "json_analysis_completed": any(
                    "JSON" in r.get("step_name", "") for r in successful_steps
                ),
                "system_verification_completed": any(
                    "Verification" in r.get("step_name", "") for r in successful_steps
                ),
                "import_testing_completed": any(
                    "Import" in r.get("step_name", "") for r in successful_steps
                ),
                "parsing_tested": any(
                    "Parsing" in r.get("step_name", "") for r in successful_steps
                ),
                "celebrations_generated": any(
                    "Celebration" in r.get("step_name", "") for r in successful_steps
                ),
            },
        }

        return summary

    def _save_pipeline_results(self, summary: dict):
        """Save pipeline results to file."""

        # Save detailed results
        results_file = Path("rtm_pipeline_results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Pipeline results saved to: {results_file}")

        # Generate summary report
        self._print_pipeline_summary(summary)

    def _print_pipeline_summary(self, summary: dict):
        """Print pipeline execution summary."""

        print("\n🎊 RTM PIPELINE EXECUTION COMPLETE!")
        print("=" * 50)

        metrics = summary["pipeline_execution"]

        print("📊 EXECUTION METRICS:")
        print(f"   ⏱️ Total time: {metrics['total_execution_time']:.2f} seconds")
        print(
            f"   📋 Steps executed: {metrics['executed_steps']}/{metrics['total_steps']}"
        )
        print(f"   ✅ Successful: {metrics['successful_steps']}")
        print(f"   ❌ Failed: {metrics['failed_steps']}")
        print(f"   🎯 Success rate: {metrics['success_rate']:.1f}%")

        print("\n🌟 PIPELINE ACHIEVEMENTS:")
        achievements = summary["summary_metrics"]

        for achievement, completed in achievements.items():
            status = "✅" if completed else "❌"
            readable_name = achievement.replace("_", " ").title()
            print(f"   {status} {readable_name}")

        # Show failed steps if any
        failed_steps = [
            r for r in self.results if r.get("status") in ["failed", "error", "timeout"]
        ]
        if failed_steps:
            print("\n⚠️ FAILED STEPS:")
            for step in failed_steps:
                print(
                    f"   ❌ {step['step_name']}: {step.get('error', 'Unknown error')}"
                )

        print("\n🏆 RTM PIPELINE EXECUTION SUMMARY:")
        if metrics["success_rate"] >= 90:
            print("   🎉 EXCELLENT! Pipeline executed with outstanding success!")
        elif metrics["success_rate"] >= 70:
            print("   👍 GOOD! Pipeline executed successfully with minor issues")
        else:
            print("   ⚠️ PARTIAL! Pipeline completed but needs attention")


def main():
    """Main pipeline execution function."""

    print("🚀 RTM Complete Pipeline Executor")
    print("=" * 45)

    executor = RTMPipelineExecutor()

    # Check command line arguments
    skip_optional = "--required-only" in sys.argv or "-r" in sys.argv

    if skip_optional:
        print("⚡ Running REQUIRED steps only (faster execution)")
    else:
        print("🎯 Running ALL steps (complete demonstration)")

    print("\n🎬 Starting pipeline execution...")

    try:
        # Run the pipeline
        executor.run_pipeline(skip_optional=skip_optional)

        # Show next steps
        print("\n🎯 NEXT STEPS:")
        print("   📄 View detailed results: rtm_pipeline_results.json")
        print("   🎨 Run visual celebration: python ascii_celebration.py")
        print("   🌐 Launch dashboard: python launch_dashboard.py")
        print("   📊 Check system status: python main_organized.py status")

        return 0

    except KeyboardInterrupt:
        print("\n⏹️ Pipeline execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Pipeline execution error: {e}")
        logger.error(f"Pipeline error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
