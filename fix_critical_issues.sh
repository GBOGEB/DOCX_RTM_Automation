#!/bin/bash

# Script to fix critical issues found in RTM status check
PROJECT_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source common utilities
source "$PROJECT_ROOT_DIR/shell_scripts/common_utils.sh"

log_message "INFO" "Starting critical issues fix script..."

# 1. Fix the problematic paths.yaml by ensuring OpenAI API key is properly configured
log_message "INFO" "Checking OpenAI API key configuration..."
CONFIG_DIR="$PROJECT_ROOT_DIR/config"
PATHS_YAML="$CONFIG_DIR/paths.yaml"
OPENAI_KEY_FILE="$CONFIG_DIR/openai_key.txt"

if [ ! -d "$CONFIG_DIR" ]; then
    log_message "INFO" "Creating config directory..."
    mkdir -p "$CONFIG_DIR"
fi

if [ ! -f "$PATHS_YAML" ]; then
    log_message "WARNING" "paths.yaml not found, creating it..."
    cat > "$PATHS_YAML" << 'EOF'
# DOCX RTM Automation Configuration

# Path Configuration
paths:
  input_dir: "input"
  output_dir: "output"
  logs_dir: "logs"
  temp_dir: "temp"
  data_dir: "data"

# OpenAI API Configuration
openai:
  api_key_file: "config/openai_key.txt"
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2048

# Pipeline Configuration
pipeline:
  steps:
    - name: word_to_md
      script: src/core/word_to_md.py
      enabled: true

    - name: extract_outline
      script: src/extractors/extract_outline.py
      enabled: true

    - name: extract_rtm
      script: src/extractors/extract_rtm.py
      enabled: true

    - name: md_to_json_yaml
      script: src/core/md_to_json_yaml.py
      enabled: true

    - name: sync_outline_files
      script: src/utils/sync_outline_files.py
      enabled: true
EOF
    log_message "SUCCESS" "Created paths.yaml"
else
    log_message "INFO" "paths.yaml exists, checking OpenAI API key configuration..."

    # Check if openai.api_key_file is present
    if ! grep -q "api_key_file" "$PATHS_YAML"; then
        log_message "WARNING" "api_key_file not found in paths.yaml, adding it..."
        # Add openai section if not present
        if ! grep -q "openai:" "$PATHS_YAML"; then
            echo "" >> "$PATHS_YAML"
            echo "# OpenAI API Configuration" >> "$PATHS_YAML"
            echo "openai:" >> "$PATHS_YAML"
        fi

        # Add api_key_file
        echo "  api_key_file: \"config/openai_key.txt\"" >> "$PATHS_YAML"
        log_message "SUCCESS" "Added api_key_file to paths.yaml"
    else
        log_message "SUCCESS" "api_key_file found in paths.yaml"
    fi
fi

# Check OpenAI API key file
if [ ! -f "$OPENAI_KEY_FILE" ]; then
    log_message "WARNING" "OpenAI API key file not found, creating placeholder..."
    touch "$OPENAI_KEY_FILE"
    echo "sk-your-openai-api-key-goes-here" > "$OPENAI_KEY_FILE"
    log_message "SUCCESS" "Created OpenAI API key file placeholder"
    log_message "WARNING" "Please replace the placeholder with your actual OpenAI API key"
else
    log_message "SUCCESS" "OpenAI API key file exists"
fi

# 2. Create missing directory structure for src files
log_message "INFO" "Creating directory structure for src files..."
mkdir -p "$PROJECT_ROOT_DIR/src/core"
mkdir -p "$PROJECT_ROOT_DIR/src/extractors"
mkdir -p "$PROJECT_ROOT_DIR/src/utils"
mkdir -p "$PROJECT_ROOT_DIR/src/modules"
log_message "SUCCESS" "Directory structure for src files created"

# 3. Make all shell scripts executable
log_message "INFO" "Making all shell scripts executable..."
find "$PROJECT_ROOT_DIR" -name "*.sh" -exec chmod +x {} \;
log_message "SUCCESS" "All shell scripts are now executable"

# 4. Clean up temporary files
log_message "INFO" "Cleaning up temporary files..."
find "$PROJECT_ROOT_DIR" -name "~$*" -exec rm -f {} \;
log_message "SUCCESS" "Temporary files cleaned up"

# 5. Check config directory for Pandoc filter
if [ ! -f "$CONFIG_DIR/extend_headings.lua" ]; then
    log_message "INFO" "Creating Pandoc Lua filter..."
    cat > "$CONFIG_DIR/extend_headings.lua" << 'EOF'
-- extend_headings.lua
-- Pandoc Lua filter to enhance heading processing for RTM extraction

function Header(el)
  -- Extract section numbers from headings
  local section_number = ""
  local title = el.content
  local text = pandoc.utils.stringify(title)

  -- Check for section number pattern (e.g., "1.2.3 Section Title")
  local s, e, sec_num = string.find(text, "^(%d+%.%d+%.?%d*%.?)%s+")
  if s then
    section_number = sec_num
    -- Update the title without the section number
    local new_content = pandoc.utils.stringify(title):sub(e+1)
    el.content = pandoc.utils.from_simple_string(new_content)

    -- Add section-number as an attribute
    el.attributes["section-number"] = section_number
  end

  return el
end
EOF
    log_message "SUCCESS" "Created Pandoc Lua filter"
fi

log_message "SUCCESS" "Critical issues fix completed"
log_message "INFO" "Please run './shell_scripts/rtm_status.sh --verbose' to check status"
