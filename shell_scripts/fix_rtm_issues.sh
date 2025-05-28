#!/bin/bash

# Script to fix common RTM automation issues based on diagnostic results
PROJECT_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${PROJECT_ROOT_DIR}/shell_scripts/common_utils.sh"

log_message "INFO" "Starting RTM issues fix script..."

# Fix 1: Ensure common_utils.sh is in the correct location and executable
log_message "INFO" "Checking common_utils.sh..."
if [ -f "${PROJECT_ROOT_DIR}/shell_scripts/common_utils.sh" ]; then
    chmod +x "${PROJECT_ROOT_DIR}/shell_scripts/common_utils.sh"
    log_message "SUCCESS" "common_utils.sh found and made executable"
else
    log_message "ERROR" "common_utils.sh not found in ${PROJECT_ROOT_DIR}/shell_scripts/"
    log_message "INFO" "Creating common_utils.sh..."
    cat > "${PROJECT_ROOT_DIR}/shell_scripts/common_utils.sh" << 'EOF'
#!/bin/bash

# Common shell utilities for RTM Automation processes
# This script is called from main.py via execute_shell_script function

# Print a timestamped log message with color
log_message() {
  local level="$1"
  local message="$2"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

  case "$level" in
    "INFO")
      # Blue text for info
      echo -e "\e[34m[$timestamp] [INFO] $message\e[0m"
      ;;
    "SUCCESS")
      # Green text for success
      echo -e "\e[32m[$timestamp] [SUCCESS] $message\e[0m"
      ;;
    "WARNING")
      # Yellow text for warnings
      echo -e "\e[33m[$timestamp] [WARNING] $message\e[0m"
      ;;
    "ERROR")
      # Red text for errors
      echo -e "\e[31m[$timestamp] [ERROR] $message\e[0m"
      ;;
    *)
      # Default - white text for other levels
      echo "[$timestamp] [$level] $message"
      ;;
  esac
}

