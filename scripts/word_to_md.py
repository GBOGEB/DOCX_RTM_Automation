#!/usr/bin/env python
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