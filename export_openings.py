#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Export de zones d'ouverture depuis un .kicad_pcb + preview STEP 2D.

Fonctionnalités:
- Lit un .kicad_pcb KiCad (S-expression)
- Extrait les footprints (ref/value/footprint/x/y/rot/layer)
- Exporte un DXF des ouvertures (et optionnellement Edge.Cuts)
- Charge un STEP du PCB (si disponible), projette en XY et superpose:
  - contours des zones générées
  - centres des composants
"""

from __future__ import annotations

import glob
import math
import os
import re
import tempfile
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple


# =========================
# PARAMETRES UTILISATEUR
# =========================
#KICAD_PCB_FILE = "USBC_Diode_Emitter_NOFLEX_V2.kicad_pcb"
#STEP_PCB_FILE: Optional[str] = "USBC_Diode_Emitter.step"
KICAD_PCB_FILE = "USBC_Diode_Emitter_NOFLEX_V2.kicad_pcb"
STEP_PCB_FILE: Optional[str] = "USBC_Diode_Emitter.step"
BOTTOM_LAYER = False

GROUP_BY_PACKAGE = True

OUT_DXF_FILE = "placement_mask.dxf"
EXPORT_DXF_OPENINGS = True
EXPORT_DXF_OPENINGS_ALERT = True
EXPORT_DXF_DISTANCE_MARKERS = True
EXPORT_DXF_DISTANCE_TEXT = True
INCLUDE_EDGE_CUTS = True
EXPORT_STEP_CONTOURS_TO_DXF = False
STEP_CONTOURS_DXF_LAYER = "STEP_COMPONENTS"
DXF_OPENINGS_COLOR = 7
DXF_OPENINGS_ALERT_COLOR = 1
DXF_OPENING_DISTANCE_MARKERS_COLOR = 1
DXF_OPENING_DISTANCE_TEXT_COLOR = 1
DXF_EDGE_CUTS_COLOR = 7
DXF_STEP_CONTOURS_COLOR = 8

# STEP preview
ENABLE_STEP_PREVIEW = True
PREVIEW_IMAGE_FILE = "placement_overlay.png"
SHOW_PREVIEW_WINDOW = True
PREVIEW_DPI = 180
PREVIEW_ZOOM = 1.2
PREVIEW_WINDOW_SCALE = 0.5
PREVIEW_WINDOW_MIN_W_IN = 1.0
PREVIEW_WINDOW_MIN_H_IN = 1.0
PREVIEW_WINDOW_MAX_W_IN = 5.0
PREVIEW_WINDOW_MAX_H_IN = 5.0
STEP_ALIGN_SCALE: Optional[float] = None
STEP_ALIGN_ROT_DEG: Optional[int] = None   # ex: 0/90/180/270
STEP_ALIGN_FLIP_Y: Optional[bool] = False  # on garde le STEP tel quel; miroir applique cote placement/DXF
STEP_ALIGN_OFFSET_X_MM = 0.0
STEP_ALIGN_OFFSET_Y_MM = 0.0

# Liste des boitiers a exporter (package_key). Vide => tout boitier connu.
EXPORT_PACKAGES: List[str] = [
    #"R_0603_1608Metric",
    #"C_0603_1608Metric",
    #"RES_0603",
    #"CAP_0603",
    #"CONN_B3B-ZR-SM4-TF_JST",
    #"MICROFJ-60035-TSV",

]

# Option: filtrer par layer KiCad
EXPORT_LAYERS = None  # ex: {"F.Cu"} ou {"B.Cu"}

# Option de geometrie
USE_ROUNDED_CORNERS = True
FLIP_Y_DXF = True
CHECK_OPENING_OVERLAP = True
MIN_OPENING_DISTANCE_MM: Optional[float] = 0.30
OPENING_CHECK_ARC_SEGMENTS = 8
OPENINGS_ALERT_LAYER = "OPENINGS_ALERT"
OPENING_DISTANCE_MARKERS_LAYER = "OPENINGS_DISTANCE_WARN"
OPENING_DISTANCE_MARKER_RADIUS_MM = 0.6
OPENING_DISTANCE_TEXT_LAYER = "OPENINGS_DISTANCE_TEXT"
OPENING_DISTANCE_TEXT_HEIGHT_MM = 0.8
OPENING_DISTANCE_TEXT_OFFSET_MM = 0.9
PREVIEW_BACKGROUND_COLOR = "#ffffff"
PREVIEW_STEP_FILL_COLOR = "#b9bfc8"
PREVIEW_STEP_EDGE_COLOR = "#7d8691"
PREVIEW_STEP_EDGE_WIDTH = 0.6
PREVIEW_STEP_ALPHA = 0.35
PREVIEW_STEP_POINT_COLOR = "#9aa0a6"
PREVIEW_STEP_POINT_SIZE = 1.2
PREVIEW_STEP_POINT_ALPHA = 0.35

PREVIEW_OPENING_COLOR = "#15c700"
PREVIEW_OPENING_LINE_WIDTH = 0.6
PREVIEW_OPENING_ALPHA = 0.95

SVG_ALERT_STROKE = "#ff2d20"
PREVIEW_ALERT_LINE_WIDTH = 1.8
PREVIEW_ALERT_ALPHA = 0.98
SVG_WARN_FILL = "#ff2d20"
PREVIEW_WARN_ALPHA = 0.96
SVG_WARN_TEXT = "#b00000"
PREVIEW_WARN_TEXT_SIZE = 8
PREVIEW_WARN_TEXT_WEIGHT = "bold"
PREVIEW_COMPONENT_CENTER_COLOR = "#1f77b4"
PREVIEW_COMPONENT_CENTER_SIZE = 10
PREVIEW_COMPONENT_CENTER_ALPHA = 0.65
COMPONENT_REF_TEXT_COLOR = "#174a7a"
COMPONENT_REF_TEXT_OFFSET_MM = 0.7
COMPONENT_REF_TEXT_SIZE = 7
COMPONENT_REF_TEXT_ALPHA = 0.9
PREVIEW_SAVE_PADDING_IN = 0.05

# Surcharges fines par reference composant.
# Exemple:
# REFERENCE_OFFSETS = {
#     "J5": {"offset_y": 0.3},
#     "SW1": {"offset_x": -1.2, "offset_y": 0.0},
# }
REFERENCE_OFFSETS: Dict[str, Dict[str, float]] = {}


PACKAGE_DIMENSIONS: Dict[str, Dict[str, float]] = {
    "R_0603_1608Metric": {"L": 2.8, "W": 1.2, "R": 0.0},
    "RES_0603": {"L": 2.8, "W": 1.2, "R": 0.0},
    "C_0603_1608Metric": {"L": 2.8, "W": 1.2, "R": 0.0},
    "CAP_0603": {"L": 2.8, "W": 1.2, "R": 0.0},
    "LED_0603_1608Metric": {"L": 2.8, "W": 1.2, "R": 0.0},
    "LXZ1": {"L": 1.6, "W": 2.5, "R": 0.0},
    "SOT26-420_DIO": {"L": 3.4, "W": 3.4, "R": 0.0},  
    "TL2233": {"L": 8.7, "W": 6.3, "R": 0.0, "offset_x" : 3.3, "offset_y" : 2},
    #"R_0402_1005Metric": {"L": 1.3, "W": 0.75, "R": 0.0},
    #"C_0402_1005Metric": {"L": 1.3, "W": 0.75, "R": 0.0},
    "CONN_B3B-ZR-SM4-TF_JST": {"L": 7.8, "W": 5.6, "R": 0.0,"offset_y" : -0.25},
    "CONN_BM03B-SRSS-TBLFSN_JST": {"L": 5.3, "W": 3.9, "R": 0.0,"offset_y": -0.35},
    "USB4125_GCT": {"L": 9.5, "W": 7.5, "R": 0.0},
    "MICROFJ-60035-TSV": {"L": 6.3, "W": 6.3, "R": 0.0},
    "QFN20_4x4MC_MCH": {"L": 4.6, "W": 4.6, "R": 0.0},
}


_BULGE_90 = math.tan(math.radians(90.0) / 4.0)  # ~0.41421356
_DXF_MIRROR_X_CENTER: Optional[float] = None


def _fy(y: float) -> float:
    return -y if FLIP_Y_DXF else y


def _fx(x: float) -> float:
    if not BOTTOM_LAYER or _DXF_MIRROR_X_CENTER is None:
        return x
    return 2.0 * _DXF_MIRROR_X_CENTER - x


# =========================
# STRUCTURE DONNEES
# =========================
@dataclass
class Component:
    ref: str
    value: str
    footprint: str
    x: float
    y: float
    rot: float
    layer: Optional[str] = None

    @property
    def package_key(self) -> str:
        if ":" in self.footprint:
            return self.footprint.split(":", 1)[1]
        return self.footprint


# =========================
# S-EXPR PARSER
# =========================
def tokenize_sexpr(text: str) -> List[str]:
    tokens: List[str] = []
    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        if c.isspace():
            i += 1
            continue

        if c in ("(", ")"):
            tokens.append(c)
            i += 1
            continue

        if c == '"':
            i += 1
            buf: List[str] = []
            while i < n:
                if text[i] == "\\" and i + 1 < n:
                    buf.append(text[i + 1])
                    i += 2
                    continue
                if text[i] == '"':
                    break
                buf.append(text[i])
                i += 1
            tokens.append('"' + "".join(buf) + '"')
            if i < n and text[i] == '"':
                i += 1
            continue

        start = i
        while i < n and (not text[i].isspace()) and text[i] not in ("(", ")"):
            i += 1
        tokens.append(text[start:i])

    return tokens


def atom(tok: str) -> Any:
    if len(tok) >= 2 and tok[0] == '"' and tok[-1] == '"':
        return tok[1:-1]
    try:
        if "." in tok or "e" in tok.lower():
            return float(tok)
        return int(tok)
    except ValueError:
        return tok


def parse_tokens(tokens: List[str]) -> Any:
    stack: List[List[Any]] = []
    current: List[Any] = []

    for tok in tokens:
        if tok == "(":
            stack.append(current)
            current = []
        elif tok == ")":
            if not stack:
                raise ValueError("Parentheses non equilibrees (trop de ')').")
            completed = current
            current = stack.pop()
            current.append(completed)
        else:
            current.append(atom(tok))

    if stack:
        raise ValueError("Parentheses non equilibrees (il manque des ')').")

    return current[0] if len(current) == 1 else current


def parse_kicad_pcb(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return parse_tokens(tokenize_sexpr(text))


# =========================
# HELPERS EXTRACTION
# =========================
def find_lists(root: Any, head: str) -> Iterable[List[Any]]:
    if isinstance(root, list) and root:
        if root[0] == head:
            yield root
        for item in root:
            yield from find_lists(item, head)


def get_first(lst: List[Any], head: str) -> Optional[List[Any]]:
    for item in lst:
        if isinstance(item, list) and item and item[0] == head:
            return item
    return None


def read_at(fp_list: List[Any]) -> Tuple[float, float, float]:
    at = get_first(fp_list, "at")
    if not at or len(at) < 3:
        return float("nan"), float("nan"), 0.0
    x = float(at[1])
    y = float(at[2])
    rot = float(at[3]) if len(at) >= 4 and isinstance(at[3], (int, float)) else 0.0
    return x, y, rot


def read_layer(fp_list: List[Any]) -> Optional[str]:
    layer = get_first(fp_list, "layer")
    if layer and len(layer) >= 2 and isinstance(layer[1], str):
        return layer[1]
    return None


def read_ref_value(fp_list: List[Any]) -> Tuple[str, str]:
    ref = ""
    val = ""

    for item in fp_list:
        if isinstance(item, list) and item and item[0] == "property" and len(item) >= 3:
            key = item[1]
            v = item[2]
            if key == "Reference" and isinstance(v, str):
                ref = v
            elif key == "Value" and isinstance(v, str):
                val = v

    if not ref or not val:
        for item in fp_list:
            if isinstance(item, list) and item and item[0] == "fp_text" and len(item) >= 3:
                kind = item[1]
                txt = item[2]
                if kind == "reference" and isinstance(txt, str) and not ref:
                    ref = txt
                elif kind == "value" and isinstance(txt, str) and not val:
                    val = txt

    return ref, val


def extract_components(root: Any) -> List[Component]:
    comps: List[Component] = []
    for fp_list in find_lists(root, "footprint"):
        footprint_name = ""
        if len(fp_list) >= 2 and isinstance(fp_list[1], str):
            footprint_name = fp_list[1]

        x, y, rot = read_at(fp_list)
        layer = read_layer(fp_list)
        ref, val = read_ref_value(fp_list)
        if not ref:
            continue

        comps.append(Component(ref=ref, value=val, footprint=footprint_name, x=x, y=y, rot=rot, layer=layer))

    comps.sort(key=lambda c: c.ref)
    return comps


def group_by_package(comps: List[Component]) -> Dict[str, List[Component]]:
    groups: Dict[str, List[Component]] = {}
    for c in comps:
        groups.setdefault(c.package_key, []).append(c)
    return groups


# =========================
# DXF WRITER (R12 minimal)
# =========================
def _dxf_pair(code: int, value) -> str:
    return f"{code}\n{value}\n"


def _dxf_header() -> str:
    return "0\nSECTION\n2\nHEADER\n0\nENDSEC\n"


def _dxf_tables(layers: Sequence[str] | Dict[str, int]) -> str:
    if isinstance(layers, dict):
        layer_items = list(layers.items())
    else:
        layer_items = [(name, 7) for name in layers]

    s = ""
    s += "0\nSECTION\n2\nTABLES\n"
    s += f"0\nTABLE\n2\nLAYER\n70\n{len(layer_items)}\n"
    for name, color in layer_items:
        s += "0\nLAYER\n"
        s += _dxf_pair(2, name)
        s += _dxf_pair(70, 0)
        s += _dxf_pair(62, color)
        s += _dxf_pair(6, "CONTINUOUS")
    s += "0\nENDTAB\n0\nENDSEC\n"
    return s


def _dxf_entities_start() -> str:
    return "0\nSECTION\n2\nENTITIES\n"


def _dxf_entities_end() -> str:
    return "0\nENDSEC\n0\nEOF\n"


def _dxf_line(x1, y1, x2, y2, layer: str) -> str:
    s = "0\nLINE\n"
    s += _dxf_pair(8, layer)
    s += _dxf_pair(10, float(_fx(x1)))
    s += _dxf_pair(20, float(_fy(y1)))
    s += _dxf_pair(11, float(_fx(x2)))
    s += _dxf_pair(21, float(_fy(y2)))
    return s


def _dxf_lwpolyline(points_xy_bulge, closed: bool, layer: str) -> str:
    s = "0\nLWPOLYLINE\n"
    s += _dxf_pair(8, layer)
    s += _dxf_pair(90, len(points_xy_bulge))
    s += _dxf_pair(70, 1 if closed else 0)
    for x, y, bulge in points_xy_bulge:
        s += _dxf_pair(10, float(_fx(x)))
        s += _dxf_pair(20, float(_fy(y)))
        bulge_out = -bulge if BOTTOM_LAYER else bulge
        s += _dxf_pair(42, float(bulge_out) if abs(bulge_out) > 1e-12 else 0.0)
    return s


def _dxf_lwpolyline_raw(points_xy_bulge, closed: bool, layer: str) -> str:
    """
    Variante sans flip Y interne.
    Utile si les points sont déjà dans le repère final (cas overlay STEP).
    """
    s = "0\nLWPOLYLINE\n"
    s += _dxf_pair(8, layer)
    s += _dxf_pair(90, len(points_xy_bulge))
    s += _dxf_pair(70, 1 if closed else 0)
    for x, y, bulge in points_xy_bulge:
        s += _dxf_pair(10, float(_fx(x)))
        s += _dxf_pair(20, float(y))
        bulge_out = -bulge if BOTTOM_LAYER else bulge
        s += _dxf_pair(42, float(bulge_out) if abs(bulge_out) > 1e-12 else 0.0)
    return s


def _dxf_circle(cx, cy, r, layer: str) -> str:
    s = "0\nCIRCLE\n"
    s += _dxf_pair(8, layer)
    s += _dxf_pair(10, float(_fx(cx)))
    s += _dxf_pair(20, float(_fy(cy)))
    s += _dxf_pair(40, float(r))
    return s


def _dxf_arc(cx, cy, r, start_deg, end_deg, layer: str) -> str:
    sx = cx + r * math.cos(math.radians(start_deg))
    sy = cy + r * math.sin(math.radians(start_deg))
    ex = cx + r * math.cos(math.radians(end_deg))
    ey = cy + r * math.sin(math.radians(end_deg))
    cx_t = _fx(cx)
    cy_t = _fy(cy)
    sx_t = _fx(sx)
    sy_t = _fy(sy)
    ex_t = _fx(ex)
    ey_t = _fy(ey)
    start_t = _angle_deg(cx_t, cy_t, sx_t, sy_t)
    end_t = _angle_deg(cx_t, cy_t, ex_t, ey_t)
    mirror_count = int(bool(BOTTOM_LAYER)) + int(bool(FLIP_Y_DXF))
    if mirror_count % 2 == 1:
        start_t, end_t = end_t, start_t
    s = "0\nARC\n"
    s += _dxf_pair(8, layer)
    s += _dxf_pair(10, float(cx_t))
    s += _dxf_pair(20, float(cy_t))
    s += _dxf_pair(40, float(r))
    s += _dxf_pair(50, float(start_t))
    s += _dxf_pair(51, float(end_t))
    return s


def _dxf_text(x: float, y: float, text: str, height: float, layer: str) -> str:
    s = "0\nTEXT\n"
    s += _dxf_pair(8, layer)
    s += _dxf_pair(10, float(_fx(x)))
    s += _dxf_pair(20, float(_fy(y)))
    s += _dxf_pair(40, float(height))
    s += _dxf_pair(1, text)
    return s


# =========================
# GEOMETRIE OUVERTURES
# =========================
def _rot(x: float, y: float, deg: float) -> Tuple[float, float]:
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return (x * ca - y * sa, x * sa + y * ca)


def _rounded_rect_poly(L: float, W: float, R: float) -> List[Tuple[float, float, float]]:
    R = max(0.0, min(R, L / 2.0, W / 2.0))
    hx, hy = L / 2.0, W / 2.0

    if R <= 1e-9:
        return [
            (-hx, -hy, 0.0),
            (hx, -hy, 0.0),
            (hx, hy, 0.0),
            (-hx, hy, 0.0),
        ]

    # Sens horaire, arcs CW => bulge negatif
    return [
        (-hx + R, -hy, 0.0),
        (hx - R, -hy, -_BULGE_90),
        (hx, -hy + R, 0.0),
        (hx, hy - R, -_BULGE_90),
        (hx - R, hy, 0.0),
        (-hx + R, hy, -_BULGE_90),
        (-hx, hy - R, 0.0),
        (-hx, -hy + R, -_BULGE_90),
    ]


def _apply_component_transform(
    poly: List[Tuple[float, float, float]],
    cx: float,
    cy: float,
    rot_deg: float,
    offset_local_x: float = 0.0,
    offset_local_y: float = 0.0,
) -> List[Tuple[float, float, float]]:
    ox, oy = _rot(offset_local_x, offset_local_y, rot_deg)
    out = []
    for x, y, b in poly:
        xr, yr = _rot(x, y, rot_deg)
        out.append((xr + cx + ox, yr + cy + oy, b))
    return out


def bbox_xy(points_xy_bulge: List[Tuple[float, float, float]]) -> Tuple[float, float, float, float]:
    xs = [p[0] for p in points_xy_bulge]
    ys = [p[1] for p in points_xy_bulge]
    return min(xs), max(xs), min(ys), max(ys)


def component_opening_poly(c: Component) -> Optional[List[Tuple[float, float, float]]]:
    spec = PACKAGE_DIMENSIONS.get(c.package_key)
    if not spec:
        return None

    L = float(spec.get("L", 0.0))
    W = float(spec.get("W", 0.0))
    R = float(spec.get("R", 0.0))
    offset_x = float(spec.get("offset_x", 0.0))
    offset_y = float(spec.get("offset_y", spec.get("offset", 0.0)))
    ref_offsets = REFERENCE_OFFSETS.get(c.ref, {})
    offset_x = float(ref_offsets.get("offset_x", offset_x))
    offset_y = float(ref_offsets.get("offset_y", offset_y))

    if L <= 0 or W <= 0:
        return None

    if not USE_ROUNDED_CORNERS:
        R = 0.0

    poly_local = _rounded_rect_poly(L, W, R)
    return _apply_component_transform(
        poly_local,
        c.x,
        c.y,
        c.rot,
        offset_local_x=offset_x,
        offset_local_y=offset_y,
    )


def collect_openings(selected: List[Component]) -> List[Tuple[Component, List[Tuple[float, float, float]]]]:
    out: List[Tuple[Component, List[Tuple[float, float, float]]]] = []
    for c in selected:
        poly = component_opening_poly(c)
        if poly:
            out.append((c, poly))
    return out


def _dist_pt_to_segment(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    abx = bx - ax
    aby = by - ay
    apx = px - ax
    apy = py - ay
    denom = abx * abx + aby * aby
    if denom <= 1e-18:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, (apx * abx + apy * aby) / denom))
    qx = ax + t * abx
    qy = ay + t * aby
    return math.hypot(px - qx, py - qy)


def _orientation(ax: float, ay: float, bx: float, by: float, cx: float, cy: float) -> float:
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def _on_segment(ax: float, ay: float, bx: float, by: float, px: float, py: float, eps: float = 1e-9) -> bool:
    return (
        min(ax, bx) - eps <= px <= max(ax, bx) + eps
        and min(ay, by) - eps <= py <= max(ay, by) + eps
        and abs(_orientation(ax, ay, bx, by, px, py)) <= eps
    )


def _segments_intersect(
    a1: Tuple[float, float],
    a2: Tuple[float, float],
    b1: Tuple[float, float],
    b2: Tuple[float, float],
    eps: float = 1e-9,
) -> bool:
    o1 = _orientation(a1[0], a1[1], a2[0], a2[1], b1[0], b1[1])
    o2 = _orientation(a1[0], a1[1], a2[0], a2[1], b2[0], b2[1])
    o3 = _orientation(b1[0], b1[1], b2[0], b2[1], a1[0], a1[1])
    o4 = _orientation(b1[0], b1[1], b2[0], b2[1], a2[0], a2[1])

    if (o1 > eps and o2 < -eps or o1 < -eps and o2 > eps) and (o3 > eps and o4 < -eps or o3 < -eps and o4 > eps):
        return True

    return (
        _on_segment(a1[0], a1[1], a2[0], a2[1], b1[0], b1[1], eps)
        or _on_segment(a1[0], a1[1], a2[0], a2[1], b2[0], b2[1], eps)
        or _on_segment(b1[0], b1[1], b2[0], b2[1], a1[0], a1[1], eps)
        or _on_segment(b1[0], b1[1], b2[0], b2[1], a2[0], a2[1], eps)
    )


def _point_in_polygon(point: Tuple[float, float], poly_xy: List[Tuple[float, float]], eps: float = 1e-9) -> bool:
    x, y = point
    inside = False
    n = len(poly_xy)
    for i in range(n):
        x1, y1 = poly_xy[i]
        x2, y2 = poly_xy[(i + 1) % n]
        if _on_segment(x1, y1, x2, y2, x, y, eps):
            return True
        crosses = (y1 > y) != (y2 > y)
        if crosses:
            xinters = (x2 - x1) * (y - y1) / max(y2 - y1, eps if y2 >= y1 else -eps) + x1
            if xinters >= x - eps:
                inside = not inside
    return inside


def _flatten_polyline_with_bulge(
    poly: List[Tuple[float, float, float]],
    arc_segments: int = OPENING_CHECK_ARC_SEGMENTS,
) -> List[Tuple[float, float]]:
    if not poly:
        return []

    pts: List[Tuple[float, float]] = []
    count = len(poly)
    for i, (x1, y1, bulge) in enumerate(poly):
        x2, y2, _ = poly[(i + 1) % count]
        if not pts:
            pts.append((x1, y1))

        if abs(bulge) <= 1e-12:
            pts.append((x2, y2))
            continue

        chord = math.hypot(x2 - x1, y2 - y1)
        if chord <= 1e-12:
            continue

        theta = 4.0 * math.atan(bulge)
        radius = chord / (2.0 * math.sin(abs(theta) / 2.0))
        mx = (x1 + x2) / 2.0
        my = (y1 + y2) / 2.0
        h = radius * math.cos(abs(theta) / 2.0)
        dx = (x2 - x1) / chord
        dy = (y2 - y1) / chord
        nx, ny = -dy, dx
        sign = 1.0 if bulge > 0.0 else -1.0
        cx = mx + sign * h * nx
        cy = my + sign * h * ny

        a1 = math.atan2(y1 - cy, x1 - cx)
        a2 = a1 + theta
        steps = max(2, int(math.ceil(abs(theta) / (math.pi / 2.0) * arc_segments)))
        for step in range(1, steps):
            t = step / steps
            a = a1 + theta * t
            pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
        pts.append((x2, y2))

    if len(pts) >= 2 and math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) <= 1e-9:
        pts.pop()
    return pts


def _bbox_overlap(a: Tuple[float, float, float, float], b: Tuple[float, float, float, float], gap: float = 0.0) -> bool:
    return not (
        a[1] + gap < b[0]
        or b[1] + gap < a[0]
        or a[3] + gap < b[2]
        or b[3] + gap < a[2]
    )


def _polygon_distance(poly_a: List[Tuple[float, float]], poly_b: List[Tuple[float, float]]) -> float:
    if not poly_a or not poly_b:
        return float("inf")

    for i in range(len(poly_a)):
        a1 = poly_a[i]
        a2 = poly_a[(i + 1) % len(poly_a)]
        for j in range(len(poly_b)):
            b1 = poly_b[j]
            b2 = poly_b[(j + 1) % len(poly_b)]
            if _segments_intersect(a1, a2, b1, b2):
                return 0.0

    if _point_in_polygon(poly_a[0], poly_b) or _point_in_polygon(poly_b[0], poly_a):
        return 0.0

    min_dist = float("inf")
    for i in range(len(poly_a)):
        a1 = poly_a[i]
        a2 = poly_a[(i + 1) % len(poly_a)]
        for p in poly_b:
            min_dist = min(min_dist, _dist_pt_to_segment(p[0], p[1], a1[0], a1[1], a2[0], a2[1]))
    for i in range(len(poly_b)):
        b1 = poly_b[i]
        b2 = poly_b[(i + 1) % len(poly_b)]
        for p in poly_a:
            min_dist = min(min_dist, _dist_pt_to_segment(p[0], p[1], b1[0], b1[1], b2[0], b2[1]))
    return min_dist


def _closest_point_on_segment(
    px: float,
    py: float,
    ax: float,
    ay: float,
    bx: float,
    by: float,
) -> Tuple[float, float]:
    abx = bx - ax
    aby = by - ay
    denom = abx * abx + aby * aby
    if denom <= 1e-18:
        return ax, ay
    t = max(0.0, min(1.0, ((px - ax) * abx + (py - ay) * aby) / denom))
    return ax + t * abx, ay + t * aby


def _closest_points_between_polygons(
    poly_a: List[Tuple[float, float]],
    poly_b: List[Tuple[float, float]],
) -> Tuple[float, Tuple[float, float], Tuple[float, float]]:
    if not poly_a or not poly_b:
        inf = float("inf")
        return inf, (0.0, 0.0), (0.0, 0.0)

    for i in range(len(poly_a)):
        a1 = poly_a[i]
        a2 = poly_a[(i + 1) % len(poly_a)]
        for j in range(len(poly_b)):
            b1 = poly_b[j]
            b2 = poly_b[(j + 1) % len(poly_b)]
            if _segments_intersect(a1, a2, b1, b2):
                return 0.0, a1, a1

    if _point_in_polygon(poly_a[0], poly_b):
        return 0.0, poly_a[0], poly_a[0]
    if _point_in_polygon(poly_b[0], poly_a):
        return 0.0, poly_b[0], poly_b[0]

    best_dist = float("inf")
    best_a = poly_a[0]
    best_b = poly_b[0]

    for i in range(len(poly_a)):
        a1 = poly_a[i]
        a2 = poly_a[(i + 1) % len(poly_a)]
        for p in poly_b:
            qa = _closest_point_on_segment(p[0], p[1], a1[0], a1[1], a2[0], a2[1])
            dist = math.hypot(p[0] - qa[0], p[1] - qa[1])
            if dist < best_dist:
                best_dist = dist
                best_a = qa
                best_b = p

    for i in range(len(poly_b)):
        b1 = poly_b[i]
        b2 = poly_b[(i + 1) % len(poly_b)]
        for p in poly_a:
            qb = _closest_point_on_segment(p[0], p[1], b1[0], b1[1], b2[0], b2[1])
            dist = math.hypot(p[0] - qb[0], p[1] - qb[1])
            if dist < best_dist:
                best_dist = dist
                best_a = p
                best_b = qb

    return best_dist, best_a, best_b


def analyze_openings(
    openings: List[Tuple[Component, List[Tuple[float, float, float]]]],
    check_overlap: bool = CHECK_OPENING_OVERLAP,
    min_distance_mm: Optional[float] = MIN_OPENING_DISTANCE_MM,
) -> Tuple[Set[int], List[Tuple[float, float, float, str]], Optional[Tuple[str, str, float]]]:
    if len(openings) < 2 or (not check_overlap and min_distance_mm is None):
        return set(), [], None

    flattened = [_flatten_polyline_with_bulge(poly) for _, poly in openings]
    bboxes = [bbox_xy(poly) for _, poly in openings]
    overlapping_indices: Set[int] = set()
    markers: List[Tuple[float, float, float, str]] = []
    closest_pair: Optional[Tuple[str, str, float]] = None

    for i in range(len(openings)):
        comp_a, _poly_a = openings[i]
        flat_a = flattened[i]
        bbox_a = bboxes[i]

        for j in range(i + 1, len(openings)):
            comp_b, _poly_b = openings[j]
            bbox_b = bboxes[j]

            if min_distance_mm is not None and not _bbox_overlap(bbox_a, bbox_b, gap=min_distance_mm):
                continue
            if min_distance_mm is None and not _bbox_overlap(bbox_a, bbox_b):
                dist_bbox_x = max(0.0, max(bbox_a[0] - bbox_b[1], bbox_b[0] - bbox_a[1]))
                dist_bbox_y = max(0.0, max(bbox_a[2] - bbox_b[3], bbox_b[2] - bbox_a[3]))
                approx = math.hypot(dist_bbox_x, dist_bbox_y)
                if closest_pair is None or approx < closest_pair[2]:
                    closest_pair = (comp_a.ref, comp_b.ref, approx)
                continue

            dist, pt_a, pt_b = _closest_points_between_polygons(flat_a, flattened[j])
            if closest_pair is None or dist < closest_pair[2]:
                closest_pair = (comp_a.ref, comp_b.ref, dist)

            if check_overlap and dist <= 1e-6:
                overlapping_indices.add(i)
                overlapping_indices.add(j)
            if min_distance_mm is not None and dist + 1e-6 < min_distance_mm:
                mx = (pt_a[0] + pt_b[0]) / 2.0
                my = (pt_a[1] + pt_b[1]) / 2.0
                markers.append(
                    (
                        mx,
                        my,
                        dist,
                        f"{comp_a.ref}/{comp_b.ref}: {dist:.4f} mm < {min_distance_mm:.4f} mm",
                    )
                )

    return overlapping_indices, markers, closest_pair


def report_opening_analysis(
    openings: List[Tuple[Component, List[Tuple[float, float, float]]]],
    overlapping_indices: Set[int],
    markers: List[Tuple[float, float, float, str]],
    closest_pair: Optional[Tuple[str, str, float]],
    check_overlap: bool = CHECK_OPENING_OVERLAP,
    min_distance_mm: Optional[float] = MIN_OPENING_DISTANCE_MM,
) -> None:
    print("\n[CHECK] Controle des ouvertures")
    print(f"[CHECK] Chevauchement: {'active' if check_overlap else 'ignore'}")
    print(
        "[CHECK] Distance minimale: "
        + (f"{min_distance_mm:.4f} mm" if min_distance_mm is not None else "non definie")
    )
    if closest_pair is not None:
        print(
            f"[CHECK] Paire la plus proche: {closest_pair[0]} / {closest_pair[1]} "
            f"-> {closest_pair[2]:.4f} mm"
        )

    if overlapping_indices:
        refs = ", ".join(sorted({openings[i][0].ref for i in overlapping_indices}))
        print(f"[CHECK] Ouvertures en chevauchement (DXF rouge): {refs}")
    else:
        print("[CHECK] Aucun chevauchement detecte.")

    if markers:
        print(f"[CHECK] Distances insuffisantes (points rouges): {len(markers)}")
        for _, _, _, msg in markers:
            print(f"  - {msg}")
    else:
        print("[CHECK] Aucune distance insuffisante detectee.")


def bbox_from_openings(openings: List[Tuple[Component, List[Tuple[float, float, float]]]]) -> Optional[Tuple[float, float, float, float]]:
    if not openings:
        return None
    xs: List[float] = []
    ys: List[float] = []
    for _, poly in openings:
        xs.extend(p[0] for p in poly)
        ys.extend(p[1] for p in poly)
    return min(xs), max(xs), min(ys), max(ys)


def mirror_bbox_y_if_needed(bbox: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    xmin, xmax, ymin, ymax = bbox
    if not FLIP_Y_DXF:
        return bbox
    y1 = _fy(ymin)
    y2 = _fy(ymax)
    return xmin, xmax, min(y1, y2), max(y1, y2)


def export_bbox(
    openings: List[Tuple[Component, List[Tuple[float, float, float]]]],
    kicad_root: Optional[Any] = None,
    step_component_polys: Optional[List[List[Tuple[float, float]]]] = None,
) -> Optional[Tuple[float, float, float, float]]:
    xs: List[float] = []
    ys: List[float] = []

    for _comp, poly in openings:
        xs.extend(p[0] for p in poly)
        ys.extend(p[1] for p in poly)

    if kicad_root is not None:
        edge_bbox = edgecuts_bbox(kicad_root)
        if edge_bbox is not None:
            xs.extend([edge_bbox[0], edge_bbox[1]])
            ys.extend([edge_bbox[2], edge_bbox[3]])

    if step_component_polys:
        for poly in step_component_polys:
            if not poly:
                continue
            xs.extend(p[0] for p in poly)
            ys.extend(p[1] for p in poly)

    if not xs or not ys:
        return None
    return min(xs), max(xs), min(ys), max(ys)


# =========================
# EDGE.CUTS extraction
# =========================
def _circle_from_3pts(ax, ay, bx, by, cx, cy) -> Optional[Tuple[float, float, float]]:
    d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return None
    ax2ay2 = ax * ax + ay * ay
    bx2by2 = bx * bx + by * by
    cx2cy2 = cx * cx + cy * cy
    ux = (ax2ay2 * (by - cy) + bx2by2 * (cy - ay) + cx2cy2 * (ay - by)) / d
    uy = (ax2ay2 * (cx - bx) + bx2by2 * (ax - cx) + cx2cy2 * (bx - ax)) / d
    r = math.hypot(ux - ax, uy - ay)
    return ux, uy, r


def _angle_deg(cx, cy, px, py) -> float:
    return (math.degrees(math.atan2(py - cy, px - cx)) + 360.0) % 360.0


def _read_xy(node_list: List[Any], head: str) -> Optional[Tuple[float, float]]:
    item = get_first(node_list, head)
    if not item:
        return None

    if len(item) >= 3 and isinstance(item[1], (int, float)) and isinstance(item[2], (int, float)):
        return float(item[1]), float(item[2])

    if len(item) >= 2 and isinstance(item[1], list) and item[1] and item[1][0] == "xy":
        xy = item[1]
        if len(xy) >= 3:
            return float(xy[1]), float(xy[2])

    return None


def _extract_edgecuts_entities(kicad_root: Any, dxf_layer: str = "EDGE_CUTS") -> str:
    s = ""

    for gl in find_lists(kicad_root, "gr_line"):
        layer = get_first(gl, "layer")
        if not layer or len(layer) < 2 or layer[1] != "Edge.Cuts":
            continue
        p1 = _read_xy(gl, "start")
        p2 = _read_xy(gl, "end")
        if p1 and p2:
            s += _dxf_line(p1[0], p1[1], p2[0], p2[1], dxf_layer)

    for ga in find_lists(kicad_root, "gr_arc"):
        layer = get_first(ga, "layer")
        if not layer or len(layer) < 2 or layer[1] != "Edge.Cuts":
            continue

        p1 = _read_xy(ga, "start")
        pm = _read_xy(ga, "mid")
        p2 = _read_xy(ga, "end")
        if not (p1 and pm and p2):
            continue

        circ = _circle_from_3pts(p1[0], p1[1], pm[0], pm[1], p2[0], p2[1])
        if not circ:
            continue

        cx, cy, r = circ
        a1 = _angle_deg(cx, cy, p1[0], p1[1])
        am = _angle_deg(cx, cy, pm[0], pm[1])
        a2 = _angle_deg(cx, cy, p2[0], p2[1])

        def is_between_ccw(a, b, x):
            if a <= b:
                return a <= x <= b
            return x >= a or x <= b

        if is_between_ccw(a1, a2, am):
            start, end = a1, a2
        else:
            start, end = a2, a1

        s += _dxf_arc(cx, cy, r, start, end, dxf_layer)

    for gc in find_lists(kicad_root, "gr_circle"):
        layer = get_first(gc, "layer")
        if not layer or len(layer) < 2 or layer[1] != "Edge.Cuts":
            continue
        pc = _read_xy(gc, "center")
        pe = _read_xy(gc, "end")
        if pc and pe:
            r = math.hypot(pe[0] - pc[0], pe[1] - pc[1])
            s += _dxf_circle(pc[0], pc[1], r, dxf_layer)

    for gr in find_lists(kicad_root, "gr_rect"):
        layer = get_first(gr, "layer")
        if not layer or len(layer) < 2 or layer[1] != "Edge.Cuts":
            continue
        p1 = _read_xy(gr, "start")
        p2 = _read_xy(gr, "end")
        if not (p1 and p2):
            continue

        x1, y1 = p1
        x2, y2 = p2
        xmin, xmax = min(x1, x2), max(x1, x2)
        ymin, ymax = min(y1, y2), max(y1, y2)
        poly = [
            (xmin, ymin, 0.0),
            (xmax, ymin, 0.0),
            (xmax, ymax, 0.0),
            (xmin, ymax, 0.0),
        ]
        s += _dxf_lwpolyline(poly, closed=True, layer=dxf_layer)

    for gp in find_lists(kicad_root, "gr_poly"):
        layer = get_first(gp, "layer")
        if not layer or len(layer) < 2 or layer[1] != "Edge.Cuts":
            continue
        pts_block = get_first(gp, "pts")
        if not pts_block:
            continue
        pts = []
        for item in pts_block:
            if isinstance(item, list) and item and item[0] == "xy" and len(item) >= 3:
                pts.append((float(item[1]), float(item[2]), 0.0))
        if len(pts) >= 3:
            s += _dxf_lwpolyline(pts, closed=True, layer=dxf_layer)

    return s


def edgecuts_bbox(kicad_root: Any) -> Optional[Tuple[float, float, float, float]]:
    xs: List[float] = []
    ys: List[float] = []

    def add_pt(p: Optional[Tuple[float, float]]) -> None:
        if p is None:
            return
        xs.append(float(p[0]))
        ys.append(float(p[1]))

    for gl in find_lists(kicad_root, "gr_line"):
        layer = get_first(gl, "layer")
        if layer and len(layer) >= 2 and layer[1] == "Edge.Cuts":
            add_pt(_read_xy(gl, "start"))
            add_pt(_read_xy(gl, "end"))

    for ga in find_lists(kicad_root, "gr_arc"):
        layer = get_first(ga, "layer")
        if layer and len(layer) >= 2 and layer[1] == "Edge.Cuts":
            p1 = _read_xy(ga, "start")
            pm = _read_xy(ga, "mid")
            p2 = _read_xy(ga, "end")
            add_pt(p1)
            add_pt(pm)
            add_pt(p2)
            if p1 and pm and p2:
                circ = _circle_from_3pts(p1[0], p1[1], pm[0], pm[1], p2[0], p2[1])
                if circ:
                    cx, cy, r = circ
                    xs.extend([cx - r, cx + r])
                    ys.extend([cy - r, cy + r])

    for gc in find_lists(kicad_root, "gr_circle"):
        layer = get_first(gc, "layer")
        if layer and len(layer) >= 2 and layer[1] == "Edge.Cuts":
            pc = _read_xy(gc, "center")
            pe = _read_xy(gc, "end")
            add_pt(pc)
            add_pt(pe)
            if pc and pe:
                r = math.hypot(pe[0] - pc[0], pe[1] - pc[1])
                xs.extend([pc[0] - r, pc[0] + r])
                ys.extend([pc[1] - r, pc[1] + r])

    for gr in find_lists(kicad_root, "gr_rect"):
        layer = get_first(gr, "layer")
        if layer and len(layer) >= 2 and layer[1] == "Edge.Cuts":
            add_pt(_read_xy(gr, "start"))
            add_pt(_read_xy(gr, "end"))

    for gp in find_lists(kicad_root, "gr_poly"):
        layer = get_first(gp, "layer")
        if not (layer and len(layer) >= 2 and layer[1] == "Edge.Cuts"):
            continue
        pts_block = get_first(gp, "pts")
        if not pts_block:
            continue
        for item in pts_block:
            if isinstance(item, list) and item and item[0] == "xy" and len(item) >= 3:
                xs.append(float(item[1]))
                ys.append(float(item[2]))

    if not xs or not ys:
        return None

    return min(xs), max(xs), min(ys), max(ys)


# =========================
# EXPORT DXF
# =========================
def export_dxf_jig(
    out_path: str,
    selected: List[Component],
    include_edge_cuts: bool = True,
    kicad_root: Optional[Any] = None,
    openings_layer: str = "OPENINGS",
    openings_alert_layer: str = OPENINGS_ALERT_LAYER,
    opening_distance_markers_layer: str = OPENING_DISTANCE_MARKERS_LAYER,
    opening_distance_text_layer: str = OPENING_DISTANCE_TEXT_LAYER,
    edge_layer: str = "EDGE_CUTS",
    step_component_polys: Optional[List[List[Tuple[float, float]]]] = None,
    step_layer: str = STEP_CONTOURS_DXF_LAYER,
    overlapping_indices: Optional[Set[int]] = None,
    distance_markers: Optional[List[Tuple[float, float, float, str]]] = None,
) -> List[Tuple[Component, List[Tuple[float, float, float]]]]:
    global _DXF_MIRROR_X_CENTER
    layers: Dict[str, int] = {}
    if EXPORT_DXF_OPENINGS:
        layers[openings_layer] = DXF_OPENINGS_COLOR
    if EXPORT_DXF_OPENINGS_ALERT:
        layers[openings_alert_layer] = DXF_OPENINGS_ALERT_COLOR
    if EXPORT_DXF_DISTANCE_MARKERS:
        layers[opening_distance_markers_layer] = DXF_OPENING_DISTANCE_MARKERS_COLOR
    if EXPORT_DXF_DISTANCE_TEXT:
        layers[opening_distance_text_layer] = DXF_OPENING_DISTANCE_TEXT_COLOR
    if include_edge_cuts:
        layers[edge_layer] = DXF_EDGE_CUTS_COLOR
    if step_component_polys:
        layers[step_layer] = DXF_STEP_CONTOURS_COLOR

    ent = ""
    openings = collect_openings(selected)
    overlapping_indices = overlapping_indices or set()
    distance_markers = distance_markers or []
    export_box = export_bbox(openings, kicad_root=kicad_root, step_component_polys=step_component_polys)
    if BOTTOM_LAYER and export_box is not None:
        _DXF_MIRROR_X_CENTER = (export_box[0] + export_box[1]) / 2.0
        print(f"[DXF] Bottom layer active: symetrie X autour de x={_DXF_MIRROR_X_CENTER:.6f} mm")
    else:
        _DXF_MIRROR_X_CENTER = None

    for idx, (c, poly_world) in enumerate(openings):
        xmin, xmax, ymin, ymax = bbox_xy(poly_world)
        is_alert = idx in overlapping_indices
        if is_alert and EXPORT_DXF_OPENINGS_ALERT:
            layer_name = openings_alert_layer
        elif EXPORT_DXF_OPENINGS:
            layer_name = openings_layer
        else:
            layer_name = None
        print(
            f"[OPENING] {c.ref:>6}  {c.package_key:<28} "
            f"at=({c.x:10.6f},{c.y:10.6f}) rot={c.rot:7.3f}  "
            f"bbox: X[{xmin:10.6f},{xmax:10.6f}]  Y[{ymin:10.6f},{ymax:10.6f}]"
        )
        if layer_name is not None:
            ent += _dxf_lwpolyline(poly_world, closed=True, layer=layer_name)

    for mx, my, dist, label in distance_markers:
        print(f"[WARN] {label} @ ({mx:.4f}, {my:.4f})")
        marker_radius = max(OPENING_DISTANCE_MARKER_RADIUS_MM, (MIN_OPENING_DISTANCE_MM or 0.0) / 2.0)
        if EXPORT_DXF_DISTANCE_MARKERS:
            ent += _dxf_circle(mx, my, marker_radius, layer=opening_distance_markers_layer)
        if EXPORT_DXF_DISTANCE_TEXT:
            ent += _dxf_text(
                mx + marker_radius + OPENING_DISTANCE_TEXT_OFFSET_MM,
                my + marker_radius + OPENING_DISTANCE_TEXT_OFFSET_MM,
                f"{dist:.4f} mm",
                OPENING_DISTANCE_TEXT_HEIGHT_MM,
                layer=opening_distance_text_layer,
            )

    if include_edge_cuts:
        if kicad_root is None:
            raise ValueError("include_edge_cuts=True mais kicad_root=None")
        ent += _extract_edgecuts_entities(kicad_root, dxf_layer=edge_layer)

    if step_component_polys:
        for poly in step_component_polys:
            if len(poly) < 3:
                continue
            poly_bulge = [(x, y, 0.0) for (x, y) in poly]
            ent += _dxf_lwpolyline_raw(poly_bulge, closed=True, layer=step_layer)

    dxf = ""
    dxf += _dxf_header()
    dxf += _dxf_tables(layers)
    dxf += _dxf_entities_start()
    dxf += ent
    dxf += _dxf_entities_end()

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(dxf)

    _DXF_MIRROR_X_CENTER = None

    print(f"\nDXF exported: {out_path}")
    print(f"  openings: {len(openings)}")
    print(f"  openings in alert layer: {len(overlapping_indices)}")
    print(f"  distance markers: {len(distance_markers)}")
    print(f"  edgecuts: {'yes' if include_edge_cuts else 'no'}")
    print(f"  step contours: {len(step_component_polys) if step_component_polys else 0}")

    return openings


# =========================
# PREVIEW STEP + OVERLAY
# =========================
def find_step_file(preferred: Optional[str]) -> Optional[str]:
    if preferred:
        if os.path.isfile(preferred):
            return preferred
        return None

    pcb_base, _ext = os.path.splitext(KICAD_PCB_FILE)
    same_base_candidates = [
        pcb_base + ".step",
        pcb_base + ".stp",
        pcb_base + ".STEP",
        pcb_base + ".STP",
    ]
    for candidate in same_base_candidates:
        if os.path.isfile(candidate):
            return candidate

    return None


def _bbox_xy_from_points(points: List[Tuple[float, float]]) -> Optional[Tuple[float, float, float, float]]:
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), max(xs), min(ys), max(ys)


def convex_hull_2d(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Monotonic chain convex hull. Retourne les points du contour en CCW.
    """
    pts = sorted(set(points))
    if len(pts) <= 1:
        return pts

    def cross(o: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: List[Tuple[float, float]] = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper: List[Tuple[float, float]] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def _bbox_xy(points: List[Tuple[float, float]]) -> Optional[Tuple[float, float, float, float]]:
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), max(xs), min(ys), max(ys)