# Check that required environment variables are set
check_env_vars() {
  local missing_vars=()

  for var_name in "$@"; do
    if [ -z "${!var_name}" ]; then
      missing_vars+=("$var_name")
    fi
  done

  if [ ${#missing_vars[@]} -gt 0 ]; then
    log_message "ERROR" "Missing required environment variables: ${missing_vars[*]}"
    return 1
  fi

  return 0
}

# Get the absolute path to the project root directory
get_project_root() {
  local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  echo "$(cd "$script_dir/.." && pwd)"
}

# Show system info for debugging
show_system_info() {
  log_message "INFO" "System Information:"
  echo "OS: $(uname -a)"
  echo "Python: $(python --version 2>&1)"
  echo "Bash: $BASH_VERSION"
  echo "Current directory: $(pwd)"
  echo "Project root: $(get_project_root)"
}

# Check if a command exists in path
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# If running as main script, show usage
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  log_message "INFO" "common_utils.sh - Common utilities for RTM Automation"
  log_message "INFO" "This script is typically sourced by other scripts or called from Python."

  # Display sample usage
  log_message "SUCCESS" "This is a success message"
  log_message "WARNING" "This is a warning message"
  log_message "ERROR" "This is an error message"

  show_system_info
fi
EOF
    chmod +x "${PROJECT_ROOT_DIR}/shell_scripts/common_utils.sh"
    log_message "SUCCESS" "common_utils.sh created and made executable"
fi

# Fix 2: Create correct path references in main.py for the shell script
log_message "INFO" "Checking main.py for shell script references..."
MAIN_PY="${PROJECT_ROOT_DIR}/code/main.py"
if [ -f "$MAIN_PY" ]; then
    # Create backup
    cp "$MAIN_PY" "${MAIN_PY}.bak"
    log_message "INFO" "Backup of main.py created at ${MAIN_PY}.bak"

    # Update shell script path in main.py if needed
    if grep -q "shell_scripts/common_utils.sh" "$MAIN_PY"; then
        log_message "INFO" "Shell script path found in main.py"

        # Check if the path is constructed correctly
        if grep -q "os.path.join(PROJECT_ROOT_DIR, 'shell_scripts', 'common_utils.sh')" "$MAIN_PY"; then
            log_message "SUCCESS" "Shell script path is correctly constructed in main.py"
        else
            log_message "WARNING" "Shell script path may not be correctly constructed in main.py"
            log_message "INFO" "Please check the path construction in main.py manually"
        fi
    else
        log_message "WARNING" "Shell script reference not found in main.py"
        log_message "INFO" "Please check main.py for how it references common_utils.sh"
    fi
else
    log_message "ERROR" "main.py not found at $MAIN_PY"
fi

# Fix 3: Check and fix YAML configuration issues
log_message "INFO" "Checking YAML configuration..."
CONFIG_YAML="${PROJECT_ROOT_DIR}/config/paths.yaml"
if [ -f "$CONFIG_YAML" ]; then
    # Try to parse the YAML file
    if command_exists python; then
        python -c "import yaml; yaml.safe_load(open('$CONFIG_YAML'))" 2>/dev/null
        if [ $? -eq 0 ]; then
            log_message "SUCCESS" "YAML configuration is valid"
        else
            log_message "ERROR" "YAML configuration is invalid"
            log_message "INFO" "Creating backup of paths.yaml..."
            cp "$CONFIG_YAML" "${CONFIG_YAML}.broken"
            log_message "INFO" "Creating a basic valid paths.yaml..."
            cat > "$CONFIG_YAML" << EOF
# RTM Automation Configuration

# Paths configuration
paths:
  input_dir: "input"
  output_dir: "output"
  logs_dir: "logs"
  data_dir: "data"
  docs_dir: "docs"

# OpenAI API configuration
openai:
  api_key_file: "config/openai_key.txt"  # Path relative to project root or absolute path

# RTM Pipeline configuration
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
            log_message "SUCCESS" "Created basic valid paths.yaml"
            log_message "INFO" "Original broken file is at ${CONFIG_YAML}.broken"
        fi
    else
        log_message "WARNING" "Python not available to check YAML validity"
    fi
else
    log_message "WARNING" "paths.yaml not found at $CONFIG_YAML"
    log_message "INFO" "Creating a basic paths.yaml configuration..."
    mkdir -p "$(dirname "$CONFIG_YAML")"
    cat > "$CONFIG_YAML" << EOF
# RTM Automation Configuration

# Paths configuration
paths:
  input_dir: "input"
  output_dir: "output"
  logs_dir: "logs"
  data_dir: "data"
  docs_dir: "docs"

# OpenAI API configuration
openai:
  api_key_file: "config/openai_key.txt"  # Path relative to project root or absolute path

# RTM Pipeline configuration
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
    log_message "SUCCESS" "Created basic paths.yaml configuration"
fi

# Fix 4: Set up OpenAI API key file
log_message "INFO" "Checking OpenAI API key configuration..."
if [ -f "$CONFIG_YAML" ]; then
    # Extract API key file path from config
    API_KEY_FILE_REL=$(grep -o 'api_key_file: *"[^"]*"' "$CONFIG_YAML" | awk -F'"' '{print $2}')
    if [ -n "$API_KEY_FILE_REL" ]; then
        # Convert to absolute path if relative
        if [[ "$API_KEY_FILE_REL" = /* ]]; then
            API_KEY_FILE="$API_KEY_FILE_REL"
        else
            API_KEY_FILE="${PROJECT_ROOT_DIR}/$API_KEY_FILE_REL"
        fi
        log_message "INFO" "OpenAI API key file path from config: $API_KEY_FILE"

        # Check if the file exists
        if [ -f "$API_KEY_FILE" ]; then
            log_message "SUCCESS" "OpenAI API key file exists"
        else
            log_message "WARNING" "OpenAI API key file does not exist at $API_KEY_FILE"
            log_message "INFO" "Creating directory for OpenAI API key file..."
            mkdir -p "$(dirname "$API_KEY_FILE")"
            log_message "INFO" "Creating placeholder OpenAI API key file..."
            echo "sk-your-openai-api-key-goes-here" > "$API_KEY_FILE"
            log_message "WARNING" "Created placeholder API key file at $API_KEY_FILE. Please replace with your actual OpenAI API key."
        fi
    else
        log_message "WARNING" "Could not find api_key_file setting in paths.yaml"
    fi
else
    log_message "ERROR" "paths.yaml not found at $CONFIG_YAML, cannot determine OpenAI API key file path"
fi

# Fix 5: Check and create necessary directories
log_message "INFO" "Ensuring required directories exist..."
directories=(
    "input"
    "output"
    "logs"
    "config"
    "data"
    "docs"
    "output/rtm"
)

for dir in "${directories[@]}"; do
    if [ -d "${PROJECT_ROOT_DIR}/$dir" ]; then
        log_message "INFO" "Directory '$dir' already exists."
    else
        mkdir -p "${PROJECT_ROOT_DIR}/$dir"
        log_message "SUCCESS" "Created directory '$dir'."
    fi
done

# Create .gitkeep files in empty directories to ensure they're tracked by Git
for dir in "${directories[@]}"; do
    dir_path="${PROJECT_ROOT_DIR}/$dir"
    if [ -d "$dir_path" ] && [ -z "$(ls -A "$dir_path")" ]; then
        touch "$dir_path/.gitkeep"
        log_message "INFO" "Created .gitkeep in empty '$dir' directory."
    fi
done

log_message "SUCCESS" "RTM issues fix script completed!"
log_message "INFO" "Run './shell_scripts/run_rtm.sh' to test the RTM automation."
log_message "INFO" "Run './shell_scripts/rtm_status.sh --verbose' to check the current status."