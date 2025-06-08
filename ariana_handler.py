"""
Ariana Extension Handler - Support for custom Ariana file formats
"""

import json
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

class ArianaExtensionHandler:
    """Handler for Ariana-specific file extensions and processing"""

    def __init__(self):
        self.logger = logging.getLogger("ArianaHandler")
        self.supported_extensions = ['.aria', '.ari', '.arx']
        self.standard_extensions = ['.docx', '.rtf', '.txt', '.md']

    def is_ariana_file(self, file_path: str) -> bool:
        """Check if file is an Ariana extension"""
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_extensions

    def is_supported_file(self, file_path: str) -> bool:
        """Check if file is supported (Ariana or standard)"""
        ext = Path(file_path).suffix.lower()
        return ext in (self.supported_extensions + self.standard_extensions)

    def analyze_ariana_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze Ariana file content"""
        try:
            file_info = {
                "file_path": file_path,
                "extension": Path(file_path).suffix.lower(),
                "size_bytes": os.path.getsize(file_path),
                "timestamp": datetime.now().isoformat(),
                "content_type": "unknown",
                "ariana_metadata": {}
            }

            # Try to read as text first
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_info["content_preview"] = content[:500]
                    file_info["content_type"] = "text"

                    # Look for Ariana-specific patterns
                    ariana_patterns = self._detect_ariana_patterns(content)
                    file_info["ariana_metadata"] = ariana_patterns

            except UnicodeDecodeError:
                # Try binary analysis
                with open(file_path, 'rb') as f:
                    binary_content = f.read(100)
                    file_info["content_type"] = "binary"
                    file_info["binary_header"] = binary_content.hex()

            return file_info

        except Exception as e:
            self.logger.error(f"Error analyzing Ariana file {file_path}: {e}")
            return {"error": str(e), "file_path": file_path}

    def _detect_ariana_patterns(self, content: str) -> Dict[str, Any]:
        """Detect Ariana-specific patterns in content"""
        patterns = {
            "requirements_found": False,
            "test_cases_found": False,
            "rtm_elements_found": False,
            "ariana_headers": [],
            "metadata_blocks": []
        }

        lines = content.split('\n')

        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Look for requirement patterns
            if any(req_pattern in line_lower for req_pattern in
                   ['req-', 'requirement', 'shall', 'must']):
                patterns["requirements_found"] = True

            # Look for test case patterns
            if any(test_pattern in line_lower for test_pattern in
                   ['tc-', 'test case', 'verify', 'validate']):
                patterns["test_cases_found"] = True

            # Look for RTM patterns
            if any(rtm_pattern in line_lower for rtm_pattern in
                   ['traceability', 'rtm', 'linked to', 'traces to']):
                patterns["rtm_elements_found"] = True

            # Look for Ariana headers
            if line.startswith('#') and 'ariana' in line_lower:
                patterns["ariana_headers"].append({
                    "line": i + 1,
                    "content": line.strip()
                })

        return patterns

    def convert_ariana_to_standard(self, file_path: str, output_format: str = 'md') -> Optional[str]:
        """Convert Ariana file to standard format"""
        try:
            ariana_info = self.analyze_ariana_content(file_path)

            if ariana_info.get("error"):
                return None

            input_path = Path(file_path)
            output_path = input_path.parent / f"{input_path.stem}_converted.{output_format}"

            # Basic conversion strategy
            if ariana_info.get("content_type") == "text":
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Apply Ariana-specific transformations
                converted_content = self._apply_ariana_transformations(content, ariana_info)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(converted_content)

                self.logger.info(f"Converted Ariana file: {file_path} -> {output_path}")
                return str(output_path)

        except Exception as e:
            self.logger.error(f"Error converting Ariana file {file_path}: {e}")
            return None

    def _apply_ariana_transformations(self, content: str, ariana_info: Dict) -> str:
        """Apply Ariana-specific content transformations"""
        # Add Ariana metadata header
        header = f"""# Ariana Document Conversion
**Original File:** {ariana_info.get('file_path', 'unknown')}
**Conversion Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Content Type:** {ariana_info.get('content_type', 'unknown')}

---

"""

        # Process content based on detected patterns
        if ariana_info.get('ariana_metadata', {}).get('requirements_found'):
            header += "**Requirements Detected:** ✅\n"

        if ariana_info.get('ariana_metadata', {}).get('test_cases_found'):
            header += "**Test Cases Detected:** ✅\n"

        if ariana_info.get('ariana_metadata', {}).get('rtm_elements_found'):
            header += "**RTM Elements Detected:** ✅\n"

        header += "\n---\n\n"

        return header + content

    def generate_ariana_compatibility_report(self, directory: str = '.') -> Dict[str, Any]:
        """Generate comprehensive Ariana compatibility report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "directory_analyzed": directory,
            "ariana_files": [],
            "standard_files": [],
            "unsupported_files": [],
            "conversion_candidates": [],
            "statistics": {
                "total_files": 0,
                "ariana_files_count": 0,
                "standard_files_count": 0,
                "convertible_files": 0
            }
        }

        # Scan directory for files
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                report["statistics"]["total_files"] += 1

                ext = Path(file).suffix.lower()

                if ext in self.supported_extensions:
                    # Ariana file
                    ariana_info = self.analyze_ariana_content(file_path)
                    report["ariana_files"].append(ariana_info)
                    report["statistics"]["ariana_files_count"] += 1

                    # Check if convertible
                    if ariana_info.get("content_type") == "text":
                        report["conversion_candidates"].append(file_path)
                        report["statistics"]["convertible_files"] += 1

                elif ext in self.standard_extensions:
                    # Standard supported file
                    file_info = {
                        "file_path": file_path,
                        "extension": ext,
                        "size_bytes": os.path.getsize(file_path),
                        "supported": True
                    }
                    report["standard_files"].append(file_info)
                    report["statistics"]["standard_files_count"] += 1

                elif file != '' and not file.startswith('.'):
                    # Unsupported file
                    file_info = {
                        "file_path": file_path,
                        "extension": ext,
                        "size_bytes": os.path.getsize(file_path),
                        "supported": False
                    }
                    report["unsupported_files"].append(file_info)

        return report

    def batch_convert_ariana_files(self, directory: str = '.', output_format: str = 'md') -> List[str]:
        """Batch convert all Ariana files in directory"""
        converted_files = []

        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)

                if self.is_ariana_file(file_path):
                    converted_file = self.convert_ariana_to_standard(file_path, output_format)
                    if converted_file:
                        converted_files.append(converted_file)

        return converted_files

def main():
    """Main function for testing Ariana handler"""
    handler = ArianaExtensionHandler()

    print("🌟 Ariana Extension Handler Test")
    print("=" * 40)

    # Generate compatibility report
    report = handler.generate_ariana_compatibility_report()

    print(f"📊 Analysis Results:")
    print(f"   Total files: {report['statistics']['total_files']}")
    print(f"   Ariana files: {report['statistics']['ariana_files_count']}")
    print(f"   Standard files: {report['statistics']['standard_files_count']}")
    print(f"   Convertible files: {report['statistics']['convertible_files']}")

    # Save report
    os.makedirs("logs", exist_ok=True)
    report_file = f"logs/ariana_compatibility_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved to: {report_file}")

if __name__ == "__main__":
    main()
