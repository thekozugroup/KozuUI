"""List, refresh, or resize marked Kozu grids in a FigCraft archive."""

import argparse
from copy import copy, deepcopy
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from graphlib import TopologicalSorter
import json
import math
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
from zipfile import BadZipFile, ZipFile


MARKER = "kozu.dotGrid"
DOCUMENT = "document.json"
PITCH, DIAMETER = 8, 4
IDENTITY = [1, 0, 0, 1]
CENTER = {"horizontal": "center", "vertical": "center"}
DOT = re.compile(r"Dot / (Lit|Blank|Signal) / ([1-9]\d*)\.([1-9]\d*)")
ROW = re.compile(r"Wrap row / ([1-9]\d*)")
CELL = re.compile(r"Wrap column / (\d+)")
LIVE = ("native-gated", "native-progress")


def width(value):
    if isinstance(value, bool):
        raise ValueError("width must be a number")
    value = float(value)
    if value < 0 or not math.isfinite(value):
        raise ValueError("width must be finite and nonnegative")
    return value


def span(count):
    return DIAMETER + PITCH * (count - 1) if count else 0


def columns(size):
    return 0 if size < DIAMETER else 1 + math.floor((size - DIAMETER) / PITCH)


def percent(value):
    try:
        value = Decimal(str(value))
    except InvalidOperation:
        raise ValueError("percent must be a number in [0, 100]") from None
    if not value.is_finite() or not 0 <= value <= 100:
        raise ValueError("percent must be a number in [0, 100]")
    return value


def stored_percent(meta):
    if "percentRatio" in meta:
        numerator, denominator = meta["percentRatio"]
        if type(numerator) is not int or type(denominator) is not int or denominator <= 0:
            raise ValueError("invalid percentRatio")
        value = Fraction(numerator, denominator)
        if value < 0 or value > 100:
            raise ValueError("percentRatio must be in [0, 100]")
        return value
    return Fraction(percent(meta["percent"]))


def lit_count(rows, count, value):
    numerator, denominator = value.as_integer_ratio()
    return rows * count * numerator // (100 * denominator)


def position(node):
    transform = node["transform"]
    if len(transform) != 6 or transform[:4] != IDENTITY or not all(map(math.isfinite, transform[4:])):
        raise ValueError(f'{node["id"]}: expected a translation-only transform')
    return transform[4:]


def move(node, x, y, w, h):
    if position(node) != [x, y]:
        node["transform"][4:] = [x, y]
    if node["width"] != w:
        node["width"] = w
    if node["height"] != h:
        node["height"] = h


def paint(node):
    data = {"fills": node["fills"]}
    if "fill" in node.get("bound", {}):
        data["bound"] = {"fill": node["bound"]["fill"]}
    return data


def apply_paint(node, data):
    node["fills"] = deepcopy(data["fills"])
    fill = data.get("bound", {}).get("fill")
    if fill is not None:
        node.setdefault("bound", {})["fill"] = fill
    elif "fill" in node.get("bound", {}):
        del node["bound"]["fill"]
        if not node["bound"]:
            del node["bound"]


def period(sequence):
    # The prefix table also finds a period when the bank ends mid-cycle.
    prefix = [0] * len(sequence)
    for i in range(1, len(sequence)):
        j = prefix[i - 1]
        while j and sequence[i] != sequence[j]:
            j = prefix[j - 1]
        prefix[i] = j + (sequence[i] == sequence[j])
    return len(sequence) - prefix[-1]


def layout(mode="horizontal", wrap=False, gap=0):
    return dict(mode=mode, wrap=wrap, gap=gap, cross_gap=4 if wrap else 0,
                padding=[0] * 4, main_align="center" if wrap else "min", cross_align="min",
                content_align="auto", grid_columns=2, grid_rows=2, column_tracks=[],
                row_tracks=[], strokes_included=True, reverse_z=False)


def grid_layout(tracks, cross_gap=0):
    return dict(layout("grid"), grid_columns=1, grid_rows=len(tracks), cross_gap=cross_gap,
                column_tracks=[{"sizing": "fill", "value": 1}],
                row_tracks=[{"sizing": "fixed", "value": h} for h in tracks])