def _bbox_iou_xy(
    a: Tuple[float, float, float, float],
    b: Tuple[float, float, float, float],
) -> float:
    ax0, ax1, ay0, ay1 = a
    bx0, bx1, by0, by1 = b
    ix = max(0.0, min(ax1, bx1) - max(ax0, bx0))
    iy = max(0.0, min(ay1, by1) - max(ay0, by0))
    inter = ix * iy
    if inter <= 0.0:
        return 0.0
    area_a = max(0.0, ax1 - ax0) * max(0.0, ay1 - ay0)
    area_b = max(0.0, bx1 - bx0) * max(0.0, by1 - by0)
    union = area_a + area_b - inter
    if union <= 0.0:
        return 0.0
    return inter / union


def parse_obj_groups_xy(obj_path: str) -> Tuple[List[Tuple[float, float]], List[List[Tuple[float, float]]]]:
    vertices: List[Tuple[float, float]] = []
    group_entries: List[Tuple[Optional[str], Set[int]]] = []
    current_group: Optional[Set[int]] = None

    with open(obj_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    vertices.append((float(parts[1]), float(parts[2])))
                continue

            if line.startswith("g "):
                group_name = line[2:].strip()
                group_name_l = group_name.lower()
                if any(token in group_name_l for token in ("_copper", "_pad", "_via", "_pcb")):
                    current_group = None
                else:
                    if "/" in group_name:
                        group_parent, _group_child = group_name.rsplit("/", 1)
                    else:
                        group_parent = None

                    current_group = set()
                    group_entries.append((group_parent, current_group))
                continue

            if line.startswith("f ") and current_group is not None:
                for token in line[2:].split():
                    head = token.split("/", 1)[0]
                    if not head:
                        continue
                    idx = int(head)
                    if idx < 0:
                        idx = len(vertices) + idx
                    else:
                        idx = idx - 1
                    if 0 <= idx < len(vertices):
                        current_group.add(idx)

    all_xy = list(vertices)
    merged_entries: List[Tuple[Optional[str], Set[int]]] = []
    for parent, indices in group_entries:
        pts = [vertices[i] for i in indices]
        if len(pts) < 3:
            continue
        bbox = _bbox_xy(pts)
        merged = False
        if parent is not None and bbox is not None:
            for idx, (parent_existing, indices_existing) in enumerate(merged_entries):
                if parent_existing != parent:
                    continue
                pts_existing = [vertices[i] for i in indices_existing]
                bbox_existing = _bbox_xy(pts_existing)
                if bbox_existing is None:
                    continue
                if _bbox_iou_xy(bbox, bbox_existing) >= 0.45:
                    merged_entries[idx][1].update(indices)
                    merged = True
                    break
        if not merged:
            merged_entries.append((parent, set(indices)))

    polys: List[List[Tuple[float, float]]] = []
    for _parent, indices in merged_entries:
        pts = [vertices[i] for i in indices]
        hull = convex_hull_2d(pts)
        if len(hull) >= 3:
            polys.append(hull)

    return all_xy, polys


def parse_step_cartesian_points_xy(step_path: str) -> List[Tuple[float, float]]:
    """
    Fallback minimal sans dépendance CAO:
    extrait les CARTESIAN_POINT du STEP ASCII et retourne leurs XY.
    """
    pattern = re.compile(
        r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[Ee][+-]?\d+)?)\s*,\s*"
        r"([+-]?(?:\d+\.?\d*|\.\d+)(?:[Ee][+-]?\d+)?)\s*,\s*"
        r"([+-]?(?:\d+\.?\d*|\.\d+)(?:[Ee][+-]?\d+)?)\s*\)\s*\)",
        flags=re.IGNORECASE,
    )

    points: List[Tuple[float, float]] = []
    with open(step_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = pattern.search(line)
            if not m:
                continue
            x = float(m.group(1))
            y = float(m.group(2))
            points.append((x, y))
    return points


def _transform_xy(
    x: float,
    y: float,
    src_center: Tuple[float, float],
    dst_center: Tuple[float, float],
    scale: float,
    rot_deg: int,
    flip_y: bool,
) -> Tuple[float, float]:
    xr = x - src_center[0]
    yr = y - src_center[1]

    if flip_y:
        yr = -yr

    a = math.radians(rot_deg)
    ca, sa = math.cos(a), math.sin(a)
    xx = xr * ca - yr * sa
    yy = xr * sa + yr * ca

    return (xx * scale + dst_center[0], yy * scale + dst_center[1])


def _best_alignment(
    src_bbox: Tuple[float, float, float, float],
    dst_bbox: Tuple[float, float, float, float],
) -> Tuple[float, int, bool]:
    sxmin, sxmax, symin, symax = src_bbox
    dxmin, dxmax, dymin, dymax = dst_bbox

    sw, sh = max(1e-9, sxmax - sxmin), max(1e-9, symax - symin)
    dw, dh = max(1e-9, dxmax - dxmin), max(1e-9, dymax - dymin)

    # Candidats: 0/90/180/270 + flipY
    best = (1.0, 0, False)
    best_score = float("inf")

    for rot in (0, 90, 180, 270):
        for flip in (False, True):
            rw, rh = (sw, sh) if rot in (0, 180) else (sh, sw)
            scale = min(dw / rw, dh / rh)

            ww = rw * scale
            hh = rh * scale

            # plus la boite transformee couvre la cible, meilleur est le score
            underfill = (dw - ww) ** 2 + (dh - hh) ** 2
            ratio_penalty = ((ww / max(hh, 1e-9)) - (dw / max(dh, 1e-9))) ** 2
            score = underfill + 10.0 * ratio_penalty

            if score < best_score:
                best_score = score
                best = (scale, rot, flip)

    return best


def compute_step_overlay_geometry(
    step_path: str,
    target_bbox: Tuple[float, float, float, float],
) -> Optional[Tuple[List[Tuple[float, float]], List[List[Tuple[float, float]]], str, float, int, bool]]:
    """
    Retourne:
      - points STEP transformés
      - contours composants transformés (hulls 2D)
      - backend
      - scale, rot, flip utilisés
    """
    verts_xy: List[Tuple[float, float]] = []
    component_polys_xy: List[List[Tuple[float, float]]] = []
    loaded_with = ""

    try:
        import cascadio  # type: ignore
        import uuid

        temp_base = os.path.join(tempfile.gettempdir(), "step-overlay-{}".format(uuid.uuid4().hex))
        temp_obj = temp_base + ".obj"
        temp_mtl = temp_base + ".mtl"
        cascadio.step_to_obj(step_path, temp_obj)
        verts_xy, component_polys_xy = parse_obj_groups_xy(temp_obj)

        if verts_xy:
            loaded_with = "cascadio->obj-groups"
        for temp_path in (temp_obj, temp_mtl):
            if os.path.isfile(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
    except Exception:
        pass

    if not verts_xy:
        verts_xy = parse_step_cartesian_points_xy(step_path)
        if verts_xy:
            loaded_with = "step-text-fallback"

    if not verts_xy:
        return None

    src_bbox = _bbox_xy_from_points(verts_xy)
    if src_bbox is None:
        return None

    scale, rot, flip = _best_alignment(src_bbox, target_bbox)
    if STEP_ALIGN_SCALE is not None:
        scale = float(STEP_ALIGN_SCALE)
    if STEP_ALIGN_ROT_DEG is not None:
        rot = int(STEP_ALIGN_ROT_DEG)
    if STEP_ALIGN_FLIP_Y is not None:
        flip = bool(STEP_ALIGN_FLIP_Y)

    sxmin, sxmax, symin, symax = src_bbox
    dxmin, dxmax, dymin, dymax = target_bbox
    src_center = ((sxmin + sxmax) / 2.0, (symin + symax) / 2.0)
    dst_center = (
        (dxmin + dxmax) / 2.0 + STEP_ALIGN_OFFSET_X_MM,
        (dymin + dymax) / 2.0 + STEP_ALIGN_OFFSET_Y_MM,
    )

    verts_xy_t: List[Tuple[float, float]] = [
        _transform_xy(x, y, src_center, dst_center, scale, rot, flip)
        for (x, y) in verts_xy
    ]
    component_polys_t: List[List[Tuple[float, float]]] = []
    for poly in component_polys_xy:
        poly_t = [_transform_xy(x, y, src_center, dst_center, scale, rot, flip) for (x, y) in poly]
        component_polys_t.append(poly_t)

    return verts_xy_t, component_polys_t, loaded_with, scale, rot, flip


def _configure_matplotlib() -> None:
    cache_root = os.path.join("/tmp", "matplotlib-test-export-pcb-cache")
    os.makedirs(cache_root, exist_ok=True)

    mpl_dir = os.environ.get("MPLCONFIGDIR")
    if not mpl_dir:
        mpl_dir = os.path.join(cache_root, "mplconfig")
        os.environ["MPLCONFIGDIR"] = mpl_dir
    os.makedirs(mpl_dir, exist_ok=True)
    os.environ.setdefault("XDG_CACHE_HOME", cache_root)


def preview_step_overlay(
    step_path: str,
    openings: List[Tuple[Component, List[Tuple[float, float, float]]]],
    all_components: List[Component],
    target_bbox: Tuple[float, float, float, float],
    out_image: str,
    overlapping_indices: Optional[Set[int]] = None,
    distance_markers: Optional[List[Tuple[float, float, float, str]]] = None,
    show_window: bool = False,
) -> bool:
    overlay = compute_step_overlay_geometry(step_path, target_bbox)
    if overlay is None:
        print("\n[STEP] Impossible d'extraire une geometrie XY depuis le STEP.")
        print("       Option recommandee: python3 -m pip install cascadio")
        return False

    verts_xy_t, component_polys_t, loaded_with, scale, rot, flip = overlay
    overlapping_indices = overlapping_indices or set()
    distance_markers = distance_markers or []

    all_x = [p[0] for p in verts_xy_t] + [c.x for c in all_components]
    all_y = [p[1] for p in verts_xy_t] + [_fy(c.y) for c in all_components]
    for _, poly in openings:
        all_x.extend(p[0] for p in poly)
        all_y.extend(_fy(p[1]) for p in poly)

    xmin, xmax = min(all_x), max(all_x)
    ymin, ymax = min(all_y), max(all_y)
    margin = 4.0
    width = max(1.0, xmax - xmin) + 2.0 * margin
    height = max(1.0, ymax - ymin) + 2.0 * margin
    zoom = max(1e-3, float(PREVIEW_ZOOM))
    view_width = width / zoom
    view_height = height / zoom
    cx = (xmin + xmax) / 2.0
    cy = (ymin + ymax) / 2.0
    xlim = (cx - view_width / 2.0, cx + view_width / 2.0)
    ylim = (cy - view_height / 2.0, cy + view_height / 2.0)

    _configure_matplotlib()
    import matplotlib

    if not show_window:
        matplotlib.use("Agg")

    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon

    fig_w = min(PREVIEW_WINDOW_MAX_W_IN, max(PREVIEW_WINDOW_MIN_W_IN, view_width * PREVIEW_WINDOW_SCALE))
    fig_h = min(PREVIEW_WINDOW_MAX_H_IN, max(PREVIEW_WINDOW_MIN_H_IN, view_height * PREVIEW_WINDOW_SCALE))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=PREVIEW_DPI)
    fig.patch.set_facecolor(PREVIEW_BACKGROUND_COLOR)
    ax.set_facecolor(PREVIEW_BACKGROUND_COLOR)

    if component_polys_t:
        for poly in component_polys_t:
            if len(poly) >= 3:
                ax.add_patch(
                    Polygon(
                        poly,
                        closed=True,
                        facecolor=PREVIEW_STEP_FILL_COLOR,
                        edgecolor=PREVIEW_STEP_EDGE_COLOR,
                        linewidth=PREVIEW_STEP_EDGE_WIDTH,
                        alpha=PREVIEW_STEP_ALPHA,
                    )
                )
    else:
        if len(verts_xy_t) > 80000:
            step_stride = max(1, len(verts_xy_t) // 80000)
            verts_plot = verts_xy_t[::step_stride]
        else:
            verts_plot = verts_xy_t
        ax.scatter(
            [p[0] for p in verts_plot],
            [p[1] for p in verts_plot],
            s=PREVIEW_STEP_POINT_SIZE,
            c=PREVIEW_STEP_POINT_COLOR,
            alpha=PREVIEW_STEP_POINT_ALPHA,
            linewidths=0,
        )

    for idx, (_, poly) in enumerate(openings):
        pts = [(x, _fy(y)) for x, y, _b in poly]
        if not pts:
            continue
        pts.append(pts[0])
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        if idx in overlapping_indices:
            ax.plot(xs, ys, color=SVG_ALERT_STROKE, linewidth=PREVIEW_ALERT_LINE_WIDTH, alpha=PREVIEW_ALERT_ALPHA)
        else:
            ax.plot(xs, ys, color=PREVIEW_OPENING_COLOR, linewidth=PREVIEW_OPENING_LINE_WIDTH, alpha=PREVIEW_OPENING_ALPHA)

    for mx, my, dist, _label in distance_markers:
        my_plot = _fy(my)
        ax.add_patch(
            Circle(
                (mx, my_plot),
                radius=OPENING_DISTANCE_MARKER_RADIUS_MM,
                facecolor=SVG_WARN_FILL,
                edgecolor=SVG_WARN_FILL,
                alpha=PREVIEW_WARN_ALPHA,
            )
        )
        ax.text(
            mx + OPENING_DISTANCE_MARKER_RADIUS_MM + OPENING_DISTANCE_TEXT_OFFSET_MM,
            my_plot + OPENING_DISTANCE_MARKER_RADIUS_MM + OPENING_DISTANCE_TEXT_OFFSET_MM,
            f"{dist:.4f} mm",
            color=SVG_WARN_TEXT,
            fontsize=PREVIEW_WARN_TEXT_SIZE,
            fontweight=PREVIEW_WARN_TEXT_WEIGHT,
            ha="left",
            va="bottom",
        )

    ax.scatter(
        [c.x for c in all_components],
        [_fy(c.y) for c in all_components],
        s=PREVIEW_COMPONENT_CENTER_SIZE,
        c=PREVIEW_COMPONENT_CENTER_COLOR,
        alpha=PREVIEW_COMPONENT_CENTER_ALPHA,
    )
    for c in all_components:
        ax.text(
            c.x + COMPONENT_REF_TEXT_OFFSET_MM,
            _fy(c.y) + COMPONENT_REF_TEXT_OFFSET_MM,
            c.ref,
            color=COMPONENT_REF_TEXT_COLOR,
            fontsize=COMPONENT_REF_TEXT_SIZE,
            ha="left",
            va="bottom",
            alpha=COMPONENT_REF_TEXT_ALPHA,
        )

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.tight_layout(pad=0.2)
    fig.savefig(
        out_image,
        dpi=PREVIEW_DPI,
        bbox_inches="tight",
        pad_inches=PREVIEW_SAVE_PADDING_IN,
        facecolor=PREVIEW_BACKGROUND_COLOR,
    )

    if show_window:
        plt.show()
    plt.close(fig)

    print(f"\n[STEP] Preview image exportee: {out_image}")
    print(f"[STEP] Backend: {loaded_with}")
    print(f"[STEP] Alignement auto: scale={scale:.6g}, rot={rot} deg, flipY={flip}")

    return True


# =========================
# MAIN
# =========================
def main() -> None:
    print("Reading:", KICAD_PCB_FILE)

    if not os.path.isfile(KICAD_PCB_FILE):
        print("ERROR: file not found.")
        return

    root = parse_kicad_pcb(KICAD_PCB_FILE)
    comps = extract_components(root)

    print("\nComponents found:", len(comps), "\n")
    for c in comps:
        print(
            f"{c.ref:>6}  {(c.value or ''):<12}  {c.footprint:<45}  "
            f"at=({c.x:8.3f},{c.y:8.3f})  rot={c.rot:6.1f}  layer={c.layer or '-'}"
        )

    if GROUP_BY_PACKAGE:
        groups = group_by_package(comps)
        print("\nGrouped by package\n")
        for k in sorted(groups.keys()):
            print(f"{k:<32} : {len(groups[k])} components")

        known = [k for k in groups.keys() if k in PACKAGE_DIMENSIONS]
        missing = [k for k in groups.keys() if k not in PACKAGE_DIMENSIONS]
        print("\nPackage dimensions coverage:")
        print("  with dims :", ", ".join(sorted(known)) if known else "-")
        print("  missing   :", ", ".join(sorted(missing)[:15]) + (" ..." if len(missing) > 15 else ""))

    if len(comps) == 0:
        print("\nDEBUG: aucune empreinte trouvee. Verifie que le fichier contient '(footprint'.")

    filtered = comps
    if EXPORT_LAYERS is not None:
        filtered = [c for c in filtered if c.layer in EXPORT_LAYERS]

    if EXPORT_PACKAGES:
        selected = [c for c in filtered if c.package_key in set(EXPORT_PACKAGES)]
    else:
        selected = filtered

    openings = collect_openings(selected)
    overlapping_indices, distance_markers, closest_pair = analyze_openings(
        openings,
        check_overlap=CHECK_OPENING_OVERLAP,
        min_distance_mm=MIN_OPENING_DISTANCE_MM,
    )
    report_opening_analysis(
        openings,
        overlapping_indices=overlapping_indices,
        markers=distance_markers,
        closest_pair=closest_pair,
        check_overlap=CHECK_OPENING_OVERLAP,
        min_distance_mm=MIN_OPENING_DISTANCE_MM,
    )

    step_path = None
    target = None
    step_component_polys_for_dxf: Optional[List[List[Tuple[float, float]]]] = None
    if ENABLE_STEP_PREVIEW or EXPORT_STEP_CONTOURS_TO_DXF:
        step_path = find_step_file(STEP_PCB_FILE)
        if not step_path:
            if ENABLE_STEP_PREVIEW:
                print("\n[STEP] Aucun fichier STEP trouve (*.step/*.stp). Preview sautee.")
            if EXPORT_STEP_CONTOURS_TO_DXF:
                print("[STEP] Contours STEP non exportes dans le DXF (fichier STEP absent).")
        else:
            target = edgecuts_bbox(root)
            if target is None:
                target = bbox_from_openings(openings)

            if target is None:
                print("\n[STEP] Impossible de calculer une bbox cible (edgecuts + openings absents).")
            else:
                target = mirror_bbox_y_if_needed(target)
                overlay = compute_step_overlay_geometry(step_path, target)
                if overlay is None:
                    print("[STEP] Geometrie STEP non disponible pour export/preview.")
                else:
                    _verts_xy_t, step_component_polys_t, backend, scale, rot, flip = overlay
                    if EXPORT_STEP_CONTOURS_TO_DXF:
                        step_component_polys_for_dxf = step_component_polys_t
                    print(f"[STEP] Alignement calcule: backend={backend}, scale={scale:.6g}, rot={rot}, flipY={flip}")
                    print(f"[STEP] Contours composants reels trouves dans le STEP: {len(step_component_polys_t)}")

    openings = export_dxf_jig(
        out_path=OUT_DXF_FILE,
        selected=selected,
        include_edge_cuts=INCLUDE_EDGE_CUTS,
        kicad_root=root,
        step_component_polys=step_component_polys_for_dxf,
        step_layer=STEP_CONTOURS_DXF_LAYER,
        overlapping_indices=overlapping_indices,
        distance_markers=distance_markers,
    )

    if EXPORT_STEP_CONTOURS_TO_DXF and not step_component_polys_for_dxf:
        print(f"[STEP] Aucun contour composant STEP a ajouter dans le DXF ({STEP_CONTOURS_DXF_LAYER}).")

    if ENABLE_STEP_PREVIEW and step_path and target is not None:
        preview_step_overlay(
            step_path=step_path,
            openings=openings,
            all_components=comps,
            target_bbox=target,
            out_image=PREVIEW_IMAGE_FILE,
            overlapping_indices=overlapping_indices,
            distance_markers=distance_markers,
            show_window=SHOW_PREVIEW_WINDOW,
        )


if __name__ == "__main__":
    main()
