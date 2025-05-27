# DOCX RTM Automation

A comprehensive automation pipeline for converting DOCX documents to Requirements Traceability Matrix (RTM) format.

## 🚀 Features

- **DOCX to Markdown Conversion**: Uses Pandoc with custom Lua filters
- **Requirements Extraction**: Automatically identifies and extracts requirements
- **Document Structure Analysis**: Generates hierarchical document outlines
- **ASCII Diagrams**: Creates text-based structure visualizations
- **Quality Assurance**: Built-in validation and error checking

## 📁 Project Structure

```
DOCX_RTM_Automation_v1.0/
├── code/                   # Main application code
├── src/                   # Source modules
│   ├── core/             # Core functionality
│   ├── modules/          # Feature modules
│   └── extractors/       # Data extraction utilities
├── config/               # Configuration files
├── input/                # Input DOCX files
├── output/               # Generated outputs
├── logs/                 # Application logs
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── tests/                # Test files
```

## 🛠️ Installation

1. **Prerequisites**:
   ```bash
   # Install Pandoc
   # Windows: Download from https://pandoc.org/installing.html
   # macOS: brew install pandoc
   # Linux: sudo apt-get install pandoc

   # Install Python dependencies
   pip install -r requirements.txt
   ```

2. **Setup**:
   ```bash
   # Clone the repository
   git clone <repository-url>
   cd DOCX_RTM_Automation_v1.0

   # Run the setup script
   python project_update.py
   ```

## 🏃‍♂️ Quick Start

1. **Place your DOCX file** in the `input/` directory
2. **Run the main pipeline**:
   ```bash
   python code/main.py
   ```
3. **Check results** in the `output/` directory

## 📊 Output Files

- `*.md` - Converted Markdown with TOC and section numbering
- `*_outline.yaml` - Document structure hierarchy
- `*_requirements.yaml` - Extracted requirements
- `*_structure.txt` - ASCII structure diagram

## 🔧 Configuration

Edit `config/paths.yaml` to customize:
- Input/output directories
- Pandoc conversion options
- Requirements extraction patterns
- Output formats

## 🐛 Troubleshooting

### Common Issues

1. **Pandoc not found**: Ensure Pandoc is installed and in PATH
2. **TOC depth errors**: TOC depth is automatically limited to 6 (Pandoc maximum)
3. **Lua filter errors**: Check if Lua filters exist in `config/` directory

### Debug Mode

Enable debug logging by setting the log level in your script:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in `docs/`
- Review the logs in `logs/` for error details

---

*Last updated: 2025-05-23*
