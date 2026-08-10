#!/usr/bin/env python3
"""CUMCM 支撑材料收集器。

用法:
  python collect_materials.py <工作区根目录>

把以下内容收集到 <工作区>/materials/ 支撑材料文件夹：
  - 源程序/    code/ 下的 .py（可运行）
  - 中间图表/  figures/ 下的图件
  - 结果数据/  result*.xlsx / RESULTS.md / data/processed
  - 附录A_支撑材料目录.md（清单）
  - 附录B_代码表格.md（代码表格 + 行号，供论文附录 B 直接引用）

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
    code_table = ["# 附录 B　代码（Python）", "", "| 行号 | 代码 |", "|---|---|"]

    # 1) 源程序
    code_dir = ws / "code"
    n_code = 0
    if code_dir.is_dir():
        for f in sorted(code_dir.rglob("*.py")):
            shutil.copy2(f, code_out / f.name)
            n_code += 1
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            span = f"1--{len(lines)}" if lines else "1"
            code_table.append(f"| {span} | {f.name}（{len(lines)} 行） |")
    manifest.append(f"## 源程序（{n_code} 个 .py）")

    # 2) 中间图表
    fig_dir = ws / "figures"
    n_fig = 0
    if fig_dir.is_dir():
        for f in sorted(fig_dir.iterdir()):
            if f.is_file():
                shutil.copy2(f, fig_out / f.name)
                n_fig += 1
    manifest.append(f"## 中间图表（{n_fig} 个文件）")

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
    code_table.append(f"> 共 {n_code} 个源程序；完整代码见 源程序/ 文件夹。")

    (out / "附录A_支撑材料目录.md").write_text("\n".join(manifest), encoding="utf-8")
    (out / "附录B_代码表格.md").write_text("\n".join(code_table), encoding="utf-8")

    print(f"✅ 支撑材料已生成: {out}")
    print(f"   源程序 {n_code} 个 / 图表 {n_fig} 个 / 数据 {n_data} 个")
    print("   附录A_支撑材料目录.md + 附录B_代码表格.md 已生成，内容可粘贴进论文附录")
    print("交付口径：Word 论文 + PDF 论文 + 支撑材料文件夹，共 3 样。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
