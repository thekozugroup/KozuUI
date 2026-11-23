"""Verify the editable kit, token values, component sources and published previews."""
import hashlib
import json
import re
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(name):
    return json.loads((ROOT / name).read_text())


def verify():
    tokens = read_json("Kozu.tokens.json")
    qa = read_json("Design QA.json")
    catalog = read_json("Component inventory.json")
    with zipfile.ZipFile(ROOT / "Kozu Universal UI Kit.figcraft") as archive:
        doc = json.loads(archive.read("document.json"))
        nodes = {int(key): value for key, value in doc["nodes"].items()}
        variables = {item["id"]: item for item in doc["variables"]["variables"]}
        assets = {item["hash"] for item in doc["imageIndex"]}
        assert set(archive.namelist()) == {"document.json", *("images/" + h for h in assets)}
        for digest in assets:
            assert hashlib.sha256(archive.read("images/" + digest)).hexdigest() == digest
    material_paths = [recipe["asset"] for recipe in tokens["materials"].values()]
    for path in [*material_paths, *tokens["portraits"]]:
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() in assets, path
    order = []
    visited = set()
    link_count = 0
    def walk(node_id, parent=None):
        nonlocal link_count
        assert node_id not in visited, node_id
        visited.add(node_id)
        node = nodes[node_id]
        assert node.get("parent") == parent, node["name"]
        if node["type"] == "instance":
            assert nodes[node["component"]]["type"] == "component", node["name"]
        if "source" in node:
            assert node["source"] in nodes, node["name"]
        assert set(node.get("bound", {}).values()) <= variables.keys(), node["name"]
        for field in ("fills", "strokes"):
            for paint in node.get(field, []):
                if paint["type"] == "image":
                    assert paint["image"] in assets
        if node.get("strokes"):
            assert node["name"].startswith("Lucide / "), node["name"]
        for event in node.get("interactions", []):
            for action in event["actions"]:
                if action.get("dest"):
                    target = nodes[action["dest"]]
                    assert target["type"] in ("frame", "component"), target
                    link_count += 1
        for child in node.get("children", []):
            walk(child, node_id)
    for page in doc["pages"]:
        walk(page)
        order.extend(nodes[page]["children"])
    assert visited == nodes.keys()
    assert order == [item["id"] for item in qa["artboards"]]
    assert len(nodes) == qa["counts"]["nodes"]
    assert link_count == qa["counts"]["prototypeActions"]
    assert {item["id"] for item in catalog} == {i for i,n in nodes.items() if n["type"] == "component"}
    # These are adjacent text layers so the cents can use a different ink.
    for dollars in (n for n in nodes.values() if n.get("characters") == "$117,450"):
        siblings = nodes[dollars["parent"]]["children"]
        cents = next(nodes[i] for i in siblings if nodes[i].get("characters") == ".17")
        size = dollars["style"]["font_size"]
        assert dollars["width"] >= 4.7 * size, f'Balance may wrap: {dollars["name"]}'
        assert dollars["transform"][5] == cents["transform"][5]
        assert dollars["transform"][4] + dollars["width"] == cents["transform"][4]
    for variable in variables.values():
        value = next(iter(variable["values"].values()))["value"]
        if variable["resolvedType"] == "color":
            packed = "#" + "".join(f"{round(value[c] * 255):02X}" for c in "rgba")
            if packed.endswith("FF"):
                packed = packed[:-2]
            assert tokens["colors"][variable["name"]].upper() == packed
        else:
            assert tokens["dimensions"][variable["name"]] == value
    css = (ROOT / "web/kozu.css").read_text().upper()
    for prop,role in tokens["cssRoles"].items():
        value = tokens["colors"][role].upper()
        assert re.search(re.escape(prop.upper()) + r"\s*:\s*" + re.escape(value) + r"\s*;", css), prop
    previews = {item["preview"] for item in qa["artboards"]}
    assert previews == {p.name for p in (ROOT / "Previews").glob("*.png")}
    for board in qa["artboards"]:
        with (ROOT / "Previews" / board["preview"]).open("rb") as stream:
            header = stream.read(24)
        assert header[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", header[16:24])
        assert abs(width * board["height"] - height * board["width"]) < max(width, height)
    print(f"Verified {len(doc['pages'])} pages, {len(order)} artboards, {len(catalog)} masters, "
          f"{len(variables)} variables and {link_count} prototype actions.")


if __name__ == "__main__":
    verify()
