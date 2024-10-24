import json

with open("json/original.js", "r") as f:
    content = f.read()

for idx, line in enumerate(content.split("\n")):
    if not line:
        continue
    txt = line[12:-2]
    data = json.loads(txt)
    with open(f"json/{idx}.json", "w") as f:
        print(idx)
        f.write(json.dumps(data, indent=4))
