---
name: cumcm-agent
description: 全国大学生数学建模竞赛（CUMCM，国赛）全流程自动执行助手。当用户要参加国赛、需要从赛题分析开始跑完"赛题分析→建模求解→编程实现→图表生成→论文撰写→编译合规→改进循环"的完整竞赛流程、并偏好 A 题（连续型/物理类）建模时使用。触发场景：用户提到"国赛""CUMCM""数学建模竞赛""建模论文""A题/赛题"，或要求按竞赛流水线完成一篇数模论文。
---

# 国赛建模全流程助手（CUMCM Agent）

把国赛当作一条 **8 步流水线** 自动推进。每一步产出文件后 **停下等用户确认/反馈** 再继续（步骤 2 为反馈型检查点：收集用户意见、修订后继续）。

## 使用方式

1. 向用户索取：**赛题 PDF** 与 **原始数据表格（xlsx/csv 等）**；询问参赛年份，并**核对当年官方规则**（正文页数上限、匿名要求、提交格式）。
2. 初始化工作区（见下；目录名以用户指定为准）。
3. 按 8 步流水线逐步骤执行，每步先读对应 `references/` 文件、套用 `templates/` 模板，完成后停下汇报。
4. **断点续跑**：工作区即状态——文件存在且通过检查 = 已完成。中断后重跑时，自动跳过已完成步骤，从失败/未做处继续。

> ⚠️ 编码约定：本 skill 所有文件均为 **UTF-8 编码**。Windows 下读写必须显式指定 UTF-8：
> - PowerShell 读取：`Get-Content -Encoding UTF8`；写入：`[System.IO.File]::WriteAllText($path, $text, [System.Text.UTF8Encoding]::new($false))`
> - 或先执行 `chcp 65001` 再操作
> 不要用默认代码页（GBK）读写，否则中文会乱码。
>
> ⚠️ 额外坑（实战踩过）：
> - **全角引号陷阱**：Windows PowerShell 命令串里的全角引号（U+201C/U+201D）会被自动转成 ASCII 双引号，导致命令被截断/内容损坏。命令行传中文时用「」（U+300C/U+300D）代替；生成中文文件推荐 `python -X utf8 -c "..."` 以三层单引号写内容（避开全角引号/ASCII 双引号/美元符/反引号）。
> - **终端乱码 ≠ 文件损坏**：终端按 GBK 显示 UTF-8 内容会乱码；校验文件用 Python 按 UTF-8 读回，不能只看终端。

## 门禁分级（Acceptance Gate）— 核心原则

来自 ARIS：**循环可以 DRIVE（驱动），不能 ACQUIT（自我宣判无罪）**。Codex 可以驱动流程前进，但绝不能自己宣布"合格/完成"。

| 类型 | 定义 | 例子 | 谁判定 |
|------|------|------|--------|
| **Type-A 执行/客观门禁** | 机器可检查的事实 | PDF 编译成功、Word 导出成功、`evidence_check.py` 全过、页数合规、公式无 undefined | Codex 可自行判定 |
| **Type-B 质量/正确性门禁** | 需要品味与领域判断 | "论文合格了""模型是对的""摘要很突出" | **必须由用户判定**（或用户提供的另一模型），Codex 绝不自我宣判 |

应用规则：
- 每步"完成" = 该步 Type-A 检查通过 **且** 用户对 Type-B 确认
- 步骤8 停止条件必须是 Type-A 全过 **且** 用户验收通过；Codex 不能因为"我觉得改好了"就停止
- 证据预检（`scripts/evidence_check.py`）是 Type-A；"这个结论站得住"是 Type-B

## 工作区结构

```
cumcm-2026/            # 示例目录名，以用户指定为准
├── problem/             # 赛题 PDF + 提取文本 + DATA_PROFILE.md（步骤0 产出）
├── data/                # 原始数据（只读）+ data/processed/ 清洗后数据
├── PROBLEM_ANALYSIS.md  # 步骤1 产出
├── MODELING_REPORT.md   # 步骤2 产出
├── code/                # 步骤3 产出（main.py 等）
├── RESULTS.md           # 步骤3 产出
├── figures/             # 步骤4/5 产出
├── paper/               # 步骤6/7 产出（main.tex / main.pdf / main.docx）
├── PAPER_ACCEPTANCE_CONTRACT.md  # 步骤6 动笔前定验收标准
├── claims.json          # 步骤8 证据预检输入（关键数字+出处）
├── COMP_REVIEW.md       # 步骤8 审计记录
└── materials/           # 支撑材料（步骤8 用 collect_materials.py 生成）
```

## 8 步流水线

### 步骤 0 — 输入处理（先做）
- 用户上传赛题 PDF 和原始数据 xlsx 后，先跑：
  `python scripts/process_inputs.py <工作区> <赛题.pdf> [附件1.xlsx ...]`
- 产出：`problem/<赛题名>_提取文本.txt`（PDF 全文）+ `problem/DATA_PROFILE.md`（数据探查报告）+ `data/`（原始数据副本）
- 读 `references/09-数据处理.md`：PDF 是扫描版时的处理办法、数据清洗规则、数据字典
- ✅ 检查点：赛题文本与数据探查报告就绪后，进入步骤 1

### 步骤 1 — 赛题分析 → `PROBLEM_ANALYSIS.md`
- 读 `references/01-赛题分析.md`，套用 `templates/PROBLEM_ANALYSIS.md`
- 判断问题类型；本题为 A 题（连续/物理类）时，重点做"物理机制分析"：识别控制方程、定解条件、参数来源
- ✅ 检查点（approve，Type-B 由用户判定）：用户批准后进入步骤 2

