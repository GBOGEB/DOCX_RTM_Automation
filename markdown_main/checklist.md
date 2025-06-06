python_path: "C:\\Users\\gbonthuy\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"

tasks:
  - name: "Convert Word to Markdown"
    script: "src/core/word_to_md.py"
    status: "pending" # Example additional field
    notes: "Ensure Pandoc is installed."

  - name: "Clean Outline"
    script: "scripts/clean_outline.py" # Assuming it's moved to scripts
    input: "input/MASTER_outline.yaml"
    output: "output/MASTER_outline.yaml"
    status: "pending"