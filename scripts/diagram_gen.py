#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 JSON 清单生成可编辑的 draw.io (.drawio) 文件。

用法:
  python diagram_gen.py <input.json> <output.drawio>

输入 JSON 示例:
{
  "title": "全题技术路线图",
  "direction": "TB",            # TB(上->下) 或 LR(左->右)，只影响自动布局
  "page":  {"width": 850, "height": 1100},
  "nodeW": 170, "nodeH": 60,
  "gapX":  60,  "gapY": 40,
  "nodes": [
    {"id":"n1","label":"赛题分析","kind":"process"},
    {"id":"n2","label":"建立模型","kind":"process"},
    {"id":"n3","label":"是否满足?","kind":"decision"},
    {"id":"n4","label":"结束","kind":"end"}
  ],
  "edges": [
    {"source":"n1","target":"n2"},
    {"source":"n2","target":"n3"},
    {"source":"n3","target":"n2","label":"否"},
    {"source":"n3","target":"n4","label":"是"}
  ]
}

kind 与配色(可在 Draw.io 里再改):
  start=绿椭圆  end=红椭圆  process=蓝圆角矩形  decision=橙菱形
  io=紫平行四边形  box=灰矩形  note=黄便签  title=蓝加粗矩形

输出为 .drawio(XML)，可直接用 Draw.io 打开、拖拽修改，再导出 SVG/PDF/PNG。
"""
import json
import sys
from collections import deque
from xml.sax.saxutils import escape

STYLES = {
    "start":    ("rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;", "ellipse"),
    "end":      ("rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;", "ellipse"),
    "process":  ("rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;", "rectangle"),
    "decision": ("rhombus;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;", "rhombus"),
    "io":       ("shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;", "parallelogram"),
    "box":      ("rounded=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;", "rectangle"),
    "note":     ("shape=note;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;", "note"),
    "title":    ("rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;", "rectangle"),
}
EDGE_STYLE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"


def escape_attr(s):
    return escape(str(s), {'"': "&quot;"})


def bfs_levels(node_ids, edges):
    adj = {i: [] for i in node_ids}
    indeg = {i: 0 for i in node_ids}
    for e in edges:
        s, t = e.get("source"), e.get("target")
        if s in adj and t in adj and s != t:
            adj[s].append(t)
            indeg[t] += 1
    roots = [i for i in node_ids if indeg[i] == 0] or [node_ids[0]]
    level = {i: 0 for i in node_ids}
    visited = set()
    q = deque()
    for r in roots:
        if r not in visited:
            q.append(r)
            visited.add(r)
    while q:
        n = q.popleft()
        for m in adj[n]:
            if m not in visited:
                level[m] = level[n] + 1
                visited.add(m)
                q.append(m)
    return level, visited


def layout(nodes, edges, direction, nodeW, nodeH, gapX, gapY):
    ids = [n["id"] for n in nodes]
    level, _ = bfs_levels(ids, edges)
    groups = {}
    for i in ids:
        groups.setdefault(level[i], []).append(i)
    pos = {}
    for lvl in sorted(groups):
        col_items = groups[lvl]
        if direction == "LR":
            x = lvl * (nodeW + gapX)
            y0 = -(len(col_items) - 1) * (nodeH + gapY) / 2.0
            for j, i in enumerate(col_items):
                pos[i] = (x, y0 + j * (nodeH + gapY))
        else:  # TB
            y = lvl * (nodeH + gapY)
            x0 = -(len(col_items) - 1) * (nodeW + gapX) / 2.0
            for j, i in enumerate(col_items):
                pos[i] = (x0 + j * (nodeW + gapX), y)
    # 用户显式坐标覆盖
    for n in nodes:
        if n.get("x") is not None and n.get("y") is not None:
            pos[n["id"]] = (n["x"], n["y"])
    return pos


def build_drawio(cfg, pos):
    nodes = cfg["nodes"]
    edges = cfg.get("edges", [])
    nodeW = cfg.get("nodeW", 170)
    nodeH = cfg.get("nodeH", 60)
    pw = cfg.get("page", {}).get("width", 850)
    ph = cfg.get("page", {}).get("height", 1100)
    parts = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append('<mxfile host="app.diagrams.net" modified="2024-01-01T00:00:00.000Z" agent="diagram_gen.py" version="21.0.0" type="device">')
    parts.append('  <diagram id="d1" name="%s">' % escape_attr(cfg.get("title", "diagram")))
    parts.append('    <mxGraphModel dx="1000" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="%s" pageHeight="%s" math="0" shadow="0">' % (pw, ph))
    parts.append('      <root>')
    parts.append('        <mxCell id="0" />')
    parts.append('        <mxCell id="1" parent="0" />')
    for n in nodes:
        i = n["id"]
        kind = n.get("kind", "box")
        style, _shape = STYLES.get(kind, STYLES["box"])
        x, y = pos[i]
        w = n.get("w", nodeW)
        h = n.get("h", nodeH)
        val = escape_attr(n.get("label", ""))
        parts.append('        <mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">' % (i, val, style))
        parts.append('          <mxGeometry x="%g" y="%g" width="%g" height="%g" as="geometry" />' % (round(x, 1), round(y, 1), w, h))
        parts.append('        </mxCell>')
    for idx, e in enumerate(edges, 1):
        ei = "e%d" % idx
        val = escape_attr(e.get("label", ""))
        src = e["source"]
        tgt = e["target"]
        parts.append('        <mxCell id="%s" value="%s" style="%s" edge="1" parent="1" source="%s" target="%s">' % (ei, val, EDGE_STYLE, src, tgt))
        parts.append('          <mxGeometry relative="1" as="geometry" />')
        parts.append('        </mxCell>')
    parts.append('      </root>')
    parts.append('    </mxGraphModel>')
    parts.append('  </diagram>')
    parts.append('</mxfile>')
    return "\n".join(parts) + "\n"


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    in_path, out_path = sys.argv[1], sys.argv[2]
    cfg = json.load(open(in_path, encoding="utf-8"))
    pos = layout(cfg["nodes"], cfg.get("edges", []), cfg.get("direction", "TB"),
                 cfg.get("nodeW", 170), cfg.get("nodeH", 60),
                 cfg.get("gapX", 60), cfg.get("gapY", 40))
    xml = build_drawio(cfg, pos)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml)
    print("OK -> %s (%d nodes, %d edges)" % (out_path, len(cfg["nodes"]), len(cfg.get("edges", []))))


if __name__ == "__main__":
    main()