def native_progress_spec(node, meta, bank):
    """Build the v1 gated layout keyed by bank, role and whole-cell coordinate."""
    parts = {}
    rows = meta["rows"]
    size, height = min(node["width"], span(bank)), span(rows)
    count = columns(size)
    center = (size - span(count)) / 2
    fill = {"sizing_h": "fill", "sizing_v": "fixed"}
    responsive = {"horizontal": "leftRight", "vertical": "center"}
    value = stored_percent(meta)

    def part(key, parent, kind, name, x, y, w, h, **props):
        parts[key] = parent, dict(type=kind, name=name, transform=[*IDENTITY, x, y],
                                  width=w, height=h, **props)

    def frame(key, parent, name, x, y, w, h, **props):
        part(key, parent, "frame", name, x, y, w, h, **props)

    def plane(key, parent, name, **props):
        frame(key, parent, name, 0, 0, size, height, clip=False,
              constraints=responsive, child_layout=dict(fill, grid_column=0, grid_row=0), **props)

    def dots(parent, role, colors):
        layer = (role,)
        plane(layer, parent, f"{role} dot bank", layout=layout("vertical", gap=PITCH - DIAMETER))
        for r in range(rows):
            row = (role, "row", r)
            frame(row, layer, f"{role} wrap / {r + 1}", 0, r * PITCH, size, DIAMETER,
                  clip=True, constraints=responsive, layout=layout(wrap=True), child_layout=fill)
            frame((role, "sentinel", r), row, "Wrap sentinel", 0, 0, 0, DIAMETER, clip=False)
            for c in range(bank):
                pad = 0 if c == 0 else PITCH - DIAMETER
                x = center + c * PITCH - pad if c < count else 0
                y = 0 if c < count else PITCH * (1 + (c - count) // max(1, count))
                slot = (role, "column", r, c)
                frame(slot, row, f"Wrap column / {c + 1:02d}", x, y, DIAMETER + pad, DIAMETER, clip=False)
                part((role, "dot", r, c), slot, "ellipse", f"Dot / {role} / {c + 1}.{r + 1}",
                     pad, 0, DIAMETER, DIAMETER, start=0, sweep=math.tau, inner=0, **colors)

    field = ("field",)
    frame(field, None, "Centered progress field", (node["width"] - size) / 2,
          (node["height"] - height) / 2, size, height, clip=False,
          child_layout=dict(fill, max_w=span(bank)), layout=grid_layout([height]))
    if value == 100:
        dots(field, "Lit", meta["activePaint"])
    else:
        dots(field, "Blank", meta["blankPaint"])
        if value:
            scope, mask = ("overlay",), ("mask",)
            plane(scope, field, "Lit overlay", layout=grid_layout([height]))
            plane(mask, scope, "Whole-dot alpha gate", is_mask=True,
                  layout=grid_layout([DIAMETER] * rows, PITCH - DIAMETER))
            numerator, denominator = value.as_integer_ratio()
            scale = rows * numerator
            white = {"type": "solid", "color": dict(r=1, g=1, b=1, a=1),
                     "opacity": 1, "visible": True, "blend": "normal"}
            for c in range(lit_count(rows, bank, value) // rows + 1):
                for r in range(rows):
                    required = ((c * rows + r + 1) * 100 * denominator + scale - 1) // scale
                    if required > bank:
                        continue
                    gate, slot = ("gate", r, c), ("gate slot", r, c)
                    threshold = span(required)
                    frame(gate, mask, f"Gate / {c + 1}.{r + 1}", 0, r * PITCH, size, DIAMETER, clip=True,
                          constraints=responsive, layout=dict(layout(wrap=True), main_align="min"),
                          child_layout=dict(fill, grid_column=0, grid_row=r))
                    frame(("gate sentinel", r, c), gate, "Gate sentinel", 0, 0, 0, DIAMETER, clip=False)
                    frame(slot, gate, "Activation threshold", 0, 0 if size >= threshold else PITCH,
                          threshold, DIAMETER, clip=False)
                    part(("bin", r, c), slot, "rectangle", "Whole column bin",
                         c * PITCH, 0, PITCH, DIAMETER, fills=[white])
            dots(scope, "Lit", meta["activePaint"])
    return parts


class Grids:
    def __init__(self, document):
        if document.get("format") != "figcraft" or document.get("version") != 1:
            raise ValueError("expected a version 1 FigCraft document")
        self.document = document
        self.nodes = document["nodes"]
        self.next_id = max(document["next_id"], max(map(int, self.nodes), default=0) + 1)
        self.grids = {}
        self.parts = {}
        self.retired = set()
        for key, node in self.nodes.items():
            if MARKER not in node.get("plugin_data", {}):
                continue
            meta = json.loads(node["plugin_data"][MARKER])
            number = node["id"]
            if str(number) != key or meta["version"] != 1:
                raise ValueError(f"{number}: invalid grid ID or metadata version")
            kind, mode = meta["kind"], meta["mode"]
            if not (kind == "progress" and mode in ("authored", *LIVE)
                    or kind == "listening" and mode in ("authored", "native-wrap")):
                raise ValueError(f"{number}: unsupported grid {kind}/{mode}")
            rows = meta["rows"]
            if (meta["pitch"], meta["diameter"]) != (PITCH, DIAMETER) or (
                type(rows) is not int or rows < (kind == "progress" or mode != "authored")
                or span(rows) > width(node["height"])
            ):
                raise ValueError(f"{number}: invalid row geometry")
            width(node["width"])
            position(node)
            self.grids[number] = meta
            self.parts[number] = self.read_parts(node, meta)
        dependencies = {}
        for number, meta in self.grids.items():
            source = self.at(number).get("source")
            if source is not None:
                master = self.grids.get(source, {})
                if master.get("kind") != meta["kind"] or (
                    master.get("mode") != meta["mode"] and
                    not (master.get("mode") in LIVE and meta["mode"] in LIVE)
                ):
                    raise ValueError(f"{number}: incompatible grid source {source}")
                dependencies[number] = [source]
            else:
                dependencies[number] = []
        self.order = list(TopologicalSorter(dependencies).static_order())
        self.family = {}
        for number in self.order:
            source = self.at(number).get("source")
            self.family[number] = number if source is None else self.family[source]

    def at(self, number):
        return self.nodes[str(number)]

    def children(self, parent):
        for number in parent["children"]:
            node = self.at(number)
            if node["id"] != number or node.get("parent") != parent["id"]:
                raise ValueError(f"{number}: invalid grid child or parent")
            yield node

    def read_parts(self, node, meta):
        parts = {}

        def record(key, part, kind):
            if key in parts or part["type"] != kind:
                raise ValueError(f'{part["id"]}: invalid or duplicate {part["name"]}')
            position(part)
            parts[key] = part

        def dot(part, expected=None):
            match = DOT.fullmatch(part["name"])
            if not match:
                return
            role, col, row = match.groups()
            key = ("dot", int(row) - 1, int(col) - 1)
            if (expected is not None and key != expected) or (
                (role == "Signal") != (meta["kind"] == "listening")
            ):
                raise ValueError(f'{part["id"]}: invalid dot coordinate or role')
            record(key, part, "ellipse")

        rows = meta["rows"]
        if meta["mode"] == "authored":
            count = meta["columns"]
            if type(count) is not int or count < 0:
                raise ValueError(f'{node["id"]}: invalid column count')
            for part in self.children(node):
                dot(part)
            expected = {("dot", r, c) for r in range(rows) for c in range(count)}
            if parts.keys() != expected:
                raise ValueError(f'{node["id"]}: incomplete authored dot coordinates')
            return parts

        bank = meta["bankColumns"]
        if type(bank) is not int or bank < 1:
            raise ValueError(f'{node["id"]}: invalid wrap bank size')
        if meta["mode"] in LIVE:
            by_name = {}
            for key, (parent_key, spec) in native_progress_spec(node, meta, bank).items():
                parent = node if parent_key is None else parts[parent_key]
                if parent_key not in by_name:
                    children = list(self.children(parent))
                    names = {child["name"]: child for child in children}
                    if len(names) != len(children):
                        raise ValueError(f'{parent["id"]}: duplicate native progress child names')
                    by_name[parent_key] = names
                part = by_name[parent_key].get(spec["name"])
                if part is None:
                    raise ValueError(f'{parent["id"]}: missing {spec["name"]}')
                record(key, part, spec["type"])
            return parts
        for row in self.children(node):
            match = ROW.fullmatch(row["name"])
            if not match:
                continue
            r = int(match[1]) - 1
            record(("row", r), row, "frame")
            if r >= rows or not row.get("clip") or not row.get("layout", {}).get("wrap"):
                raise ValueError(f'{row["id"]}: expected a clipped native wrap row')
            row_children = list(self.children(row))
            if len(row_children) != bank + 1 or row_children[0]["name"] != "Wrap sentinel":
                raise ValueError(f'{row["id"]}: incomplete native wrap bank')
            record(("sentinel", r), row_children[0], "frame")
            for c, cell in enumerate(row_children[1:]):
                match = CELL.fullmatch(cell["name"])
                if not match or int(match[1]) != c + 1:
                    raise ValueError(f'{cell["id"]}: invalid wrap column order')
                record(("column", r, c), cell, "frame")
                for part in self.children(cell):
                    dot(part, ("dot", r, c))
        if any(("row", r) not in parts for r in range(rows)):
            raise ValueError(f'{node["id"]}: missing wrap row')
        return parts

    def add(self, parent, kind, name, x, y, w, h, **properties):
        number = self.next_id
        self.next_id += 1
        node = dict(id=number, parent=parent["id"], type=kind, name=name,
                    transform=[*IDENTITY, x, y], width=w, height=h, **properties)
        self.nodes[str(number)] = node
        parent["children"].append(number)
        return node

    def new_dot(self, parent, name, x, y, colors, constraints=None):
        node = self.add(parent, "ellipse", name, x, y, DIAMETER, DIAMETER,
                        start=0, sweep=math.tau, inner=0)
        if constraints is not None:
            node["constraints"] = deepcopy(constraints)
        apply_paint(node, colors)
        return node

    def list(self):
        for number, meta in self.grids.items():
            node = self.at(number)
            owner = self.at(node["parent"])
            names = [owner["name"]]
            ancestor = owner
            seen = {number}
            while ancestor["type"] != "page":
                if ancestor["id"] in seen:
                    raise ValueError(f"{number}: cyclic page ancestry")
                seen.add(ancestor["id"])
                ancestor = self.at(ancestor["parent"])
                names.append(ancestor["name"])
            page = names[-1]
            context = " / ".join(reversed(names[:-1]))
            value = f' {meta["percent"]:g}%' if meta["kind"] == "progress" else ""
            bank = f', {meta["bankColumns"]} bank columns' if "bankColumns" in meta else ""
            print(f'{number}  {page}  {context}  {node["name"]}  '
                  f'[{meta["mode"]}, {node["width"]:g} units{value}{bank}; owner {owner["id"]}]')
        if not self.grids:
            print("No marked dot grids.")

    def label(self, number):
        label = self.grids[number].get("valueLabel")
        if label is None:
            return None
        node = self.at(label)
        if node["type"] != "text":
            raise ValueError(f"{number}: percentage label {label} is not text")
        position(node)
        return node

    def value(self, number, value):
        meta = self.grids[number]
        label = self.label(number)
        text = format(value, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        meta["percent"] = float(value)
        meta["percentRatio"] = list(value.as_integer_ratio())
        if label is not None and label.get("characters") != text + "%":
            label["characters"] = text + "%"
            font = label.get("style", {}).get("font_size", 0)
            needed = math.ceil(font * (0.7 * sum(c.isdigit() for c in text) + 0.35 * ("." in text) + 1))
            if needed > label["width"]:
                if label.get("align_h") == "right":
                    label["transform"][4] -= needed - label["width"]
                label["width"] = needed

    def resolve_target(self, target):
        if target in self.grids:
            return target, None
        owner = self.at(target)
        if "children" not in owner:
            raise ValueError(f"{target}: expected a marked track or its owner")
        children = [node["id"] for node in self.children(owner) if node["id"] in self.grids]
        if len(children) != 1:
            raise ValueError(f"{target}: expected a marked track or its owner with exactly one marked track")
        return children[0], owner

    def resize(self, target, size, value):
        number, owner = self.resolve_target(target)
        node = self.at(number)
        parent = self.at(node["parent"])
        if size is not None and owner is None and node.get("child_layout", {}).get("sizing_h") == "fill":
            if parent.get("layout") and parent["children"] == [number]:
                # Keep native fill active by resizing the single-track wrapper.
                owner = parent
                size += owner["width"] - node["width"]
            elif parent.get("layout"):
                raise ValueError(f'{number}: native layout sets the track width; resize owner {parent["id"]}')
        label = self.label(number)
        previous_x = label["transform"][4] if label is not None else None
        previous_width = label["width"] if label is not None else None
        if value is not None:
            if self.grids[number]["kind"] != "progress":
                raise ValueError(f"{number}: only progress grids accept --percent")
            self.value(number, value)
        if size is not None:
            if owner is None:
                node["width"] = size
            else:
                delta = size - owner["width"]
                owner["width"] = size
                x, y = position(node)
                slot = max(0, node["width"] + delta)
                if label is not None and label["parent"] == owner["id"]:
                    ly = position(label)[1]
                    beside = y < ly + label["height"] and ly < y + node["height"] and previous_x >= x
                    if beside or label.get("constraints", {}).get("horizontal") == "right":
                        label["transform"][4] = previous_x + delta + previous_width - label["width"]
                    if beside:
                        gap = max(0, previous_x - x - node["width"])
                        slot = min(slot, max(0, label["transform"][4] - x - gap))
                node["width"] = slot
                host_id = owner.get("parent")
                if host_id is not None:
                    host = self.at(host_id)
                    if host["name"] == "Waveform width host" and host["children"] == [owner["id"]]:
                        host["width"] = size
        if position(node)[0] + node["width"] > parent["width"] + 1e-9:
            raise ValueError(f'{number}: track does not fit in owner {parent["id"]}; resize the owner')
        self.refresh(number)

    def space_label(self, number):
        label = self.label(number)
        if label is None:
            return
        node = self.at(number)
        if label["parent"] != node["parent"]:
            raise ValueError(f"{number}: expected the recorded percentage label beside its track")
        x, y = position(node)
        lx, ly = position(label)
        right = x + node["width"]
        limit = self.at(node["parent"])["width"] - label["width"]
        if node["width"] and y < ly + label["height"] and ly < y + node["height"]:
            if x <= lx < right:
                lx = min(right + PITCH, limit)
                if lx < right:
                    raise ValueError(f'{number}: no room beside the track for the percentage; resize owner {node["parent"]}')
            elif lx < x < lx + label["width"]:
                lx = max(0, x - label["width"] - PITCH)
                if lx + label["width"] > x:
                    raise ValueError(f"{number}: no room before the track for the percentage")
        if not 0 <= lx <= limit + 1e-9:
            raise ValueError(f'{number}: percentage does not fit in owner {node["parent"]}')
        label["transform"][4] = lx

    def authored(self, node, meta, parts):
        rows, count = meta["rows"], columns(node["width"])
        dx, dy = (node["width"] - span(count)) / 2, (node["height"] - span(rows)) / 2
        progress = meta["kind"] == "progress"
        if progress:
            filled = lit_count(rows, count, stored_percent(meta))
            meta.update(litCount=filled, authoredWidth=node["width"])
            for key in ("activePaint", "blankPaint"):
                if not isinstance(meta[key]["fills"], list):
                    raise ValueError(f'{node["id"]}: invalid {key}')
        else:
            samples = meta.get("signalPaints")
            if samples is None and count != meta["columns"]:
                samples = [[paint(parts["dot", r, c]) for c in range(meta["columns"])] for r in range(rows)]
                meta["signalPaints"] = deepcopy(samples)
            if count and samples is not None and (len(samples) != rows or any(not band for band in samples)):
                raise ValueError(f'{node["id"]}: no listening samples to grow this grid')
        result = {}
        for c in range(count):
            for r in range(rows):
                key = ("dot", r, c)
                dot = parts.get(key)
                if progress:
                    on = c * rows + r < filled
                    role = "Lit" if on else "Blank"
                    colors = meta["activePaint" if on else "blankPaint"]
                else:
                    role = "Signal"
                    band = samples[r] if samples is not None else None
                    colors = band[(2 * c + 1) * len(band) // (2 * count)] if band else paint(dot)
                name = f"Dot / {role} / {c + 1}.{r + 1}"
                x, y = dx + c * PITCH, dy + r * PITCH
                if dot is None:
                    dot = self.new_dot(node, name, x, y, colors, CENTER)
                else:
                    move(dot, x, y, DIAMETER, DIAMETER)
                    if dot["name"] != name or not progress and samples is not None:
                        apply_paint(dot, colors)
                    dot["name"] = name
                result[key] = dot
        removed = {dot["id"] for key, dot in parts.items() if key not in result}
        if removed:
            node["children"] = [number for number in node["children"] if number not in removed]
            self.retired.update(removed)
        meta["columns"] = count
        return result

    def wrapped(self, node, meta, parts, bank):
        rows, old_bank = meta["rows"], meta["bankColumns"]
        count = columns(node["width"])
        dx, dy = (node["width"] - span(count)) / 2, (node["height"] - span(rows)) / 2
        if bank > old_bank:
            pattern = [
                [paint(dot) if (dot := parts.get(("dot", r, c))) is not None else None for r in range(rows)]
                for c in range(old_bank)
            ]
            cycle = period(pattern)
        for r in range(rows):
            row = parts["row", r]
            move(row, 0, dy + r * PITCH, node["width"], DIAMETER)
            move(parts["sentinel", r], 0, 0, 0, DIAMETER)
            for c in range(bank):
                padding = 0 if c == 0 else PITCH - DIAMETER
                x = dx + c * PITCH - padding
                y = 0 if c < count else PITCH * (1 + (c - count) // max(1, count))
                key = ("column", r, c)
                cell = parts.get(key)
                if cell is None:
                    cell = self.add(row, "frame", f"Wrap column / {c + 1:02d}",
                                    x, y, padding + DIAMETER, DIAMETER, children=[], clip=False)
                    parts[key] = cell
                    colors = pattern[c % cycle][r]
                    if colors is not None:
                        parts["dot", r, c] = self.new_dot(
                            cell, f"Dot / Signal / {c + 1}.{r + 1}", padding, 0, colors)
                else:
                    move(cell, x, y, padding + DIAMETER, DIAMETER)
                    dot = parts.get(("dot", r, c))
                    if dot is not None:
                        move(dot, padding, 0, DIAMETER, DIAMETER)
        meta["bankColumns"] = bank
        return parts

    def native_progress(self, node, meta, parts, bank):
        spec = native_progress_spec(node, meta, bank)
        result = {}
        previous = {part["id"] for part in parts.values()}
        desired = {}
        for key, (parent_key, props) in spec.items():
            parent = node if parent_key is None else result[parent_key]
            part = parts.get(key)
            if part is None and key[0] in ("Blank", "Lit"):
                other = ("Blank" if key[0] == "Lit" else "Lit", *key[1:])
                if other not in spec:
                    part = parts.get(other)
            if part is None:
                extras = {"children": []} if props["type"] == "frame" else {}
                part = self.add(parent, props["type"], props["name"], *props["transform"][4:],
                                props["width"], props["height"], **extras)
            elif part["parent"] != parent["id"]:
                self.at(part["parent"])["children"].remove(part["id"])
                part["parent"] = parent["id"]
            for name, value in props.items():
                if name in ("layout", "constraints", "child_layout"):
                    part.setdefault(name, {}).update(deepcopy(value))
                elif name not in ("fills", "bound") and part.get(name) != value:
                    part[name] = deepcopy(value)
            if "fills" in props:
                apply_paint(part, props)
            result[key] = part
            desired.setdefault(parent["id"], []).append(part["id"])

        retained = {part["id"] for part in result.values()}
        removed = previous - retained
        for number in removed:
            if any(child not in removed for child in self.at(number).get("children", [])):
                raise ValueError(f"{number}: removing the native progress layer would orphan other content")
        managed = previous | retained
        for number, children in desired.items():
            parent = self.at(number)
            sequence = iter(children)
            order = (next(sequence, None) if child in managed else child for child in parent["children"])
            parent["children"] = [child for child in order if child is not None] + list(sequence)
        meta.update(bankColumns=bank, capWidth=span(bank))
        self.retired.update(removed)
        if "description" in node and bank:
            node["description"] = re.sub(r"Live whole-dot fill through \d+ columns",
                                         f"Live whole-dot fill through {bank} columns", node["description"])
        return result

    def refresh(self, target=None):
        selected = [number for number in self.order
                    if target is None or self.family[number] == self.family[target]]
        banks = {}
        for number in selected:
            meta = self.grids[number]
            if meta["mode"] != "authored":
                root = self.family[number]
                banks[root] = max(banks.get(root, 0), meta["bankColumns"], columns(self.at(number)["width"]))
        for number in selected:
            self.space_label(number)
            node, meta = self.at(number), self.grids[number]
            parts = self.parts[number]
            if meta["mode"] == "authored":
                parts = self.authored(node, meta, parts)
            elif meta["mode"] in LIVE:
                parts = self.native_progress(node, meta, parts, banks[self.family[number]])
            else:
                parts = self.wrapped(node, meta, parts, banks[self.family[number]])
            source = self.parts.get(node.get("source"), {})
            for key, part in parts.items():
                if key in source:
                    part["source"] = source[key]["id"]
                elif node.get("source") is not None:
                    part.pop("source", None)
            self.parts[number] = parts
            if json.loads(node["plugin_data"][MARKER]) != meta:
                node["plugin_data"][MARKER] = json.dumps(meta, ensure_ascii=False, separators=(",", ":"))

        for node in self.nodes.values():
            if node["id"] in self.retired:
                continue
            refs = [node.get("source"), node.get("component")]
            refs.extend(action.get("dest") for event in node.get("interactions", [])
                        for action in event.get("actions", []))
            if any(ref in self.retired for ref in refs):
                raise ValueError(f'{node["id"]}: an external reference still uses a removed dot')
        for number in self.retired:
            self.nodes.pop(str(number))
        if self.next_id > self.document["next_id"]:
            self.document["next_id"] = self.next_id


def snapshot(filename):
    info = filename.stat()
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def save(source, archive, destination, current, updated, original, in_place):
    if in_place and current == updated:
        return
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".kozu-reflow-", delete=False) as file:
            temp = Path(file.name)
            if current == updated:
                archive.fp.seek(0)
                shutil.copyfileobj(archive.fp, file)
            else:
                with ZipFile(file, "w") as output:
                    output.comment = archive.comment
                    for member in archive.infolist():
                        entry = copy(member)
                        if member.filename == DOCUMENT:
                            output.writestr(entry, updated)
                        else:
                            with archive.open(member) as inp, output.open(entry, "w") as out:
                                shutil.copyfileobj(inp, out)
            file.flush()
            os.fsync(file.fileno())
        os.chmod(temp, stat.S_IMODE(source.stat().st_mode))
        if snapshot(source) != original:
            raise ValueError("input changed during reflow; reload it and retry")
        if in_place:
            os.replace(temp, destination)
        else:
            os.link(temp, destination)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    listing = subs.add_parser("list", help="list marked grids and their owner IDs")
    listing.add_argument("file", type=Path)
    for command, description in (
        ("refresh", "reflow all marked grids using their saved widths"),
        ("resize", "resize a track or its immediate owner, or set its percentage"),
    ):
        sub = subs.add_parser(command, help=description)
        sub.add_argument("file", type=Path)
        outputs = sub.add_mutually_exclusive_group(required=True)
        outputs.add_argument("-o", "--output", type=Path, help="write a new archive")
        outputs.add_argument("--in-place", action="store_true", help="replace the input atomically")
        if command == "resize":
            sub.add_argument("id", type=int, help="grid or owner ID from list")
            sub.add_argument("width", nargs="?", help="nonnegative width in FigCraft units")
            sub.add_argument("--percent", metavar="NUMBER")
    args = parser.parse_args()
    try:
        source = args.file
        original = snapshot(source)
        with ZipFile(source) as archive:
            if archive.namelist().count(DOCUMENT) != 1:
                raise ValueError("expected a single document.json in the FigCraft archive")
            document = json.loads(archive.read(DOCUMENT))
            grids = Grids(document)
            if args.command == "list":
                grids.list()
                return
            destination = source if args.in_place else args.output
            if args.in_place and source.is_symlink():
                raise ValueError("--in-place requires the real file path")
            if not args.in_place and (destination.exists() or destination.is_symlink()):
                raise ValueError(f"output already exists: {destination}")

            def serialize():
                return json.dumps(document, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()

            before = serialize()
            if args.command == "resize":
                if args.width is None and args.percent is None:
                    raise ValueError("resize requires a width, --percent, or both")
                grids.resize(args.id, width(args.width) if args.width is not None else None,
                             percent(args.percent) if args.percent is not None else None)
            else:
                grids.refresh()
            save(source, archive, destination, before, serialize(), original, args.in_place)
        print(f"Wrote {destination}")
    except (BadZipFile, KeyError, TypeError, ValueError, OverflowError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
