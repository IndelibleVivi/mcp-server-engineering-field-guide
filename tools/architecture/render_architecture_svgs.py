#!/usr/bin/env python3
"""Render house-styled publication SVGs from the editable Excalidraw scenes.

The Excalidraw files own geometry and connector bindings. This renderer owns
the fixed publication typography and vector treatment used by the attachment.
It intentionally does not use Excalidraw's built-in sans export.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIGURES = ROOT / "docs" / "architecture"

SCENES = {
    "architecture-master.zh-CN.excalidraw": "architecture-master.zh-CN.svg",
    "architecture-master.en.excalidraw": "architecture-master.en.svg",
    "architecture-master.landscape.zh-CN.excalidraw": "architecture-master.landscape.zh-CN.svg",
    "architecture-master.landscape.en.excalidraw": "architecture-master.landscape.en.svg",
    "review-execution.zh-CN.excalidraw": "review-execution.zh-CN.svg",
    "review-execution.en.excalidraw": "review-execution.en.svg",
    "review-execution.landscape.zh-CN.excalidraw": "review-execution.landscape.zh-CN.svg",
    "review-execution.landscape.en.excalidraw": "review-execution.landscape.en.svg",
    "evaluation-loop.zh-CN.excalidraw": "evaluation-loop.zh-CN.svg",
    "evaluation-loop.en.excalidraw": "evaluation-loop.en.svg",
    "evaluation-loop.landscape.zh-CN.excalidraw": "evaluation-loop.landscape.zh-CN.svg",
    "evaluation-loop.landscape.en.excalidraw": "evaluation-loop.landscape.en.svg",
}

EDGE_LABEL_ALLOW = {
    "architecture-master.zh-CN.excalidraw": {
        "e00", "e03", "e14", "e15", "e25", "e29",
        "e33", "e34", "e37",
    },
    "review-execution.zh-CN.excalidraw": {
        "a03", "a04", "a05", "a08", "a09", "a10", "a11", "a12",
        "a13", "a14", "a15",
    },
    "evaluation-loop.zh-CN.excalidraw": {
        "e25", "r_observer", "r_scenario", "r_rubric", "r_run", "e30", "e33",
    },
}

ZONE_IDS = {
    "zone_r0", "zone_r1", "zone_r2", "zone_r3", "zone_r4", "zone_r5",
    "rv_authority", "rv_route", "rv_execution",
    "ev_skill_zone", "ev_eval_zone", "ev_release_zone",
}

SERIF = "'Iowan Old Style','Songti SC','STSong','Times New Roman',serif"
MONO = "'Menlo','SFMono-Regular','Cascadia Code',monospace"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def opacity(element: dict) -> float:
    return max(0.0, min(1.0, float(element.get("opacity", 100)) / 100.0))


def dash(element: dict) -> str:
    style = element.get("strokeStyle", "solid")
    if style == "dashed":
        return "18 12"
    if style == "dotted":
        return "4 10"
    return ""


def box(element: dict) -> tuple[float, float, float, float]:
    return (
        float(element.get("x", 0)),
        float(element.get("y", 0)),
        float(element.get("width", 0)),
        float(element.get("height", 0)),
    )


def render_rect(element: dict) -> str:
    x, y, width, height = box(element)
    fill = element.get("backgroundColor", "#ffffff")
    stroke = element.get("strokeColor", "#1e1e1e")
    stroke_width = max(1.2, float(element.get("strokeWidth", 1)) * 1.15)
    fill_opacity = 0.44 if element["id"] in ZONE_IDS else 0.96
    radius = 16 if element["id"] not in ZONE_IDS else 24
    return (
        f'<rect id="{esc(element["id"])}" x="{x:g}" y="{y:g}" '
        f'width="{width:g}" height="{height:g}" rx="{radius}" '
        f'fill="{esc(fill)}" fill-opacity="{fill_opacity:g}" '
        f'stroke="{esc(stroke)}" stroke-width="{stroke_width:g}" '
        f'stroke-dasharray="{dash(element)}" opacity="{opacity(element):g}"/>'
    )


def render_arrow(element: dict) -> str:
    x = float(element.get("x", 0))
    y = float(element.get("y", 0))
    points = element.get("points") or [[0, 0], [float(element.get("width", 0)), float(element.get("height", 0))]]
    coords = " ".join(f"{x + float(px):g},{y + float(py):g}" for px, py in points)
    marker = ' marker-end="url(#arrowhead)"' if element.get("endArrowhead") else ""
    return (
        f'<polyline id="{esc(element["id"])}" points="{coords}" fill="none" '
        f'stroke="{esc(element.get("strokeColor", "#52616b"))}" '
        f'stroke-width="{max(2.0, float(element.get("strokeWidth", 1)) * 1.25):g}" '
        f'stroke-dasharray="{dash(element)}" stroke-linecap="round" '
        f'stroke-linejoin="round" opacity="{opacity(element):g}"{marker}/>'
    )


def is_title(element: dict) -> bool:
    return element["id"].endswith("_title") or element["id"] in {"master_title", "review_title", "eval_title"}


def is_subtitle(element: dict) -> bool:
    return element["id"] in {"master_subtitle", "review_sub", "eval_sub"}


def is_coordinate_line(line: str, line_index: int, container_id: str | None) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if line_index == 0 and container_id:
        return True
    prefixes = (
        "R0", "R1", "R2", "R3", "R4", "R5", "N00", "N01", "N02",
        "N10", "N11", "N12", "N13", "N14", "N20", "N21", "N22",
        "N30", "N31", "N32", "N33", "N34", "N35", "N40", "N41",
        "N42", "N43", "N44", "N45", "N50", "N51", "N52", "U0",
        "U1", "U2", "U3", "U4", "S0", "S1", "S2", "S3", "S4",
        "CONTROL FAMILIES", "LOCKED DURING RERUN", "DECLARED",
        "DECISION RAIL", "RERUN ALL", "OBSERVER DEFECT", "SCENARIO / PROMPT",
        "RUBRIC / PROVENANCE",
    )
    return stripped.startswith(prefixes)


def render_text(element: dict, parent_by_id: dict[str, dict]) -> str:
    x, y, width, height = box(element)
    raw = element.get("text", "")
    lines = raw.splitlines() or [""]
    size = float(element.get("fontSize", 18))
    if element.get("containerId"):
        # Excalidraw computes bound text boxes against its bundled mono/sans
        # metrics. The publication Song/Iowan pair is wider and has a taller
        # Chinese em box, so preserve the box and reduce only bound copy.
        size *= 0.88
    line_height = float(element.get("lineHeight", 1.25)) * size
    color = element.get("strokeColor", "#24333a")
    container_id = element.get("containerId")
    text_align = element.get("textAlign", "left")
    if text_align == "center" or container_id:
        anchor = "middle"
        tx = x + width / 2
    elif text_align == "right":
        anchor = "end"
        tx = x + width
    else:
        anchor = "start"
        tx = x

    if is_title(element):
        family = SERIF
        weight = 500
        letter_spacing = "0.2"
    elif is_subtitle(element):
        family = MONO
        weight = 400
        letter_spacing = "0.1"
    else:
        family = SERIF
        weight = 400
        letter_spacing = "0"

    # Excalidraw already computed a vertically centered text box. Preserve its
    # geometry while giving the first line of a bound node a coordinate voice.
    if container_id and len(lines) == 1:
        parent = parent_by_id.get(container_id)
        if parent and float(parent.get("height", 0)) >= 180:
            first_baseline = float(parent["y"]) + size * 1.75
        else:
            first_baseline = y + size * 0.92
    else:
        first_baseline = y + size * 0.92
    spans: list[str] = []
    for index, line in enumerate(lines):
        line_family = MONO if is_coordinate_line(line, index, container_id) else family
        line_weight = 600 if index == 0 and container_id else weight
        line_size = size * 1.06 if index == 0 and container_id else size
        spans.append(
            f'<tspan x="{tx:g}" dy="{0 if index == 0 else line_height:g}" '
            f'font-family="{line_family}" font-size="{line_size:g}" '
            f'font-weight="{line_weight}">{esc(line) or "&#160;"}</tspan>'
        )
    return (
        f'<text id="{esc(element["id"])}" x="{tx:g}" y="{first_baseline:g}" '
        f'text-anchor="{anchor}" fill="{esc(color)}" font-family="{family}" '
        f'font-size="{size:g}" font-weight="{weight}" letter-spacing="{letter_spacing}" '
        f'opacity="{opacity(element):g}">{"".join(spans)}</text>'
    )


def render_edge_label(element: dict, parent_by_id: dict[str, dict]) -> str:
    x, y, width, height = box(element)
    size = max(15.5, float(element.get("fontSize", 14)))
    cx = x + width / 2
    baseline = y + size * 0.95
    parent = parent_by_id.get(element.get("containerId", ""), {})
    color = parent.get("strokeColor", element.get("strokeColor", "#52616b"))
    family = SERIF if re.search(r"[\u2e80-\u9fff]", element.get("text", "")) else MONO
    return (
        f'<g class="edge-label"><rect x="{x - 6:g}" y="{y - 3:g}" '
        f'width="{width + 12:g}" height="{height + 6:g}" rx="6" '
        f'fill="#ffffff" fill-opacity="0.86"/>'
        f'<text x="{cx:g}" y="{baseline:g}" text-anchor="middle" '
        f'fill="{esc(color)}" font-family="{family}" font-size="{size:g}" '
        f'font-weight="500">{esc(element.get("text", ""))}</text></g>'
    )


def element_bounds(element: dict) -> tuple[float, float, float, float]:
    if element.get("type") == "arrow":
        x = float(element.get("x", 0))
        y = float(element.get("y", 0))
        points = element.get("points") or [[0, 0]]
        absolute = [(x + float(px), y + float(py)) for px, py in points]
        return (
            min(point[0] for point in absolute),
            min(point[1] for point in absolute),
            max(point[0] for point in absolute),
            max(point[1] for point in absolute),
        )
    x, y, width, height = box(element)
    return (x, y, x + width, y + height)


def render_scene(source: Path, destination: Path) -> None:
    scene = json.loads(source.read_text(encoding="utf-8"))
    elements = [element for element in scene["elements"] if not element.get("isDeleted")]
    parent_by_id = {element["id"]: element for element in elements}
    bounds = [element_bounds(element) for element in elements]
    min_x = min(value[0] for value in bounds)
    min_y = min(value[1] for value in bounds)
    max_x = max(value[2] for value in bounds)
    max_y = max(value[3] for value in bounds)
    pad = 34
    view_x = min_x - pad
    view_y = min_y - pad
    view_w = max_x - min_x + pad * 2
    view_h = max_y - min_y + pad * 2

    zones = [element for element in elements if element["type"] == "rectangle" and element["id"] in ZONE_IDS]
    arrows = [element for element in elements if element["type"] == "arrow"]
    nodes = [element for element in elements if element["type"] == "rectangle" and element["id"] not in ZONE_IDS]
    texts = [
        element for element in elements
        if element["type"] == "text"
        and not (
            element.get("containerId")
            and parent_by_id.get(element["containerId"], {}).get("type") == "arrow"
        )
    ]
    label_key = source.name.replace(".landscape", "").replace(".en.excalidraw", ".zh-CN.excalidraw")
    allowed_edge_ids = EDGE_LABEL_ALLOW[label_key]
    edge_labels = [
        element for element in elements
        if element["type"] == "text"
        and element.get("containerId") in allowed_edge_ids
    ]

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_x:g} {view_y:g} {view_w:g} {view_h:g}" '
        'width="100%" height="100%" preserveAspectRatio="xMidYMid meet" role="img">',
        '<defs>',
        '<marker id="arrowhead" markerWidth="10" markerHeight="10" refX="8.5" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="context-stroke"/></marker>',
        '<filter id="node-shadow" x="-15%" y="-15%" width="130%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#17324d" flood-opacity="0.08"/></filter>',
        '</defs>',
        f'<rect x="{view_x:g}" y="{view_y:g}" width="{view_w:g}" height="{view_h:g}" fill="#ffffff"/>',
        '<g id="regions">',
        *(render_rect(element) for element in zones),
        '</g>',
        '<g id="edges">',
        *(render_arrow(element) for element in arrows),
        '</g>',
        '<g id="nodes" filter="url(#node-shadow)">',
        *(render_rect(element) for element in nodes),
        '</g>',
        '<g id="labels">',
        *(render_text(element, parent_by_id) for element in texts),
        '</g>',
        '<g id="edge-labels">',
        *(render_edge_label(element, parent_by_id) for element in edge_labels),
        '</g>',
        '</svg>',
    ]
    destination.write_text("\n".join(body) + "\n", encoding="utf-8")


def main() -> None:
    for source_name, output_name in SCENES.items():
        render_scene(FIGURES / source_name, FIGURES / output_name)
        print(output_name)


if __name__ == "__main__":
    main()