### 步骤 2 — 建模求解 → `MODELING_REPORT.md`
- 读 `references/02-建模选型.md`，套用 `templates/MODELING_REPORT.md`
- 建立模型（A 题：机理建模 + 数值方法 + 参数辨识 + 灵敏度/稳定性分析），写明假设、符号、求解方案
- 🔁 检查点（feedback）：收集用户意见，修订后继续

### 步骤 3 — 编程实现 → `code/main.py` + `RESULTS.md`
- 读 `references/03-编程实现.md`，套用 `templates/RESULTS.md`
- 实现模型求解并跑出结果，做 5 项可信度校验（Sanity/Consistency/Physical/Prediction/Evaluation）
- ✅ 检查点（approve，Type-B 由用户判定）：用户批准后继续

### 步骤 4 — 图表生成 → `figures/`
- 读 `references/04-图表规范.md`
- 生成论文级图表：黑白可印刷、矢量/高分辨率、坐标轴规范；正确性规则（事实）必守，风格规则可商量
- A 题典型图：解曲面/热图/等高线、时空演化、参数扫描、收敛性、灵敏度

### 步骤 5 — 流程图/架构图 → `figures/`
- 画模型框架图、算法流程图（draw.io / mermaid / HTML→PDF 均可，输出矢量文件给 LaTeX 引用）
- ⚠️ 为保证 LaTeX→Word 转换成功，**架构图用外部图片文件（`\includegraphics` 引用），不要用内嵌 TikZ 代码**

### 步骤 6 — 论文撰写 → `paper/main.tex`
- 读 `references/05-论文写作.md`，用 `templates/paper/main.tex` 骨架
- **动笔前先定验收标准**：用 `templates/PAPER_ACCEPTANCE_CONTRACT.md` 写 `PAPER_ACCEPTANCE_CONTRACT.md`（读 `references/08-验收契约.md`），请用户确认（10-20 条可检验断言）
- 写完整论文：摘要单独一页、正文按当年官方页数上限
- ✅ 检查点（approve，Type-B 由用户判定）：用户批准后继续

### 步骤 7 — 编译 PDF + 导出 Word
- 读 `references/06-编译与合规.md`
- **Word**：用 pandoc 由 LaTeX 导出 `paper/main.docx`（`pandoc main.tex -o main.docx`）——已实测可用
- **PDF**：优先 **Overleaf**（上传 main.tex + figures/，编译器选 XeLaTeX，下载 main.pdf）；本机有可用 xelatex 时也可本地编译（详见 06 方案 B，注意 Modex 内置 MiKTeX 需先初始化）
- **合规检查**：跑 `python scripts/compliance_check.py paper [paper/main.pdf]`，要求无 FAIL（摘要≤1页/页码页脚中部/图表居中/每条文献被\\cite/页边距/匿名/图表明细）
- ✅ 检查点（Type-A）：PDF 与 Word 都成功生成，且合规检查无 FAIL，用户批准进入步骤 8

### 步骤 8 — 改进循环 → 修订终稿
- 读 `references/07-改进循环.md`
- ① **Type-A 机器审计**：
  - 证据预检：把摘要/结论里的关键数字整理成 `claims.json`，跑 `python scripts/evidence_check.py <工作区> --batch claims.json`，要求全部 `verified`
  - 页数/公式渲染/图表引用/匿名/参考文献 逐项机器检查（PDF 与 Word 各查一遍）
- ② **Type-B 验收**：按 `PAPER_ACCEPTANCE_CONTRACT.md` 逐条核对，**由用户判定**未过项；列出未过项 → 修复 → 重编译 → 复验
- ③ 可选：若用户提供另一个模型的 API，可做独立审稿（审稿人**直接读原始文件**，不喂摘要/不引导结论）
- ④ **支撑材料收集**：跑 `python scripts/collect_materials.py <工作区>`，生成 `materials/`（源程序+中间图表+结果数据+附录A/B清单）
- **停止条件 = Type-A 全过 + 用户验收通过**。Codex 不得以"我觉得改好了"为由停止。
- **交付口径（只交 3 样）**：① `paper/main.docx`（Word 论文）② `paper/main.pdf`（PDF 论文）③ `materials/`（支撑材料文件夹）；其余中间产物留在过程目录不上交

## 硬性规则

- 每步先读对应 references 再执行；产出严格套用模板结构
- 所有数值结果必须可复现（固定随机种子、保存中间数据、写清运行命令）
- **论文里每个数字必须可溯源**：步骤8 用 `scripts/evidence_check.py` 做证据预检（Type-A 门禁）
- **Codex 不得自我宣判"论文合格/完成"**：Type-B 一律由用户判定
- 图表必须黑白可印刷（国赛打印评审）；正确性规则必守，风格规则可商量
- 论文必须匿名（不出现姓名/学校/指导教师），符合当年页数限制
- **终稿双格式交付**：PDF（参赛提交）+ Word（`main.docx`，由 LaTeX 经 pandoc 导出；导出的 Word 是内容骨架，最终按学校模板微调）
- **交付口径 3 样**：Word 论文 + PDF 论文 + 支撑材料文件夹（`materials/`）；参考文献 ≥8 条且每条正文有 \\cite，无官网/组委会条目
- A 题优先机理建模：守恒/平衡方程 → 数值求解 → 灵敏度与稳定性分析，避免纯数据拟合
- 完成全部 8 步后，向用户输出：终稿路径（PDF + Word）、关键结果摘要、验收契约判定结果、待人工核对的点