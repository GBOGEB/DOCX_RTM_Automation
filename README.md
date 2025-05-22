# DOCX → Markdown → YAML/JSON/RTM Pipeline

## 🚀 Getting Started

### Step 1: Setup

- Place your `.docx` file into `/input/`.
- Ensure `paths.yaml` is correctly updated with your paths.

### Step 2: Install Dependencies
```bash
pip install -r config/requirements.txt
```

### Step 3: Run Automation
```bash
bash config/commands.sh
```

### Outputs (`/output/`):
- `MASTER_1805_1144.md`: Markdown conversion
- `MASTER_1805_1144.yaml/json`: Parsed Markdown
- `MASTER_outline.yaml`: TOC outline
- `RTM_QQQ.yaml`: Requirements Traceability Matrix

✅ Traceability ensured with structured automation.
