"""
Format Handler - Convert unsupported file formats to supported ones
"""

import json
import os
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

class FormatHandler:
    """Handler for converting unsupported file formats"""

    def __init__(self):
        self.supported_extensions = ['.docx', '.txt', '.md', '.rtf', '.odt']
        self.convertible_extensions = ['.json', '.yaml', '.yml']

    def is_supported(self, file_path: str) -> bool:
        """Check if file format is supported"""
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_extensions

    def is_convertible(self, file_path: str) -> bool:
        """Check if file format can be converted"""
        ext = Path(file_path).suffix.lower()
        return ext in self.convertible_extensions

    def convert_json_to_markdown(self, json_file: str) -> Optional[str]:
        """Convert JSON file to Markdown"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            input_path = Path(json_file)
            output_path = input_path.parent / f"{input_path.stem}_converted.md"

            markdown_content = self._json_to_markdown(data, input_path.name)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            return str(output_path)

        except Exception as e:
            print(f"Error converting JSON {json_file}: {e}")
            return None

    def convert_yaml_to_markdown(self, yaml_file: str) -> Optional[str]:
        """Convert YAML file to Markdown"""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            input_path = Path(yaml_file)
            output_path = input_path.parent / f"{input_path.stem}_converted.md"

            markdown_content = self._yaml_to_markdown(data, input_path.name)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            return str(output_path)

        except Exception as e:
            print(f"Error converting YAML {yaml_file}: {e}")
            return None

    def _json_to_markdown(self, data: Any, filename: str) -> str:
        """Convert JSON data to Markdown format"""
        content = f"""# Converted from JSON: {filename}

**Conversion Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Original Format:** JSON
**Source File:** {filename}

---

## Document Content

"""

        if isinstance(data, dict):
            content += self._dict_to_markdown(data)
        elif isinstance(data, list):
            content += self._list_to_markdown(data)
        else:
            content += f"```json\n{json.dumps(data, indent=2)}\n```\n"

        return content

    def _yaml_to_markdown(self, data: Any, filename: str) -> str:
        """Convert YAML data to Markdown format"""
        content = f"""# Converted from YAML: {filename}

**Conversion Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Original Format:** YAML
**Source File:** {filename}

---

## Document Content

"""

        if isinstance(data, dict):
            content += self._dict_to_markdown(data)
        elif isinstance(data, list):
            content += self._list_to_markdown(data)
        else:
            content += f"```yaml\n{yaml.dump(data, default_flow_style=False)}\n```\n"

        return content

    def _dict_to_markdown(self, data: dict, level: int = 2) -> str:
        """Convert dictionary to Markdown"""
        content = ""

        for key, value in data.items():
            # Create header
            header_prefix = "#" * min(level, 6)
            content += f"\n{header_prefix} {str(key).replace('_', ' ').title()}\n\n"

            if isinstance(value, dict):
                content += self._dict_to_markdown(value, level + 1)
            elif isinstance(value, list):
                content += self._list_to_markdown(value)
            elif isinstance(value, str) and len(value) > 100:
                content += f"{value}\n\n"
            else:
                content += f"**Value:** {value}\n\n"

        return content

    def _list_to_markdown(self, data: list) -> str:
        """Convert list to Markdown"""
        content = ""

        for i, item in enumerate(data):
            if isinstance(item, dict):
                content += f"\n### Item {i + 1}\n\n"
                content += self._dict_to_markdown(item, 4)
            elif isinstance(item, list):
                content += f"\n### List Item {i + 1}\n\n"
                content += self._list_to_markdown(item)
            else:
                content += f"- {item}\n"

        content += "\n"
        return content

    def batch_convert_unsupported(self, directory: str = "input") -> List[str]:
        """Batch convert all unsupported files in directory"""
        converted_files = []

        if not os.path.exists(directory):
            return converted_files

        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)

            if os.path.isfile(file_path) and not self.is_supported(file_path):
                if self.is_convertible(file_path):
                    ext = Path(file_path).suffix.lower()

                    if ext == '.json':
                        converted = self.convert_json_to_markdown(file_path)
                    elif ext in ['.yaml', '.yml']:
                        converted = self.convert_yaml_to_markdown(file_path)
                    else:
                        continue

                    if converted:
                        converted_files.append(converted)
                        print(f"✅ Converted: {file} -> {Path(converted).name}")

        return converted_files

    def generate_format_report(self, directory: str = "input") -> Dict[str, Any]:
        """Generate format compatibility report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "directory": directory,
            "supported_files": [],
            "convertible_files": [],
            "unsupported_files": [],
            "statistics": {
                "total_files": 0,
                "supported_count": 0,
                "convertible_count": 0,
                "unsupported_count": 0
            }
        }

        if not os.path.exists(directory):
            return report

        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)

            if os.path.isfile(file_path):
                report["statistics"]["total_files"] += 1

                file_info = {
                    "filename": file,
                    "path": file_path,
                    "extension": Path(file).suffix.lower(),
                    "size_bytes": os.path.getsize(file_path)
                }

                if self.is_supported(file_path):
                    report["supported_files"].append(file_info)
                    report["statistics"]["supported_count"] += 1
                elif self.is_convertible(file_path):
                    report["convertible_files"].append(file_info)
                    report["statistics"]["convertible_count"] += 1
                else:
                    report["unsupported_files"].append(file_info)
                    report["statistics"]["unsupported_count"] += 1

        return report

def main():
    """Main function for testing format handler"""
    handler = FormatHandler()

    print("📄 Format Handler Test")
    print("=" * 30)

    # Generate format report
    report = handler.generate_format_report()

    print(f"📊 Format Analysis:")
    print(f"   Total files: {report['statistics']['total_files']}")
    print(f"   Supported: {report['statistics']['supported_count']}")
    print(f"   Convertible: {report['statistics']['convertible_count']}")
    print(f"   Unsupported: {report['statistics']['unsupported_count']}")

    # Convert unsupported files
    if report['statistics']['convertible_count'] > 0:
        print(f"\n🔄 Converting {report['statistics']['convertible_count']} files...")
        converted = handler.batch_convert_unsupported()
        print(f"✅ Converted {len(converted)} files successfully")

    # Save report
    os.makedirs("logs", exist_ok=True)
    report_file = f"logs/format_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved to: {report_file}")

if __name__ == "__main__":
    main()
