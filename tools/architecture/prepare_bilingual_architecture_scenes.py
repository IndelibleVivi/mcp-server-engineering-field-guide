#!/usr/bin/env python3
"""Create paired English and Chinese-leading editable architecture scenes.

The first run treats the original mixed-English Excalidraw geometry as the
English base. Later runs use the existing `.en.excalidraw` files as the base,
so the Chinese projection never becomes the source for another translation.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIGURES = ROOT / "docs" / "architecture"

BASES = [
    "architecture-master",
    "review-execution",
    "evaluation-loop",
]

VARIANTS = (
    "",
    ".landscape",
)

EDGE_LABEL_ALLOW = {
    "architecture-master": {"e00", "e03", "e14", "e15", "e25", "e29", "e33", "e34", "e37"},
    "review-execution": {"a03", "a04", "a05", "a08", "a09", "a10", "a11", "a12", "a13", "a14", "a15"},
    "evaluation-loop": {"e25", "r_observer", "r_scenario", "r_rubric", "r_run", "e30", "e33"},
}

EN_TEXT = {
    "architecture-master": {
        "head_r0": "R0  External normative authority\nnamed source owners",
        "n30-label": "N30 · Target preflight\nrevision · transport · deployment\nowner · evidence ceiling",
    },
    "review-execution": {
        "review_title": "V-REVIEW · How one review crosses ownership and enforcement boundaries",
        "review_sub": "revision · transport · deployment · owner · evidence ceiling determine applicability, reference selection, and claim ceiling",
        "control_note-label": "CONTROL FAMILIES · protocol invariant · implementation invariant · deployment policy · hardening choice\nalways declare owner + applicability",
    },
    "evaluation-loop": {
        "eval_title": "V-EVALUATION · How evaluation detects and repairs its own measurement defects",
    },
}

ZH_TEXT = {
    "architecture-master": {
        "master_subtitle": "Authority → Artifact → Execution → Evidence → Evaluation → Release · public snapshot dcb2c61a",
        "head_r0": "R0  外部 normative authority\nnamed source owners",
        "head_r1": "R1  Public reference repository\n项目 authored truth",
        "head_r2": "R2  Executable skill\n被选择的工作流",
        "head_r3": "R3  Target implementation + deployment\nruntime / effect canonical owners",
        "head_r4": "R4  Evaluation + adjudication\nsame-owner release evidence",
        "head_r5": "R5  Maintenance + release\npublic byte identity",
        "unknown_text": "明确保留的 UNKNOWN / NON-CLAIM\nU0 runtime model identity：unknown  ·  U1 independent assurance：未建立  ·  U2 no-skill A/B：未执行\nU3 stranger adoption/use：unknown  ·  U4 runtime / proxy / tunnel / browser / named-host：观察前保持 task-dependent",
        "n00-label": "N00 · MCP specifications\n2025-06-18 / 2025-11-25 / 2026-07-28\nOWN：protocol semantics",
        "n01-label": "N01 · JSON-RPC 2.0\nHTTP RFC 9110 / 9112\nOWN：message + transport semantics",
        "n02-label": "N02 · Named integration guidance\nassessment：2026-08-15\nDATED · 不是 live host check",
        "n10-label": "N10 · Field Guide stable core\nowner · partial order · state/effect · egress · verification",
        "n11-label": "N11 · Revision profiles\nMCP + JSON-RPC + HTTP + integration\nDATED interpretation，不替代 normative source",
        "n12-label": "N12 · Public case study\nintervention · reconciliation · tests · receipts · residuals",
        "n13-label": "N13 · VERSION-REGISTER\nS1 canonical selected release identities\nGuide 2.0.1 · Skill 0.1.0",
        "n14-label": "N14 · BILINGUAL-MANIFEST\n登记 Chinese / English pairs\nstructural pair ≠ independent parity",
        "n20-label": "N20 · SKILL controller\npreflight → work mode → profile → refs\n按比例停止 / non-trigger",
        "n21-label": "N21 · Bundled references\ncore · ownership · evidence · protocol\n只加载 selected material",
        "n22-label": "N22 · Templates + validators\nclaims · findings · threats · tests · receipts\nschema / link valid ≠ assurance",
        "n30-label": "N30 · Target preflight\nrevision · transport · deployment\nowner · evidence ceiling",
        "n31-label": "N31 · Transport envelopes\nstdio / HTTP / custom\nparse · frame · admit · deliver",
        "n32-label": "N32 · Shared capability core · S2\nnormalize → validate → authorize → execute → mutate → result\n所有 transport 共享一个 semantic path",
        "n33-label": "N33 · Deployment owners\nsource · runtime · proxy\ntunnel · host · operator",
        "n34-label": "N34 · MCP App projections\nmodel\ncomponent\noperator",
        "n35-label": "N35 · Observations + receipts\nsource → test → function → runtime → host → independent\nreceipt 只证明 observed boundary",
        "n40-label": "N40 · Scenario corpus\n1 个 discovery canary\n8 个 scored synthetic scenarios",
        "n41-label": "N41 · Installed runs\nbyte-identical skill 0.1.0\nrequested gpt-5.6-sol",
        "n42-label": "N42 · Trace observer\nprocess · turn · trace\nloading · oracle evidence",
        "n43-label": "N43 · Outputs + receipts\npublic projected finals\nprivate raw traces 不公开",
        "n44-label": "N44 · Frozen rubric + adjudication · S3\nrubric 1.1.0 · 仅 valid-completed 进入\nresults.json · 9/9 critical pass",
        "n45-label": "N45 · Evaluation repair boundary\nobserver defect → observer\nlanguage control → prompt/scenario\njudgment contract → versioned rubric\n随后 rerun · SKILL BYTES 保持固定",
        "n50-label": "N50 · Repository gates\n32 tests · syntax · version · mirrors\nbilingual · package · links · scan · corpus\nPASS ≠ deployed assurance",
        "n51-label": "N51 · Git commit / tag / release · S4\ndcb2c61a… · v2.0.1\nOWN：exact public bytes\n不是 stranger-use evidence",
        "n52-label": "N52 · Future revision intake\nnew spec / integration / field case / eval failure\nroute → profile / core / case / skill / corpus\nsync pair → gates → new release",
        "e00-label": "固定 MCP revision",
        "e03-label": "稳定方法",
        "e14-label": "normalized request",
        "e15-label": "state / effect evidence",
        "e19-label": "prompt + fixture",
        "e20-label": "固定的 installed skill",
        "e25-label": "路由 evaluator defect",
        "e29-label": "rerun · skill 不变",
        "e33-label": "gate exact bytes",
        "e34-label": "public baseline",
        "e37-label": "field residual",
    },
    "review-execution": {
        "review_title": "V-REVIEW · 一次 review 怎样穿过 ownership 与 enforcement boundaries",
        "review_sub": "revision · transport · deployment · owner · evidence ceiling 决定 applicability、reference selection 与 claim ceiling",
        "rv_authority_head": "R0 / R1 · named authority + project interpretation · S0",
        "rv_route_head": "R2 + preflight · controller 只选择这个 target 所需的 workflow 与 references",
        "rv_exec_head": "R3 · partially ordered execution · transport-specific admission → shared capability core → bounded evidence",
        "core_rule": "后置 control 不能倒流保护已经消耗的 resource / state / authority",
        "n00-label": "N00 · MCP specs\n3 个 named revisions\nnormative protocol truth",
        "n01-label": "N01 · JSON-RPC / HTTP RFCs\nmessage + transport semantics\nHTTP 仅在 applicable 时进入",
        "n02-label": "N02 · integration guidance\ndated assessment\n不是 live host check",
        "n10-label": "N10 · Field Guide stable core\npartial order · ownership · state/effect · evidence discipline",
        "n11-label": "N11 · selected revision profiles\ndated interpretation + applicability\nprofile ≠ normative replacement",
        "n30-label": "N30 · TARGET FACTS\n\n01 revision\n02 transport\n03 deployment reachability\n04 capability / boundary owner\n05 evidence ceiling\n\n缺失 evidence 保持 unknown",
        "n20-label": "N20 · SKILL controller\n\nmode：design / audit / patch-review / spec-upgrade\n选择 profile + control family + refs\n按比例停止 / wording-only non-trigger",
        "n21-label": "N21 · Bundled references\n\ncore invariants\ndeployment ownership\nevidence discipline\nprotocol / HTTP / MCP Apps\nrevision mirrors",
        "n22-label": "N22 · Templates + validators\n\nclaim / finding / threat / test / receipt\n让 review 可检查\n\nschema validity ≠ review truth",
        "control_note-label": "CONTROL FAMILIES · protocol invariant · implementation invariant · deployment policy · hardening choice\n始终明确 owner + applicability",
        "n31-label": "N31 · Transport envelopes\n\nstdio · HTTP · custom\nparse / frame / admit / identify\nnormalize transport shape\ndeliver response\n\nHTTP controls 可能 N/A",
        "n32-label": "N32 · SHARED CAPABILITY CORE · S2",
        "gate0-label": "normalize\n输入",
        "gate1-label": "validate\nschema + semantics",
        "gate2-label": "authorize\ncapability",
        "gate3-label": "budget\nresource",
        "gate4-label": "execute\noperation",
        "gate5-label": "mutate state\n/ emit effect",
        "gate6-label": "result semantics\n+ error boundary",
        "n33-label": "N33 · Deployment owners\nsource / runtime / proxy / tunnel\nhost / operator\n每层只出自己的 receipt",
        "n34-label": "N34 · MCP App projections\nmodel / component / operator\nvisibility ≠ shared authority\nbrowser + host 另需 evidence",
        "n35-label": "N35 · OBSERVATIONS + RECEIPTS\n\nsource inspection → project tests → function reproduction → runtime → named host → independent\n\nclaim：Observed / Normative / Inference / Decision / Unknown\nprovenance：original-observation / reproduced / independently-reproduced",
        "decision_rail-label": "DECISION RAIL · applicable finding / verified absence / not applicable / runtime-unknown / host-unknown / independent-unverified   ·   U4 在对应 boundary 被观察前保持可见",
        "a03-label": "稳定方法",
        "a04-label": "selected profile",
        "a05-label": "五个 target facts",
        "a08-label": "transport applicability",
        "a09-label": "capability review",
        "a10-label": "deployment owners",
        "a11-label": "projection owners",
        "a12-label": "normalized request",
        "a13-label": "capability evidence",
        "a14-label": "deployment evidence",
        "a15-label": "projection evidence",
    },
    "evaluation-loop": {
        "eval_title": "V-EVALUATION · Evaluation 如何发现并修正自己的测量缺陷",
        "eval_sub": "scenario control → byte-identical installed execution → observer + projection → frozen rubric → repair routing → rerun → release",
        "ev_skill_head": "R2 · object under test\n固定 skill bytes",
        "ev_eval_head": "R4 · evaluation + adjudication\nsame-owner evidence production",
        "ev_release_head": "R5 · validation + release\nexact public bytes",
        "n20-label": "N20 · installed skill\nmcp-server-engineering 0.1.0\n\nrelease runs 前固定 byte identity\nworkflow + bundled refs\n\nEVALUATOR REPAIR 不得修改这里",
        "skill_lock-label": "RERUN 期间保持 LOCKED\n\nGuide 可以变成 2.0.1\nrubric 可以变成 1.1.0\nscenario revisions 可以改变\n\nskill 保持 0.1.0",
        "n40-label": "N40 · SCENARIO CORPUS\n\n1 个 positive discovery canary\n8 个 scored synthetic scenarios\nisolated prompts + fixtures\nscenario revision + language control",
        "n41-label": "N41 · INSTALLED RUNS\n\nprocess + thread / turn\nrequested model：gpt-5.6-sol\nruntime model identity：unknown\nsame-owner execution",
        "n42-label": "N42 · TRACE OBSERVER\n\nprocess exit · turn complete\ntrace completeness · final message\nskill material loading\noracle access evidence",
        "n43-label": "N43 · PUBLIC PROJECTION\n\ncomplete final answers\nschema-v2 same-owner receipts\nnormalize temporary paths\nprivate raw JSONL / traces 不公开",
        "n44-label": "N44 · FROZEN RUBRIC + ADJUDICATION · S3\n\n只有 valid-completed 进入 rubric\nrubric / scenario / run identity 绑定\ncritical items + residual boundaries\nresults.json owns public dispositions\n\nrelease：rubric 1.1.0 · 9/9 valid-completed",
        "n45-label": "N45 · EVALUATION REPAIR BOUNDARY",
        "defect_a-label": "OBSERVER DEFECT\n只认 resolved path\n漏掉 installed symlink spelling\n漏掉 relative ref reads",
        "defect_b-label": "SCENARIO / PROMPT DEFECT\nEnglish pair 未要求\nEnglish output\nambient language 污染 control",
        "defect_c-label": "RUBRIC / PROVENANCE REPAIR\n保留 excluded preflight run IDs + reasons\nversion 1.0.0 → 1.1.0\n不拿旧 output 重新评分",
        "rerun_bar-label": "RERUN 全部 affected release scenarios · 回到 N41 · byte-identical skill 0.1.0",
        "n50-label": "N50 · REPOSITORY GATES\n\n32 tests · syntax\nversion register · profile mirrors\nbilingual coverage · skill package\nlinks · public scan · corpus validation\n\nnamed gates only；不是 assurance",
        "n51-label": "N51 · PUBLIC RELEASE · S4\n\nGuide 2.0.1 · Skill 0.1.0\ncommit dcb2c61a… · tag v2.0.1\n9/9 same-owner installed dogfood\n\nowns bytes；不是 external adoption",
        "unknown_rail-label": "明确保留的 NON-CLAIMS\n\nU0 runtime model identity：unknown\nU1 independent assurance：未建立\nU2 no-skill A/B：未执行",
        "e25-label": "ambiguity / evaluator defect",
        "r_observer-label": "修 observer path recognition",
        "r_scenario-label": "更新 scenario / prompt",
        "r_rubric-label": "freeze 新 rubric",
        "r_run-label": "rerun · skill 不变",
        "e30-label": "results + report + corpus",
        "e33-label": "gate exact bytes",
    },
}

LANDSCAPE_EN_TEXT = {
    "review-execution": {
        "control_note-label": "CONTROL FAMILIES\n\nprotocol invariant\nimplementation invariant\ndeployment policy\nhardening choice\n\nalways name owner + applicability",
    },
}

LANDSCAPE_ZH_TEXT = {
    "review-execution": {
        "control_note-label": "CONTROL FAMILIES\n\nprotocol invariant\nimplementation invariant\ndeployment policy\nhardening choice\n\n始终明确 owner + applicability",
    },
}

LANDSCAPE_TEXT_GEOMETRY = {
    "architecture-master": {
        # Keep edge labels in the whitespace between node rows rather than
        # letting the recovered Excalidraw auto-placement cover node copy.
        "e03-label": (925, 410, 130, 24),
        "e15-label": (1625, 990, 210, 24),
    },
}

MASTER_MAINTENANCE_EDGES = {
    ("n00", "n52"): "e35",
    ("n02", "n52"): "e36",
    ("n35", "n52"): "e37",
    ("n52", "n10"): "e38",
    ("n52", "n11"): "e39",
    ("n52", "n14"): "e40",
    ("n52", "n40"): "e41",
}


def align_master_maintenance_edges(scene: dict) -> dict:
    """Align editable edge IDs with E35-E41 and add both revision inputs."""

    arrows = [element for element in scene["elements"] if element.get("type") == "arrow"]
    renames: dict[str, str] = {}
    pairs: set[tuple[str, str]] = set()
    for arrow in arrows:
        pair = (
            arrow.get("startBinding", {}).get("elementId"),
            arrow.get("endBinding", {}).get("elementId"),
        )
        pairs.add(pair)
        canonical = MASTER_MAINTENANCE_EDGES.get(pair)
        if canonical and arrow["id"] != canonical:
            renames[arrow["id"]] = canonical

    for element in scene["elements"]:
        if element.get("type") == "arrow" and element["id"] in renames:
            element["id"] = renames[element["id"]]
        if element.get("containerId") in renames:
            element["containerId"] = renames[element["containerId"]]
        if element.get("boundElements"):
            for bound in element["boundElements"]:
                if bound.get("id") in renames:
                    bound["id"] = renames[bound["id"]]

    by_id = {element["id"]: element for element in scene["elements"]}
    residual_label = by_id.get("e39-label")
    if residual_label:
        residual_label["id"] = "e37-label"
        residual_label["containerId"] = "e37"
        for bound in by_id["e37"].get("boundElements", []):
            if bound.get("id") == "e39-label":
                bound["id"] = "e37-label"

    by_id = {element["id"]: element for element in scene["elements"]}
    template = next(element for element in scene["elements"] if element.get("type") == "arrow")
    for index, ((start_id, end_id), edge_id) in enumerate(MASTER_MAINTENANCE_EDGES.items(), start=35):
        if (start_id, end_id) in pairs:
            continue
        arrow = copy.deepcopy(template)
        arrow.update(
            id=edge_id,
            x=0,
            y=0,
            width=1,
            height=1,
            points=[[0, 0], [1, 1]],
            startBinding={"elementId": start_id, "fixedPoint": None, "focus": 0, "gap": 4},
            endBinding={"elementId": end_id, "fixedPoint": None, "focus": 0, "gap": 4},
            boundElements=[],
            strokeColor="#2f9e44",
            strokeStyle="dashed",
            seed=410000000 + index,
            versionNonce=510000000 + index,
            index=f"z{index}",
        )
        scene["elements"].append(arrow)
        by_id[start_id].setdefault("boundElements", []).append({"id": edge_id, "type": "arrow"})
        by_id[end_id].setdefault("boundElements", []).append({"id": edge_id, "type": "arrow"})
    return scene


def route_landscape_master_revision_inputs(scene: dict) -> dict:
    """Give the two post-recovery revision inputs deliberate wide routes."""

    routes = {
        "e35": [(240, 270), (240, 238), (2920, 238), (2920, 980)],
        "e36": [(410, 745), (430, 745), (430, 250), (2960, 250), (2960, 980)],
    }
    for element in scene["elements"]:
        points = routes.get(element.get("id"))
        if not points:
            continue
        start_x, start_y = points[0]
        element["x"] = start_x
        element["y"] = start_y
        element["points"] = [
            [point_x - start_x, point_y - start_y]
            for point_x, point_y in points
        ]
        element["width"] = max(point[0] for point in points) - min(point[0] for point in points)
        element["height"] = max(point[1] for point in points) - min(point[1] for point in points)
    return scene


def update_text(element: dict, text: str) -> None:
    element["text"] = text
    if "originalText" in element:
        element["originalText"] = text


def normalize(scene: dict, base: str) -> dict:
    allowed = EDGE_LABEL_ALLOW[base]
    element_by_id = {element["id"]: element for element in scene["elements"]}
    removed: set[str] = set()
    for element in scene["elements"]:
        container_id = element.get("containerId")
        parent = element_by_id.get(container_id) if container_id else None
        if element.get("type") == "text" and parent and parent.get("type") == "arrow":
            if container_id not in allowed:
                removed.add(element["id"])
            else:
                element["strokeColor"] = parent.get("strokeColor", "#52616b")
                element["fontSize"] = max(16, int(element.get("fontSize", 14)))
                element["fontFamily"] = 3
                element["strokeWidth"] = 1
    scene["elements"] = [element for element in scene["elements"] if element["id"] not in removed]
    for element in scene["elements"]:
        if element.get("boundElements"):
            element["boundElements"] = [bound for bound in element["boundElements"] if bound.get("id") not in removed]
    return scene


def apply_map(scene: dict, replacements: dict[str, str]) -> dict:
    for element in scene["elements"]:
        if element["id"] in replacements:
            update_text(element, replacements[element["id"]])
    return scene


def apply_text_geometry(scene: dict, placements: dict[str, tuple[float, float, float, float]]) -> dict:
    for element in scene["elements"]:
        placement = placements.get(element.get("id"))
        if placement:
            element["x"], element["y"], element["width"], element["height"] = placement
    return scene


def write(path: Path, scene: dict) -> None:
    path.write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for base in BASES:
        for variant in VARIANTS:
            stem = f"{base}{variant}"
            zh_path = FIGURES / f"{stem}.zh-CN.excalidraw"
            en_path = FIGURES / f"{stem}.en.excalidraw"
            if not zh_path.exists() and not en_path.exists():
                continue
            if en_path.exists():
                english = json.loads(en_path.read_text(encoding="utf-8"))
            else:
                english = json.loads(zh_path.read_text(encoding="utf-8"))
            if base == "architecture-master":
                english = align_master_maintenance_edges(english)
                if variant == ".landscape":
                    english = route_landscape_master_revision_inputs(english)
            english = normalize(english, base)
            english = apply_map(english, EN_TEXT.get(base, {}))
            if variant == ".landscape":
                english = apply_map(english, LANDSCAPE_EN_TEXT.get(base, {}))
                english = apply_text_geometry(english, LANDSCAPE_TEXT_GEOMETRY.get(base, {}))
            write(en_path, english)

            chinese = copy.deepcopy(english)
            chinese = apply_map(chinese, ZH_TEXT[base])
            if variant == ".landscape":
                chinese = apply_map(chinese, LANDSCAPE_ZH_TEXT.get(base, {}))
                chinese = apply_text_geometry(chinese, LANDSCAPE_TEXT_GEOMETRY.get(base, {}))
            for element in chinese["elements"]:
                if element.get("type") == "text":
                    # Avoid Cascadia/mono CJK fallback blocks in the editable
                    # source. Publication SVG typography remains renderer-owned.
                    element["fontFamily"] = 2
            write(zh_path, chinese)
            print(f"{stem}: en + zh-CN")


if __name__ == "__main__":
    main()
