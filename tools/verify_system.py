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


def verify_dot_grids(nodes, tokens):
    from math import floor, isclose

    spec = tokens["feedback"]["dotGrid"]
    diameter, pitch = spec["diameter"], spec["pitch"]
    assert (diameter, pitch) == (4, 8)
    grids = {}
    for key, node in nodes.items():
        raw = node.get("plugin_data", {}).get("kozu.dotGrid")
        if not raw:
            continue
        spec = json.loads(raw)
        grids[key] = spec
        assert (spec["diameter"], spec["pitch"]) == (diameter, pitch)
        rows, width, height = spec["rows"], node["width"], node["height"]
        columns = max(0, 1 + floor((width - diameter) / pitch))
        dy = (height - (rows - 1) * pitch - diameter) / 2
        capacity = spec["bankColumns"]
        assert capacity >= columns and dy >= 0
        wraps = []
        if spec["mode"] == "native-gated":
            from fractions import Fraction
            from math import ceil

            field, = [nodes[i] for i in node["children"]]
            assert field["child_layout"]["max_w"] == diameter + (capacity - 1) * pitch
            planes = [nodes[i] for i in field["children"]]
            pct = Fraction(*spec["percentRatio"])
            assert 0 <= pct <= 100
            wraps.append(planes[0])
            if 0 < pct < 100:
                mask, lit = [nodes[i] for i in planes[1]["children"]]
                assert mask["is_mask"]
                wraps.append(lit)
                total = floor(capacity * rows * pct / 100)
                assert len(mask["children"]) == total
                for index, gate_id in enumerate(mask["children"]):
                    gate = nodes[gate_id]
                    c, r = divmod(index, rows)
                    assert gate["height"] == diameter and gate["child_layout"]["grid_row"] == r
                    start, activation = [nodes[i] for i in gate["children"]]
                    assert start["width"] == 0
                    threshold = ceil(Fraction(100 * (index + 1), rows) / pct)
                    assert activation["width"] == diameter + (threshold - 1) * pitch
                    bin_node, = [nodes[i] for i in activation["children"]]
                    assert bin_node["transform"][4] == c * pitch and bin_node["width"] == pitch
        else:
            assert spec["mode"] == "native-wrap", (key, spec["mode"])
            wraps.append(node)
        for bank in wraps:
            assert len(bank["children"]) == rows
            for r, row_id in enumerate(bank["children"]):
                row = nodes[row_id]
                assert row["layout"]["wrap"] and row["layout"]["main_align"] == "center"
                assert row["height"] == diameter
                offset = dy if spec["mode"] == "native-wrap" else 0
                assert isclose(row["transform"][5], offset + r * pitch)
                assert len(row["children"]) == 1 + capacity
                assert nodes[row["children"][0]]["width"] == 0
                for c, cell_id in enumerate(row["children"][1:]):
                    cell = nodes[cell_id]
                    assert cell["width"] == (pitch if c else diameter)
                    for dot_id in cell["children"]:
                        dot = nodes[dot_id]
                        assert dot["type"] == "ellipse" and dot["transform"][4:] == [cell["width"] - diameter, 0]
                        assert dot["width"] == dot["height"] == diameter
    assert grids, "No annotated dot grids"
    return grids



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
    # Check both appearances. The first mode alone cannot catch a dark-mode import collision.
    by_name = {v["name"]: v for v in variables.values()}
    appearance = next(c for c in doc["variables"]["collections"] if c["name"] == "Kozu / appearance")
    for mode in appearance["modes"]:
        theme = mode["name"].lower()
        expected = {"role/" + name: color for name, color in tokens["palette"]["semantic"][theme].items()}
        for role, recipe in tokens["glass"]["recipes"].items():
            alpha = round(255 * recipe[theme + "Opacity"])
            expected["glass/" + role] = tokens["glass"]["tint"][theme] + f"{alpha:02X}"
        for role, color in expected.items():
            paint = by_name[role]["values"][mode["id"]]["value"]
            channels = "rgba" if len(color) == 9 else "rgb"
            assert color.upper() == "#" + "".join(f"{round(255 * paint[c]):02X}" for c in channels), role
    for hue, ramp in tokens["palette"]["ramps"].items():
        for grade, value in ramp.items():
            assert tokens["colors"][f"palette/{hue.title()}/{grade}"] == value

    progress = tokens["feedback"]["progress"]
    grids = verify_dot_grids(nodes, tokens)
    meters = [nodes[i] for i, g in grids.items() if nodes[nodes[i]["parent"]]["name"] in ("Inbox progress", "Flow progress", "Scout progress")]
    assert len(meters) >= 3
    for track in meters:
        parent = nodes[track["parent"]]
        label, _, value = (nodes[i] for i in parent["children"])
        assert label["style"]["font_size"] == progress["labelSize"]
        assert value["style"]["font_size"] == progress["valueSize"]
        assert label["transform"][4] == parent["width"] - value["width"] - value["transform"][4] == progress["sideInset"]
        assert track["width"] > 2 * label["width"]
    listening = next(n for n in nodes.values() if n["name"] == "Waveform / Playback")
    phases = [nodes[i] for i in listening["children"]]
    assert len(phases) == 4
    for phase, successor in zip(phases[:3], phases[1:3] + phases[:1]):
        assert any(a.get("type") == "changeTo" and a.get("dest") == successor["id"]
                   for event in phase.get("interactions", []) for a in event["actions"])
    assert not phases[-1].get("interactions")
    inputs = [n for n in nodes.values() if n["name"] == "Tasks / Listening input"]
    assert len(inputs) == 2
    for bar in inputs:
        children = [nodes[i] for i in bar["children"]]
        wave = next(n for n in children if n["name"] == "Waveform width host")
        stop = next(n for n in children if n["name"] == "Icon button / Stop listening")
        assert wave["width"] > bar["width"] / 2 and wave["constraints"]["horizontal"] == "leftRight"
        assert min(stop["width"], stop["height"]) >= tokens["geometry"]["touchTarget"]
        instance, = [nodes[i] for i in wave["children"]]
        assert any(c in grids and grids[c]["mode"] == "native-wrap" for c in instance["children"])
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
