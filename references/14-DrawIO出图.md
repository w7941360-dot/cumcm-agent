# 12 Draw.io 出图（流程图 / 架构图 / 示意图）

> 用途：生成「全题技术路线图」「全题工作机理示意图」「每问算法流程图/模型框架图」。这套流程既能让我精准生成，又能让你在 Draw.io 里**手动拖拽修改**，再直接对接 LaTeX（矢量）与 Word（PNG）。

## 工具
- **Draw.io 桌面版（本机已装）**：`C:\Users\21662\AppData\Local\Programs\draw.io\draw.io.exe`
- 也可用网页版：https://app.diagrams.net （零安装，同文件格式）
- **命令行导出**（三种格式）：
  ```powershell
  & "<draw.io.exe>" --export --format svg --output <out.svg> <in.drawio>
  & "<draw.io.exe>" --export --format pdf --output <out.pdf> <in.drawio>
  & "<draw.io.exe>" --export --format png --output <out.png>  <in.drawio>
  ```

## 工作流（我生成 → 你修改 → 导出进论文）
1. **我生成**：按节点/连线清单，用 `scripts/diagram_gen.py` 生成可编辑 `.drawio`
   ```
   python scripts/diagram_gen.py <清单.json> <图名.drawio>
   ```
   清单 JSON 见下；`templates/diagrams/` 已有两个可改样例：`技术路线图`、`工作机理示意图`。
2. **你修改**：双击 `.drawio` 用 Draw.io 打开，随意拖节点、改文字、调箭头/配色——这是**可编辑源**。
3. **导出进论文**：
   - LaTeX 用**矢量**：`--format svg` 或 `--format pdf`
   - Word 用**位图**：`--format png`
   - LaTeX 里 `\includegraphics{../figures/技术路线图.pdf}`；Word 版同目录放 PNG。

## 清单 JSON 说明
```json
{
  "title": "全题技术路线图",
  "direction": "TB",             // TB=上→下, LR=左→右（只影响自动布局）
  "page":  { "width": 850, "height": 1100 },
  "nodeW": 170, "nodeH": 60, "gapX": 60, "gapY": 40,
  "nodes": [
    { "id": "n1", "label": "赛题分析", "kind": "process" },
    { "id": "n2", "label": "是否满足?", "kind": "decision", "x": 300, "y": 200 }
  ],
  "edges": [
    { "source": "n1", "target": "n2" },
    { "source": "n2", "target": "n1", "label": "否" }
  ]
}
```

### kind → 形状 / 配色（在 Draw.io 里仍可改）
| kind | 形状 | 配色（fill / stroke） | 用途 |
|------|------|----------------------|------|
| `start` | 椭圆 | 绿 #d5e8d4 / #82b366 | 起点 |
| `end` | 椭圆 | 红 #f8cecc / #b85450 | 终点 |
| `process` | 圆角矩形 | 蓝 #dae8fc / #6c8ebf | 一般处理 |
| `decision` | 菱形 | 橙 #ffe6cc / #d79b00 | 判定 |
| `io` | 平行四边形 | 紫 #e1d5e7 / #9673a6 | 输入/输出 |
| `box` | 矩形 | 灰 #f5f5f5 / #666 | 系统/容器 |
| `note` | 便签 | 黄 #fff2cc / #d6b656 | 注释/方程 |
| `title` | 矩形加粗 | 蓝 #dae8fc / #6c8ebf | 标题 |

- 节点可省 `x/y`（自动分层布局），也可显式指定 `x`、`y`、`w`、`h` 精确定位。
- 边可省 `label`；`source` / `target` 对应节点 `id`。

## 与论文衔接
- 图注按「五要素」写（见 `references/04-图表规范.md`）；图前有引导文字、图后有解释。
- **保留 `.drawio` 源文件**与清单 JSON（放工作区 `figures/` 旁或 `templates/diagrams/`），导出的 SVG/PDF/PNG 只是最终产物；后续改图改源文件重导，别直接改位图。
- 架构/流程类图**必须**用外部图片文件（`\includegraphics`）引用，不要内嵌 TikZ（保证 LaTeX→Word 可转换）。