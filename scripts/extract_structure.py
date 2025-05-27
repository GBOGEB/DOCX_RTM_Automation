#!/usr/bin/env python
import sys
import json
from docx import Document


def parse(path):
    doc = Document(path)
    out = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        if t.startswith("QQQ"):
            tag, rest = t.split(None, 1) if " " in t else (t, "")
            out.append({"type": "tag", "tag": tag, "text": rest})
        elif p.style.name.startswith("Heading"):
            lvl = int(p.style.name.split()[-1])
            out.append({"type": "h", "lvl": lvl, "text": t})
    return out


if __name__ == "__main__":
    print(json.dumps(parse(sys.argv[1]), indent=2))
