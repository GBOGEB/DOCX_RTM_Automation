#!/bin/bash
pip install -r config/requirements.txt
python code/word_to_md.py
python code/md_to_json_yaml.py
python code/extract_outline.py
python code/extract_rtm.py
