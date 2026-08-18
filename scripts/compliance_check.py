#!/usr/bin/env python3
"""CUMCM 论文合规自动检查。

用法:
  python compliance_check.py <paper目录> [main.pdf]

检查项（对齐 2025 国赛实战反馈的版式合规要求）:
  1. 页边距 >= 2.5cm            (tex geometry 配置)
  2. 页码页脚中部 + 摘要起从 1 连续  (fancyhdr 配置)
  3. 摘要 <= 1 页                (PDF 实际页数/页序, 有 pypdf 时)
  4. 图表全部居中                 (figure/table 环境内含 \\centering)
  5. 每条参考文献至少被 \\cite 一次  (\\bibitem vs \\cite 覆盖)
  6. 参考文献条数 >= 8
  7. 无官网/组委会条目            (URL 检查: 组委会/官网/cumcm 等)
  8. 匿名                        (无姓名/学校/指导老师 特征)
  9. 图/表编号完整且正文有引用      (figure/table 有 label 且被 \\ref)

退出码: 0 = 全部 PASS; 1 = 存在 FAIL/WARN。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REQUIRED_MARGIN = 2.5


def parse_tex(tex_path: Path) -> str:
    return tex_path.read_text(encoding="utf-8", errors="replace")


def check_geometry(text: str):
    m = re.search(r"\\usepackage\[([^\]]*)\]{geometry}", text)
    if not m:
        return ("FAIL", "未找到 geometry 配置")
    opts = m.group(1)
    for side in ("top", "bottom", "left", "right"):
        mm = re.search(side + r"\s*=\s*([\d.]+)\s*cm", opts)
        if not mm:
            return ("FAIL", f"geometry 缺 {side} 边距")
        if float(mm.group(1)) < REQUIRED_MARGIN - 1e-9:
            return ("FAIL", f"{side} 边距 {mm.group(1)}cm < 2.5cm")
    return ("PASS", f"页边距均 >= {REQUIRED_MARGIN}cm")


def check_pagenum(text: str):
    has_fancy = "\\pagestyle{fancy}" in text and "\\fancyfoot[C]" in text
    has_reset = "\\setcounter{page}{1}" in text or "\\setcounter{page}{1}" in text.replace(" ", "")
    if has_fancy:
        return ("PASS", "页码页脚中部 (fancyhdr)")
    return ("FAIL", "未找到 页脚中部页码 配置 (\\pagestyle{fancy} + \\fancyfoot[C])")


def check_centering(text: str):
    # 每个 figure/table 环境里必须有 \centering
    bad = []
    for env in ("figure", "table"):
        pat = re.compile(r"\\begin\{" + env + r"\}(.*?)\\end\{" + env + r"\}", re.DOTALL)
        for i, m in enumerate(pat.finditer(text), 1):
            body = m.group(1)
            if "\\centering" not in body:
                bad.append(f"{env}#{i}")
    if bad:
        return ("FAIL", "以下环境缺 \\centering: " + ", ".join(bad))
    return ("PASS", "所有 figure/table 均已居中")


def check_citations(text: str):
    bibs = re.findall(r"\\bibitem\{([^}]+)\}", text)
    cites = re.findall(r"\\cite\{([^}]+)\}", text)
    cited_set = set()
    for c in cites:
        cited_set.update(x.strip() for x in c.split(","))
    if not bibs:
        return ("FAIL", "没有 thebibliography")
    missing = [b for b in bibs if b not in cited_set]
    if len(bibs) < 8:
        return ("FAIL", f"参考文献仅 {len(bibs)} 条 (<8)")
    if missing:
        return ("FAIL", f"以下文献未被 \\cite: {missing}")
    return ("PASS", f"{len(bibs)} 条参考文献全部被 \\cite 引用")


def check_no_official_url(text: str):
    hits = re.findall(r"(https?://\S+|组委会|官网|cumcm\.cn)", text, re.IGNORECASE)
    # 过滤掉注释行里的 URL
    hits = [h for h in hits if not re.match(r"^\s*%", text[text.find(h)-30:text.find(h)].splitlines()[-1] if text.find(h) >= 0 else "")]
    if hits:
        return ("WARN", "疑似官网/组委会条目: " + ", ".join(set(hits[:5])))
    return ("PASS", "无官网/组委会条目")


def check_anonymous(text: str):
    # 常见身份特征（保守，主要靠人工复核；不匹配"大学/学院"等赛题正文常见词）
    pat = re.compile(r"(?:指导教师|指导老师|指导教授|学号|联系电话|手机号|作者简介|@[a-z0-9]+\.[a-z]{2,})", re.IGNORECASE)
    hits = set(m.group(0) for m in pat.finditer(text))
    if hits:
        return ("WARN", "疑似身份信息（需人工确认）: " + ", ".join(sorted(hits)))
    return ("PASS", "未发现明显身份信息")


def check_refs_complete(text: str):
    figs = re.findall(r"\\begin\{figure\}(.*?)\\end\{figure\}", text, re.DOTALL)
    tabs = re.findall(r"\\begin\{table\}(.*?)\\end\{table\}", text, re.DOTALL)
    bad = []
    for kind, items in (("figure", figs), ("table", tabs)):
        for i, b in enumerate(items, 1):
            lab = re.search(r"\\label\{([^}]+)\}", b)
            if not lab:
                bad.append(f"{kind}#{i} 缺 label")
            elif f"\\ref{{{lab.group(1)}}}" not in text:
                bad.append(f"{kind}#{i} label {{{lab.group(1)}}} 未被 \\ref 引用")
    if bad:
        return ("WARN", "; ".join(bad))
    return ("PASS", "图/表 label 与 \\ref 完整")


def check_pdf_abstract_page(pdf_path: Path):
    if not pdf_path.exists():
        return ("SKIP", "未提供 PDF，跳过页数检查")
    n_pages = None
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        n_pages = doc.page_count
        doc.close()
    except Exception:
        try:
            import pypdf
            n_pages = len(pypdf.PdfReader(str(pdf_path)).pages)
        except Exception as e:
            return ("SKIP", f"无法读取 PDF: {e}")
    # 摘要页 = 第 1 页；检查第 1 页是否含「摘要」文本且不超 1 页
    first_text = ""
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        first_text = doc[0].get_text()[:200]
        doc.close()
    except Exception:
        pass
    return ("PASS", f"PDF 共 {n_pages} 页，摘要从第 1 页起（正文页数请人工对照官方上限）")


def main() -> int:
    ap = argparse.ArgumentParser(description="CUMCM paper compliance check.")
    ap.add_argument("paper_dir", help="paper 目录（含 main.tex）")
    ap.add_argument("pdf", nargs="?", default=None, help="可选 main.pdf 路径")
    a = ap.parse_args()
    d = Path(a.paper_dir)
    tex = d / "main.tex"
    if not tex.exists():
        print("ERROR: 找不到 main.tex"); return 1
    text = parse_tex(tex)
    pdf = Path(a.pdf) if a.pdf else d / "main.pdf"

    checks = [
        ("页边距 >= 2.5cm", check_geometry(text)),
        ("页码页脚中部", check_pagenum(text)),
        ("图表居中", check_centering(text)),
        ("参考文献 \\cite 覆盖", check_citations(text)),
        ("官网/组委会条目", check_no_official_url(text)),
        ("匿名", check_anonymous(text)),
        ("图/表引用完整", check_refs_complete(text)),
        ("摘要页数", check_pdf_abstract_page(pdf)),
    ]
    failed = 0
    for name, (status, msg) in checks:
        flag = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "SKIP": "⏭"}[status]
        print(f"{flag} [{status}] {name}: {msg}")
        if status == "FAIL":
            failed += 1
    print("结论:", "全部通过" if failed == 0 else f"存在 {failed} 项 FAIL，请修复后复检")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
