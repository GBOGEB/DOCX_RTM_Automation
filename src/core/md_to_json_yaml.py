import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import json
import re

paths = yaml.safe_load(open("config/paths.yaml"))
lines = open(paths["md_output"], encoding="utf-8").readlines()
data = {
    "requirements": [l.strip() for l in lines if re.match(r"^QQQ_[0-9]{3}", l)],
    "headings": [l.strip() for l in lines if re.match(r"^#{1,7}\s", l)],
}
yaml.dump(data, open(paths["yaml_output"], "w"), allow_unicode=True)
json.dump(data, open(paths["json_output"], "w"), indent=2, ensure_ascii=False)
print("✅ Markdown → YAML/JSON parsing complete.")
