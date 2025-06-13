#!/usr/bin/env python3
"""
Main Organized - Clean, well-structured entry point for RTM automation
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main_organized.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RTMAutomationPipeline:
    """Main RTM automation pipeline class"""

    def __init__(self):
        """Initialize the RTM automation pipeline"""
        self.input_dir = Path("input")
        self.output_dir = Path("output")
        self.logs_dir = Path("logs")
        self.processed_files = []
        self.failed_files = []

        # Ensure directories exist
        self.setup_directories()

    def setup_directories(self):
        """Create necessary directories"""
        directories = [self.input_dir, self.output_dir, self.logs_dir]

        for directory in directories:
            try:
                directory.mkdir(exist_ok=True)
                logger.info(f"Directory ready: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")

    def discover_input_files(self) -> List[Path]:
        """Discover DOCX files for processing"""
        logger.info("🔍 Discovering input files...")

        if not self.input_dir.exists():
            logger.warning(f"Input directory not found: {self.input_dir}")
            return []

        # Find DOCX files
        docx_files = list(self.input_dir.glob("*.docx"))

        # Filter out temporary files (starting with ~$)
        valid_files = [f for f in docx_files if not f.name.startswith("~$")]

        logger.info(f"Found {len(valid_files)} DOCX files to process")
        for file_path in valid_files:
            logger.info(f"  📄 {file_path.name}")

        return valid_files

    def process_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single DOCX file"""
        logger.info(f"🔄 Processing: {file_path.name}")

        start_time = datetime.now()
        result = {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "start_time": start_time,
            "success": False,
            "error": None,
            "output_files": [],
            "stats": {}
        }

        try:
            # Import the document converter
            from src.rtm.document_converter import run_document_conversion

            # Process the file
            conversion_result = run_document_conversion(str(file_path))

            if conversion_result:
                result["success"] = True
                logger.info(f"  ✅ Successfully processed: {file_path.name}")
                self.processed_files.append(result)
            else:
                result["error"] = "Conversion returned False"
                logger.warning(f"  ⚠️  Processing completed with issues: {file_path.name}")
                self.failed_files.append(result)

        except ImportError as e:
            # Fallback to basic processing
            logger.warning(f"  ⚠️  Using fallback processing for {file_path.name}: {e}")
            fallback_result = self.fallback_processing(file_path)
            result.update(fallback_result)

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"  ❌ Error processing {file_path.name}: {e}")
            self.failed_files.append(result)

        # Calculate processing time
        result["end_time"] = datetime.now()
        result["processing_time"] = (result["end_time"] - start_time).total_seconds()

        return result

    def fallback_processing(self, file_path: Path) -> Dict[str, Any]:
        """Fallback processing when main converter isn't available"""
        logger.info(f"  🔄 Using fallback processing for: {file_path.name}")

        try:
            # Create a simple analysis file
            output_file = self.output_dir / f"{file_path.stem}_fallback_analysis.txt"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"RTM Fallback Analysis\n")
                f.write(f"=" * 30 + "\n")
                f.write(f"File: {file_path.name}\n")
                f.write(f"Processed: {datetime.now().isoformat()}\n")
                f.write(f"Size: {file_path.stat().st_size:,} bytes\n")
                f.write(f"Modified: {datetime.fromtimestamp(file_path.stat().st_mtime)}\n")
                f.write(f"\nNote: This is a fallback analysis.\n")
                f.write(f"For full processing, ensure python-docx is installed.\n")

            return {
                "success": True,
                "output_files": [str(output_file)],
                "stats": {"type": "fallback", "output_size": output_file.stat().st_size}
            }

        except Exception as e:
            logger.error(f"  ❌ Fallback processing failed: {e}")
            return {
                "success": False,
                "error": f"Fallback processing failed: {e}"
            }

    def process_all_files(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Process all discovered files"""
        logger.info(f"🚀 Starting batch processing of {len(file_paths)} files")

        processing_summary = {
            "total_files": len(file_paths),
            "successful": 0,
            "failed": 0,
            "start_time": datetime.now(),
            "files_processed": []
        }

        for i, file_path in enumerate(file_paths, 1):
            logger.info(f"\n📄 Processing file {i}/{len(file_paths)}: {file_path.name}")

            result = self.process_single_file(file_path)
            processing_summary["files_processed"].append(result)

            if result["success"]:
                processing_summary["successful"] += 1
            else:
                processing_summary["failed"] += 1

        processing_summary["end_time"] = datetime.now()
        processing_summary["total_time"] = (
            processing_summary["end_time"] - processing_summary["start_time"]
        ).total_seconds()

        return processing_summary

    def generate_summary_report(self, processing_summary: Dict[str, Any]):
        """Generate a comprehensive summary report"""
        logger.info("\n📊 Generating summary report...")

        # Create summary report
        report_file = self.logs_dir / f"processing_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("RTM AUTOMATION PROCESSING SUMMARY\n")
                f.write("=" * 50 + "\n\n")

                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Total files: {processing_summary['total_files']}\n")
                f.write(f"Successful: {processing_summary['successful']}\n")
                f.write(f"Failed: {processing_summary['failed']}\n")
                f.write(f"Success rate: {(processing_summary['successful']/processing_summary['total_files']*100):.1f}%\n")
                f.write(f"Total processing time: {processing_summary['total_time']:.2f} seconds\n\n")

                f.write("DETAILED RESULTS:\n")
                f.write("-" * 20 + "\n")

                for result in processing_summary["files_processed"]:
                    status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
                    f.write(f"{status} - {result['file_name']}\n")
                    f.write(f"   Time: {result.get('processing_time', 0):.2f}s\n")
                    if result.get("error"):
                        f.write(f"   Error: {result['error']}\n")
                    f.write("\n")

            logger.info(f"📋 Summary report saved: {report_file}")

        except Exception as e:
            logger.error(f"Failed to generate summary report: {e}")

    def display_final_results(self, processing_summary: Dict[str, Any]):
        """Display final results to console"""
        total = processing_summary["total_files"]
        successful = processing_summary["successful"]
        failed = processing_summary["failed"]

        print(f"\n📊 PROCESSING SUMMARY")
        print("=" * 30)
        print(f"Files found: {total}")
        print(f"Successfully processed: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {(successful/total*100):.1f}%")
        print(f"Total time: {processing_summary['total_time']:.2f} seconds")

        if successful > 0:
            print(f"\n✅ RTM automation completed!")
            print(f"📁 Check '{self.output_dir}' directory for results")
            print(f"📋 Check '{self.logs_dir}' directory for detailed logs")
        else:
            print(f"\n❌ No files were successfully processed")
            print(f"📋 Check logs for details: {self.logs_dir}")

    def run(self) -> int:
        """Main execution method"""
        logger.info("🚀 RTM AUTOMATION PIPELINE STARTING")
        logger.info("=" * 50)

        try:
            # Discover files
            input_files = self.discover_input_files()

            if not input_files:
                logger.warning("⚠️  No DOCX files found for processing")
                print("\n⚠️  No DOCX files found for processing")
                print("\nSuggestions:")
                print(f"   • Place DOCX files in '{self.input_dir}/' directory")
                print(f"   • Ensure files have .docx extension")
                print(f"   • Run: python create_test_document.py")
                return 1

            # Process all files
            processing_summary = self.process_all_files(input_files)

            # Generate reports
            self.generate_summary_report(processing_summary)

            # Display results
            self.display_final_results(processing_summary)

            # Return exit code based on success
            if processing_summary["successful"] > 0:
                logger.info("🎉 RTM automation pipeline completed successfully")
                return 0
            else:
                logger.warning("⚠️  RTM automation pipeline completed with issues")
                return 1

        except Exception as e:
            logger.error(f"❌ Critical error in RTM automation pipeline: {e}")
            print(f"\n❌ Critical error: {e}")
            return 2


def main():
    """Main entry point"""
    print("🚀 RTM AUTOMATION - ORGANIZED PIPELINE")
    print("=" * 45)
    print("Professional document processing with comprehensive logging\n")

    # Create and run pipeline
    pipeline = RTMAutomationPipeline()
    exit_code = pipeline.run()

    # Show next steps
    if exit_code == 0:
        print(f"\n🎯 Next Steps:")
        print(f"   python find_output_files.py           # Analyze results")
        print(f"   python scripts/automation/version_manager.py  # Update version")
        print(f"   python comprehensive_test.py          # Run full tests")
    elif exit_code == 1:
        print(f"\n🔧 Troubleshooting:")
        print(f"   python fix_environment.py             # Fix environment")
        print(f"   python create_test_document.py        # Create test files")
        print(f"   python comprehensive_test.py          # Check system health")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
