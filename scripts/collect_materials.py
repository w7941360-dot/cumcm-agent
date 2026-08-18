#!/usr/bin/env python3
"""CUMCM 支撑材料收集器。

用法:
  python collect_materials.py <工作区根目录>

把以下内容收集到 <工作区>/materials/ 支撑材料文件夹：
  - 源程序/    code/ 下的求解/模型代码 .py/.m（自动排除生图脚本：code/plots/ 目录或 plot_*/fig_*/draw_* 命名）
  - 中间图表/  figures/ 下的图件
  - 结果数据/  result*.xlsx / RESULTS.md / data/processed
  - 附录A_支撑材料目录.md（清单）
  - 附录B_代码表格.md（每问求解/模型代码明细：文件名 + 逐行行号，不含生图代码）

交付口径：只交 3 样——Word 论文、PDF 论文、支撑材料文件夹。
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="CUMCM supporting-materials collector.")
    ap.add_argument("workspace", help="工作区根目录")
    a = ap.parse_args()
    ws = Path(a.workspace)
    out = ws / "materials"
    code_out = out / "源程序"
    fig_out = out / "中间图表"
    data_out = out / "结果数据"
    for d in (out, code_out, fig_out, data_out):
        d.mkdir(parents=True, exist_ok=True)

    manifest = ["# 附录 A　支撑材料目录", ""]
    code_table = ["# 附录 B　代码明细（每问求解代码 + 模型代码，不含生图代码）", ""]

    def is_plot_script(code_dir: Path, path: Path) -> bool:
        # 生图脚本约定：code/plots/ 或 code/figures/ 目录；或文件名以 plot_/fig_/draw_ 开头、以 _plot/_fig/_draw 结尾
        try:
            rel = path.relative_to(code_dir)
        except ValueError:
            return False
        if any(seg.lower() in ("plots", "figures") for seg in rel.parts[:-1]):
            return True
        name = path.name.lower()
        return any(
            name.startswith(h + "_") or name.endswith("_" + h + path.suffix.lower())
            for h in ("plot", "fig", "draw")
        )

    # 1) 源程序（.py / .m：每问求解/模型代码，文件名 + 逐行行号；生图脚本不展示）
    code_dir = ws / "code"
    code_exts = (".py", ".m")
    n_code = 0
    n_plot = 0
    if code_dir.is_dir():
        for f in sorted(p for p in code_dir.rglob("*") if p.is_file() and p.suffix.lower() in code_exts):
            if is_plot_script(code_dir, f):
                n_plot += 1
                continue
            shutil.copy2(f, code_out / f.name)
            n_code += 1
            rel = f.relative_to(ws).as_posix()
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            code_table.append(f"## {rel}")
            code_table.append("")
            code_table.append("| 行号 | 代码 |")
            code_table.append("|---:|---|")
            for i, ln in enumerate(lines, 1):
                cell = ln.replace("|", "\\|")
                code_table.append(f"| {i} | {cell} |")
            code_table.append("")
    manifest.append(f"## 源程序（{n_code} 个 .py/.m，不含生图脚本）")

    # 2) 中间图表
    fig_dir = ws / "figures"
    n_fig = 0
    if fig_dir.is_dir():
        for f in sorted(fig_dir.iterdir()):
            if f.is_file() and f.suffix.lower() == ".png":
                shutil.copy2(f, fig_out / f.name)
                n_fig += 1
    manifest.append(f"## 中间图表（{n_fig} 个 PNG）")

    # 3) 结果数据
    n_data = 0
    for pat in ("result*.xlsx", "*.xlsx", "RESULTS.md"):
        for f in sorted(ws.glob(pat)):
            shutil.copy2(f, data_out / f.name)
            n_data += 1
    proc = ws / "data" / "processed"
    if proc.is_dir():
        for f in sorted(proc.iterdir()):
            if f.is_file():
                shutil.copy2(f, data_out / f.name)
                n_data += 1
    manifest.append(f"## 结果数据（{n_data} 个文件）")

    # 4) 附录 B 汇总
    code_table.append("")
    code_table.append(f"> 共 {n_code} 个源程序（求解/模型代码），已按文件展开（文件名 + 逐行行号）；生图脚本 {n_plot} 个不展示。")

    (out / "附录A_支撑材料目录.md").write_text("\n".join(manifest), encoding="utf-8")
    (out / "附录B_代码表格.md").write_text("\n".join(code_table), encoding="utf-8")

    print(f"✅ 支撑材料已生成: {out}")
    print(f"   源程序 {n_code} 个 / 图表 {n_fig} 个 / 数据 {n_data} 个")
    print("   附录A_支撑材料目录.md + 附录B_代码表格.md 已生成，内容可粘贴进论文附录")
    print("交付口径：Word 论文 + PDF 论文 + 支撑材料文件夹，共 3 样。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
