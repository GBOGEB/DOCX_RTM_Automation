import yaml, re
paths = yaml.safe_load(open('config/paths.yaml'))
lines = open(paths['md_output'], encoding="utf-8").readlines()
outline = [
    {'level': len(m.group(1)), 'title': m.group(2).strip()}
    for l in lines if (m := re.match(r'^(#{1,7})\s(.*)', l))
]
yaml.dump(outline, open(paths['outline_yaml'], "w"), allow_unicode=True)
print(f"✅ Outline YAML created with {len(outline)} entries.")
