import os, subprocess, yaml, re

with open('config/paths.yaml') as file:
    paths = yaml.safe_load(file)

# Ensure output directory exists
os.makedirs(os.path.dirname(paths['md_output']), exist_ok=True)

try:
    subprocess.run([
        paths['pandoc_path'], 
        paths['word_master'], 
        "-f", "docx", 
        "-t", "markdown",
        "--toc", "--toc-depth=6",  # Changed from 7 to 6
        "--number-sections",
        "--lua-filter=config/extend_headings.lua",
        "-o", paths['md_output']
    ], check=True)
    print("✅ DOCX → Markdown conversion complete.")
except subprocess.CalledProcessError as e:
    print("❌ Conversion failed.", e)
    exit(1)

# Process the generated Markdown file to extract QQQ requirements and outline
lines = open(paths['md_output'], encoding="utf-8").readlines()

# Extract QQQ requirements
rtm = []
for l in lines:
    # Use robust matching for formats like QQQ_123, QQQ.123, QQQ-123, QQQ 123
    match = re.search(r"\b(QQQ[._\s-]*[0-9]{3,})\b(.*)", l)
    if match:
        rtm.append({
            "Req.#": match.group(1).replace(' ', '_').replace('-', '_').replace('.', '_'),
            "RS": match.group(2).strip()
        })

yaml.dump(rtm, open(paths['rtm_yaml'], "w"), allow_unicode=True)
print(f"✅ RTM YAML created with {len(rtm)} requirements.")

# Extract outline from TOC-style headings
outline = []
for l in lines:
    # Match TOC style: [3.2.5 QPLANT performance [21](#_Toc...)]
    toc_match = re.match(r"\[(\d+(\.\d+)*\s+.+?)\s+\[\d+\]", l)
    if toc_match:
        full_title = toc_match.group(1).strip()
        section_number = full_title.split()[0]
        title = " ".join(full_title.split()[1:])
        outline.append({
            'section': section_number,
            'title': title
        })

yaml.dump(outline, open(paths['outline_yaml'], "w"), allow_unicode=True)
print(f"✅ Outline YAML created with {len(outline)} sections.")
