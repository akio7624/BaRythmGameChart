import json

idx = [0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14]

for i in idx:
    with open(f"json/{i}.json") as f:
        data = json.load(f)
    cnt = len(data["data"]["notes"])
    print(f"{i}.json 노트개수: {cnt}")