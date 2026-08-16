#!/usr/bin/env python3
"""Re-layout the bilingual architecture scenes for native A4 portrait reading.

The semantic node and edge identities remain unchanged. This script owns only
the publication geometry: horizontal authority planes become stacked bands,
forward evidence follows a vertical spine, and return paths use side gutters.
No portrait scene is produced by cropping or rotating a landscape source.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
FIGURES = ROOT / "docs" / "architecture"

SCENES = (
    "architecture-master.en.excalidraw",
    "architecture-master.zh-CN.excalidraw",
    "review-execution.en.excalidraw",
    "review-execution.zh-CN.excalidraw",
    "evaluation-loop.en.excalidraw",
    "evaluation-loop.zh-CN.excalidraw",
)

Rect = tuple[float, float, float, float]
Point = tuple[float, float]


MASTER_RECTS: dict[str, Rect] = {
    "zone_r0": (70, 130, 1300, 210),
    "zone_r1": (70, 360, 1300, 300),
    "zone_r2": (70, 680, 1300, 220),
    "zone_r3": (70, 920, 1300, 330),
    "zone_r4": (70, 1270, 1300, 360),
    "zone_r5": (70, 1650, 1300, 260),
    "unknown_rail": (70, 1930, 1300, 150),
    "n00": (95, 200, 390, 115),
    "n01": (525, 200, 390, 115),
    "n02": (955, 200, 390, 115),
    "n10": (95, 425, 390, 100),
    "n11": (525, 425, 390, 100),
    "n12": (955, 425, 390, 100),
    "n13": (250, 545, 440, 90),
    "n14": (750, 545, 440, 90),
    "n20": (95, 750, 390, 125),
    "n21": (525, 750, 390, 125),
    "n22": (955, 750, 390, 125),
    "n30": (95, 990, 390, 110),
    "n31": (525, 990, 390, 110),
    "n32": (955, 990, 390, 110),
    "n33": (95, 1120, 390, 105),
    "n34": (525, 1120, 390, 105),
    "n35": (955, 1120, 390, 105),
    "n40": (95, 1340, 390, 110),
    "n41": (525, 1340, 390, 110),
    "n42": (955, 1340, 390, 110),
    "n43": (95, 1475, 390, 125),
    "n44": (525, 1475, 390, 125),
    "n45": (955, 1475, 390, 125),
    "n50": (95, 1725, 390, 150),
    "n51": (525, 1725, 390, 150),
    "n52": (955, 1725, 390, 150),
}

MASTER_TEXT: dict[str, tuple[float, float, float, float, float, str]] = {
    "master_title": (70, 28, 1280, 42, 32, "left"),
    "master_subtitle": (70, 78, 1280, 28, 16, "left"),
    "head_r0": (92, 148, 1235, 30, 18, "left"),
    "head_r1": (92, 378, 1235, 30, 18, "left"),
    "head_r2": (92, 698, 1235, 30, 18, "left"),
    "head_r3": (92, 938, 1235, 30, 18, "left"),
    "head_r4": (92, 1288, 1235, 30, 18, "left"),
    "head_r5": (92, 1668, 1235, 30, 18, "left"),
    "unknown_text": (95, 1950, 1250, 110, 16, "center"),
}

REVIEW_RECTS: dict[str, Rect] = {
    "rv_authority": (70, 135, 1300, 380),
    "rv_route": (70, 540, 1300, 520),
    "rv_execution": (70, 1085, 1300, 820),
    "n00": (95, 205, 390, 120),
    "n01": (525, 205, 390, 120),
    "n02": (955, 205, 390, 120),
    "n10": (180, 350, 510, 130),
    "n11": (750, 350, 510, 130),
    "n30": (95, 615, 350, 330),
    "n20": (485, 615, 390, 330),
    "n21": (915, 615, 405, 145),
    "n22": (915, 785, 405, 160),
    "control_note": (95, 970, 1225, 65),
    "n31": (95, 1165, 335, 270),
    "n32": (465, 1165, 855, 350),
    "gate0": (500, 1250, 175, 90),
    "gate1": (700, 1250, 175, 90),
    "gate2": (900, 1250, 175, 90),
    "gate3": (1100, 1250, 175, 90),
    "gate4": (1100, 1375, 175, 90),
    "gate5": (900, 1375, 175, 90),
    "gate6": (700, 1375, 175, 90),
    "n33": (95, 1550, 320, 220),
    "n34": (445, 1550, 320, 220),
    "n35": (795, 1550, 525, 220),
    "decision_rail": (95, 1810, 1225, 70),
}

REVIEW_TEXT: dict[str, tuple[float, float, float, float, float, str]] = {
    "review_title": (70, 28, 1280, 42, 30, "left"),
    "review_sub": (70, 78, 1280, 30, 15, "left"),
    "rv_authority_head": (92, 155, 1235, 28, 18, "left"),
    "rv_route_head": (92, 560, 1235, 28, 18, "left"),
    "rv_exec_head": (92, 1105, 1235, 28, 18, "left"),
    "core_rule": (500, 1480, 785, 28, 15, "center"),
}

EVALUATION_RECTS: dict[str, Rect] = {
    "ev_skill_zone": (70, 135, 1300, 330),
    "ev_eval_zone": (70, 490, 1300, 1120),
    "ev_release_zone": (70, 1635, 1300, 450),
    "n20": (95, 215, 610, 210),
    "skill_lock": (735, 215, 585, 210),
    "n40": (95, 575, 570, 230),
    "n41": (735, 575, 585, 230),
    "n42": (95, 835, 570, 230),
    "n43": (735, 835, 585, 230),
    "n44": (180, 1095, 1080, 250),
    "n45": (95, 1375, 1225, 190),
    "defect_a": (125, 1430, 360, 92),
    "defect_b": (525, 1430, 360, 92),
    "defect_c": (925, 1430, 360, 92),
    "rerun_bar": (125, 1530, 1160, 28),
    "n50": (95, 1720, 560, 210),
    "n51": (690, 1720, 630, 210),
    "unknown_rail": (95, 1950, 1225, 110),
}

EVALUATION_TEXT: dict[str, tuple[float, float, float, float, float, str]] = {
    "eval_title": (70, 28, 1280, 42, 30, "left"),
    "eval_sub": (70, 78, 1280, 30, 15, "left"),
    "ev_skill_head": (92, 155, 1235, 28, 18, "left"),
    "ev_eval_head": (92, 510, 1235, 28, 18, "left"),
    "ev_release_head": (92, 1655, 1235, 28, 18, "left"),
}

ZONE_IDS = {
    "zone_r0", "zone_r1", "zone_r2", "zone_r3", "zone_r4", "zone_r5",
    "rv_authority", "rv_route", "rv_execution",
    "ev_skill_zone", "ev_eval_zone", "ev_release_zone",
}

RAIL_IDS = {"unknown_rail", "decision_rail", "rerun_bar", "control_note"}
FRAME_TITLE_IDS = {"n32-label", "n45-label"}

NODE_FONT_OVERRIDES = {
    "architecture-master": {"default": 20.5, "unknown_rail": 16},
    "review-execution": {
        "default": 17.5,
        "n00": 18.5,
        "n01": 18.5,
        "n02": 18.5,
        "n10": 18.5,
        "n11": 18.5,
        "gate0": 16.5,
        "gate1": 16.5,
        "gate2": 16.5,
        "gate3": 16.5,
        "gate4": 16.5,
        "gate5": 16.5,
        "gate6": 16.5,
        "control_note": 15.5,
        "decision_rail": 14.5,
    },
    "evaluation-loop": {
        "default": 18,
        "defect_a": 15.5,
        "defect_b": 15.5,
        "defect_c": 15.5,
        "rerun_bar": 13.5,
        "unknown_rail": 15,
    },
}


def em_width(value: str) -> float:
    total = 0.0
    for character in value:
        code = ord(character)
        if character.isspace():
            total += 0.32
        elif 0x2E80 <= code <= 0x9FFF or 0xF900 <= code <= 0xFAFF:
            total += 1.0
        elif character in "·→←↔≠—–/|":
            total += 0.72
        elif character in ".,:;()[]{}'`":
            total += 0.38
        elif character.isupper() or character.isdigit():
            total += 0.62
        else:
            total += 0.55
    return total


def tokens(value: str) -> list[str]:
    return re.findall(
        r"\s+|[\u2e80-\u9fff]|[A-Za-z0-9_.:+#/-]+|→|←|↔|≠|—|–|…|.",
        value,
    )


def wrap_line(value: str, maximum: float) -> list[str]:
    if not value:
        return [""]
    if em_width(value) <= maximum:
        return [value.strip()]
    lines: list[str] = []
    current = ""
    for token in tokens(value):
        candidate = current + token
        if current.strip() and em_width(candidate) > maximum:
            lines.append(current.strip())
            current = token.lstrip()
        else:
            current = candidate
    if current.strip() or not lines:
        lines.append(current.strip())
    return lines


def wrap_text(value: str, maximum: float) -> str:
    lines: list[str] = []
    for source_line in value.splitlines() or [""]:
        lines.extend(wrap_line(source_line, maximum))
    return "\n".join(lines)


def element_map(scene: dict) -> dict[str, dict]:
    return {element["id"]: element for element in scene["elements"]}


def place_unbound_text(
    element: dict,
    spec: tuple[float, float, float, float, float, str],
) -> None:
    x, y, width, height, font_size, align = spec
    element.update(
        x=x,
        y=y,
        width=width,
        height=height,
        fontSize=font_size,
        textAlign=align,
        verticalAlign="middle",
    )


def fit_bound_text(
    text: dict,
    rect: Rect,
    requested_font_size: float,
    *,
    top_title: bool = False,
) -> None:
    x, y, width, height = rect
    font_size = requested_font_size
    minimum = 12.5
    if top_title:
        value = text.get("originalText", text.get("text", "")).splitlines()[0]
        maximum = max(8.0, (width - 28) / font_size)
        wrapped = wrap_text(value, maximum)
        lines = wrapped.splitlines()
        text_height = len(lines) * font_size * 1.18
        text_y = y + 9
    else:
        source = text.get("originalText", text.get("text", ""))
        while True:
            maximum = max(8.0, (width - 28) / font_size)
            wrapped = wrap_text(source, maximum)
            lines = wrapped.splitlines() or [""]
            text_height = len(lines) * font_size * 1.18
            if text_height <= height - 16 or font_size <= minimum:
                break
            font_size -= 0.5
        text_y = y + max(8, (height - text_height) / 2)
    text.update(
        x=x + 14,
        y=text_y,
        width=width - 28,
        height=text_height,
        fontSize=font_size,
        lineHeight=1.18,
        text=wrapped,
        originalText=wrapped,
        textAlign="center",
        verticalAlign="middle",
        autoResize=True,
    )


def place_rectangles(
    scene: dict,
    rectangles: dict[str, Rect],
    base: str,
) -> None:
    by_id = element_map(scene)
    font_sizes = NODE_FONT_OVERRIDES[base]
    for identifier, rect in rectangles.items():
        element = by_id[identifier]
        x, y, width, height = rect
        element.update(x=x, y=y, width=width, height=height)
        if identifier in ZONE_IDS:
            continue
        labels = [
            candidate
            for candidate in scene["elements"]
            if candidate.get("containerId") == identifier and candidate.get("type") == "text"
        ]
        for label in labels:
            size = font_sizes.get(identifier, font_sizes["default"])
            fit_bound_text(
                label,
                rect,
                size,
                top_title=label["id"] in FRAME_TITLE_IDS,
            )


def anchor(rect: Rect, side: str) -> Point:
    x, y, width, height = rect
    if side == "top":
        return (x + width / 2, y - 4)
    if side == "bottom":
        return (x + width / 2, y + height + 4)
    if side == "left":
        return (x - 4, y + height / 2)
    if side == "right":
        return (x + width + 4, y + height / 2)
    raise ValueError(f"Unknown anchor side: {side}")


def auto_route(source: Rect, target: Rect) -> tuple[str, str, list[Point]]:
    sx, sy, sw, sh = source
    tx, ty, tw, th = target
    if ty >= sy + sh + 20:
        start_side, end_side = "bottom", "top"
        start = anchor(source, start_side)
        end = anchor(target, end_side)
        middle = (start[1] + end[1]) / 2
        via = [] if abs(start[0] - end[0]) < 4 else [(start[0], middle), (end[0], middle)]
    elif sy >= ty + th + 20:
        start_side, end_side = "top", "bottom"
        start = anchor(source, start_side)
        end = anchor(target, end_side)
        middle = (start[1] + end[1]) / 2
        via = [] if abs(start[0] - end[0]) < 4 else [(start[0], middle), (end[0], middle)]
    elif tx >= sx + sw:
        start_side, end_side = "right", "left"
        start = anchor(source, start_side)
        end = anchor(target, end_side)
        middle = (start[0] + end[0]) / 2
        via = [] if abs(start[1] - end[1]) < 4 else [(middle, start[1]), (middle, end[1])]
    else:
        start_side, end_side = "left", "right"
        start = anchor(source, start_side)
        end = anchor(target, end_side)
        middle = (start[0] + end[0]) / 2
        via = [] if abs(start[1] - end[1]) < 4 else [(middle, start[1]), (middle, end[1])]
    return start_side, end_side, via


def path_midpoint(points: list[Point]) -> Point:
    lengths = [math.dist(one, two) for one, two in zip(points, points[1:])]
    half = sum(lengths) / 2
    walked = 0.0
    for index, length in enumerate(lengths):
        if walked + length >= half:
            ratio = 0 if length == 0 else (half - walked) / length
            one, two = points[index], points[index + 1]
            return (one[0] + (two[0] - one[0]) * ratio, one[1] + (two[1] - one[1]) * ratio)
        walked += length
    return points[-1]


def set_arrow_path(
    arrow: dict,
    source: Rect,
    target: Rect,
    *,
    start_side: str | None = None,
    end_side: str | None = None,
    via: Iterable[Point] = (),
) -> list[Point]:
    if start_side is None or end_side is None:
        start_side, end_side, automatic_via = auto_route(source, target)
        if not tuple(via):
            via = automatic_via
    start = anchor(source, start_side)
    end = anchor(target, end_side)
    absolute = [start, *via, end]
    arrow["x"], arrow["y"] = start
    arrow["points"] = [[point[0] - start[0], point[1] - start[1]] for point in absolute]
    arrow["width"] = max(point[0] for point in absolute) - min(point[0] for point in absolute)
    arrow["height"] = max(point[1] for point in absolute) - min(point[1] for point in absolute)
    arrow["elbowed"] = False
    arrow["roundness"] = None
    return absolute


MASTER_ROUTES: dict[str, tuple[str, str, list[Point]]] = {
    "e05": ("top", "top", [(1150, 410), (290, 410)]),
    "e07": ("left", "left", [(42, 590), (42, 1800)]),
    "e16": ("bottom", "bottom", [(290, 1238), (1150, 1238)]),
    "e20": ("right", "right", [(1390, 812), (1390, 1395)]),
    "e26": ("right", "top", [(1392, 1538), (1392, 1325), (290, 1325)]),
    "e27": ("right", "right", [(1404, 1538), (1404, 1395)]),
    "e29": ("right", "top", [(1380, 1538), (1380, 1315), (720, 1315)]),
    "e31": ("left", "left", [(30, 590), (30, 1800)]),
    "e32": ("left", "left", [(54, 812), (54, 1800)]),
    "e35": ("left", "top", [(18, 257), (18, 1620), (1150, 1620)]),
    "e36": ("right", "top", [(1430, 257), (1430, 1630), (1150, 1630)]),
    "e38": ("right", "top", [(1416, 1800), (1416, 410), (290, 410)]),
    "e39": ("right", "top", [(1404, 1800), (1404, 400), (720, 400)]),
    "e40": ("right", "right", [(1392, 1800), (1392, 590)]),
    "e41": ("right", "top", [(1380, 1800), (1380, 1305), (290, 1305)]),
}

EVALUATION_ROUTES: dict[str, tuple[str, str, list[Point]]] = {
    "r_observer": ("left", "left", [(42, 1476), (42, 950)]),
    "r_scenario": ("left", "left", [(28, 1476), (28, 690)]),
    "r_rubric": ("top", "bottom", []),
    "r_run": ("right", "right", [(1402, 1544), (1402, 690)]),
    "e30": ("left", "top", [(48, 1220), (48, 1690), (375, 1690)]),
}

REVIEW_ROUTES: dict[str, tuple[str, str, list[Point]]] = {
    "a10": ("left", "top", [(42, 780), (42, 1525), (255, 1525)]),
    "a11": ("right", "top", [(1392, 780), (1392, 1525), (605, 1525)]),
    "a14": ("bottom", "bottom", [(255, 1790), (1058, 1790)]),
    "a16": ("right", "top", [(1404, 865), (1404, 1525), (1058, 1525)]),
}

EDGE_LABEL_POSITIONS: dict[str, dict[str, tuple[float, float, float]]] = {
    "architecture-master": {
        "e00-label": (315, 335, 185),
        "e03-label": (200, 650, 145),
        "e14-label": (760, 1078, 170),
        "e15-label": (1055, 1100, 220),
        "e25-label": (870, 1515, 190),
        "e29-label": (1135, 1292, 190),
        "e33-label": (445, 1788, 170),
        "e34-label": (875, 1788, 165),
        "e37-label": (1125, 1625, 170),
    },
    "review-execution": {
        "a03-label": (335, 500, 155),
        "a04-label": (1000, 500, 175),
        "a05-label": (345, 670, 180),
        "a08-label": (105, 1045, 215),
        "a09-label": (570, 1045, 190),
        "a10-label": (78, 1440, 190),
        "a11-label": (1090, 1510, 190),
        "a12-label": (350, 1270, 190),
        "a13-label": (805, 1510, 190),
        "a14-label": (275, 1774, 200),
        "a15-label": (610, 1660, 195),
    },
    "evaluation-loop": {
        "e25-label": (565, 1348, 220),
        "r_observer-label": (75, 1125, 190),
        "r_scenario-label": (75, 810, 190),
        "r_rubric-label": (955, 1348, 180),
        "r_run-label": (1135, 810, 180),
        "e30-label": (78, 1605, 205),
        "e33-label": (595, 1805, 190),
    },
}


def place_arrows(
    scene: dict,
    rectangles: dict[str, Rect],
    routes: dict[str, tuple[str, str, list[Point]]],
    base: str,
) -> None:
    by_id = element_map(scene)
    for arrow in [item for item in scene["elements"] if item.get("type") == "arrow"]:
        start_id = arrow.get("startBinding", {}).get("elementId")
        end_id = arrow.get("endBinding", {}).get("elementId")
        if start_id not in rectangles or end_id not in rectangles:
            raise ValueError(f"{arrow['id']} has unresolved portrait binding: {start_id} -> {end_id}")
        custom = routes.get(arrow["id"])
        if custom:
            start_side, end_side, via = custom
            points = set_arrow_path(
                arrow,
                rectangles[start_id],
                rectangles[end_id],
                start_side=start_side,
                end_side=end_side,
                via=via,
            )
        else:
            points = set_arrow_path(arrow, rectangles[start_id], rectangles[end_id])
        labels = [
            by_id[bound["id"]]
            for bound in arrow.get("boundElements", [])
            if bound.get("type") == "text" and bound.get("id") in by_id
        ]
        for label in labels:
            middle_x, middle_y = path_midpoint(points)
            label_width = max(90, min(255, em_width(label.get("text", "")) * 9.5 + 22))
            label.update(
                x=middle_x - label_width / 2,
                y=middle_y - 13,
                width=label_width,
                height=24,
                fontSize=14,
                lineHeight=1.15,
                textAlign="center",
                verticalAlign="middle",
            )
            position = EDGE_LABEL_POSITIONS[base].get(label["id"])
            if position:
                label_x, label_y, label_width = position
                label.update(x=label_x, y=label_y, width=label_width, height=24)


def layout_scene(path: Path) -> None:
    scene = json.loads(path.read_text(encoding="utf-8"))
    if path.name.startswith("architecture-master"):
        base = "architecture-master"
        rectangles = MASTER_RECTS
        unbound = MASTER_TEXT
        routes = MASTER_ROUTES
    elif path.name.startswith("review-execution"):
        base = "review-execution"
        rectangles = REVIEW_RECTS
        unbound = REVIEW_TEXT
        routes = REVIEW_ROUTES
    else:
        base = "evaluation-loop"
        rectangles = EVALUATION_RECTS
        unbound = EVALUATION_TEXT
        routes = EVALUATION_ROUTES

    place_rectangles(scene, rectangles, base)
    by_id = element_map(scene)
    for identifier, spec in unbound.items():
        place_unbound_text(by_id[identifier], spec)
    place_arrows(scene, rectangles, routes, base)

    # Keep editable Chinese scenes readable in Excalidraw itself. Cascadia's
    # CJK fallback can show missing-glyph blocks; the publication SVG keeps the
    # serif-led house typography independently.
    chinese = ".zh-CN." in path.name
    for element in scene["elements"]:
        if element.get("type") == "text":
            element["fontFamily"] = 2 if chinese else 3

    scene["appState"]["viewBackgroundColor"] = "#ffffff"
    path.write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{path.name}: native portrait geometry")


def main() -> None:
    for filename in SCENES:
        layout_scene(FIGURES / filename)


if __name__ == "__main__":
    main()
