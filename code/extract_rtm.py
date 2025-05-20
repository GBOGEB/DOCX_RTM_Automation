import yaml, re
paths = yaml.safe_load(open('config/paths.yaml'))
lines = open(paths['md_output'], encoding="utf-8").readlines()
rtm = [
    {"Req.#": m.group(1), "RS": m.group(2).strip()}
    for l in lines if (m := re.match(r"^(QQQ_[0-9]{3,})(.*)", l))
]
yaml.dump(rtm, open(paths['rtm_yaml'], "w"), allow_unicode=True)
print(f"✅ RTM YAML created with {len(rtm)} requirements.")
