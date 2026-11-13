"""Đọc FitLifeHub.v2.dbml thành cấu trúc Python (bảng, cột, PK, FK, chỉ mục)."""
import re

DBML_PATH = r"D:\HK1_Năm 3\CSDL Nâng cao - Pass hangvu@hcmus-20260913\Đồ án\FitLifeHub.v2.dbml"


def parse(path=DBML_PATH):
    text = open(path, encoding="utf-8").read()
    tables = {}
    order = []
    cur = None
    in_idx = False
    in_note = False
    for line in text.splitlines():
        m = re.match(r"^Table (\w+) \{", line)
        if m:
            cur = {"name": m.group(1), "cols": [], "pk": [], "indexes": [], "note": ""}
            tables[cur["name"]] = cur
            order.append(cur["name"])
            in_idx = in_note = False
            continue
        if cur is None:
            continue
        if line.startswith("}"):
            cur = None
            continue
        if re.match(r"^\s{2}indexes \{", line):
            in_idx = True
            continue
        if in_idx:
            if re.match(r"^\s{2}\}", line):
                in_idx = False
                continue
            mi = re.match(r"^\s{4}\(([^)]*)\)\s*\[(.*)\]\s*$", line)
            if mi:
                cols = [c.strip() for c in mi.group(1).split(",")]
                attrs = mi.group(2)
                cur["indexes"].append({"cols": cols, "attrs": attrs})
                if re.search(r"\bpk\b", attrs):
                    cur["pk"] = cols
            continue
        if re.match(r"^\s{2}Note:", line) or in_note:
            in_note = True
            cur["note"] += line + "\n"
            if line.strip().endswith("'") and not line.strip().endswith("'''") or line.strip() == "'''" and cur["note"].count("'''") >= 2:
                in_note = False
            continue
        mc = re.match(r"^\s{2}(\w+)\s+(\w+(?:\(\d+(?:,\d+)?\))?)\s*(?:\[(.*)\])?\s*$", line)
        if mc:
            name, typ, attrs = mc.group(1), mc.group(2), mc.group(3) or ""
            nullable = bool(re.search(r"(?<!not )\bnull\b", attrs)) and "not null" not in attrs
            cur["cols"].append({"name": name, "type": typ.upper(), "null": nullable, "attrs": attrs})
            if re.search(r"\bpk\b", attrs):
                cur["pk"].append(name)
    refs = []
    for m in re.finditer(r"^Ref (\w+): (\w+)\.(\([\w, ]+\)|\w+) ([>-]) (\w+)\.(\([\w, ]+\)|\w+)\s*(?://\s*(.*))?$", text, re.M):
        def cols(s):
            return [c.strip() for c in s.strip("()").split(",")]
        refs.append({"name": m.group(1), "t": m.group(2), "c": cols(m.group(3)), "op": m.group(4),
                     "rt": m.group(5), "rc": cols(m.group(6)), "label": (m.group(7) or "").strip()})
    return {"tables": tables, "order": order, "refs": refs}


if __name__ == "__main__":
    d = parse()
    print(len(d["order"]), "tables;", sum(len(t["cols"]) for t in d["tables"].values()), "cols;", len(d["refs"]), "refs")
    for n in d["order"]:
        t = d["tables"][n]
        print(n, len(t["cols"]), "PK", t["pk"])
    for r in d["refs"]:
        print(r["name"], r["t"], r["c"], r["op"], r["rt"], r["rc"], "//", r["label"])
