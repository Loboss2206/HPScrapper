import os

def return_datas(path="credentials.txt"):
    if not os.path.exists(path):
        print(f"[❌] {path} introuvable.")
        exit(1)

    with open(path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) < 2:
        exit(1)

    return lines[0], lines[1]
