---
name: cumcm-agent
description: 全国大学生数学建模竞赛（CUMCM，国赛）全流程自动执行助手。当用户要参加国赛、需要从赛题分析开始跑完"赛题分析→建模求解→编程实现→图表生成→论文撰写→编译合规→改进循环"的完整竞赛流程、并偏好 A 题（连续型/物理类）建模时使用。触发场景：用户提到"国赛""CUMCM""数学建模竞赛""建模论文""A题/赛题"，或要求按竞赛流水线完成一篇数模论文。
---

# 国赛建模全流程助手（CUMCM Agent）

把国赛当作一条 **8 步流水线** 自动推进。每一步产出文件后 **停下等用户确认/反馈** 再继续（步骤 2 为反馈型检查点：收集用户意见、修订后继续）。

## 使用方式

1. 向用户索取：**赛题 PDF** 与 **原始数据表格（xlsx/csv 等）**；询问参赛年份，并**核对当年官方规则**（匿名要求、提交格式等）；正文页数目标：**正文（不含参考文献与附录）≤ 30 页，25 页最好**。
2. **确认求解引擎偏好**（调用 skill 时一次性问清，写入 `plan/solution_manifest.json` 的 `engine` 字段）：纯 MATLAB / 纯 Python / Python+MATLAB 混合。本机已装 MATLAB R2025b；重数值（ODE/PDE/全局优化/布局优化）推荐 MATLAB，重数据（xlsx/JSON/字符串）推荐 Python，想要两套实现互验的强交叉验证推荐混合（决策指引见 `references/03-编程实现.md`）。**混合 = 各取所长**：Python 干数据/胶水活，MATLAB 干重数值活，另一引擎做独立交叉验证，按 `references/03-编程实现.md` 的『混合模式执行手册』自动分工。
3. 初始化工作区（见下；目录名以用户指定为准）。
4. 按 8 步流水线逐步骤执行，每步先读对应 `references/` 文件、套用 `templates/` 模板，完成后停下汇报。
5. **断点续跑**：工作区即状态——文件存在且通过检查 = 已完成；优化题以 `code/run_registry.json` 台账为准（status=ok 且结果非空才算完成，aborted/empty/failed 不算）。中断后重跑时，自动跳过已完成步骤，从失败/未做处继续。

> ⚠️ 编码约定：本 skill 所有文件均为 **UTF-8 编码**。Windows 下读写必须显式指定 UTF-8：
> - PowerShell 读取：`Get-Content -Encoding UTF8`；写入：`[System.IO.File]::WriteAllText($path, $text, [System.Text.UTF8Encoding]::new($false))`
> - 或先执行 `chcp 65001` 再操作
> 不要用默认代码页（GBK）读写，否则中文会乱码。
>
> ⚠️ 额外坑（实战踩过）：
> - **全角引号陷阱**：Windows PowerShell 命令串里的全角引号（U+201C/U+201D）会被自动转成 ASCII 双引号，导致命令被截断/内容损坏。命令行传中文时用「」（U+300C/U+300D）代替；生成中文文件推荐 `python -X utf8 -c "..."` 以三层单引号写内容（避开全角引号/ASCII 双引号/美元符/反引号）。
> - **终端乱码 ≠ 文件损坏**：终端按 GBK 显示 UTF-8 内容会乱码；校验文件用 Python 按 UTF-8 读回，不能只看终端。
> - **控制台编码**：Windows 控制台默认 GBK，跑含 emoji 的脚本（如 compliance_check.py）会报 UnicodeEncodeError，先 `$env:PYTHONIOENCODING='utf-8'`
> - **编译退出码**：xelatex 有错也会写出 PDF，必须检查 `$LASTEXITCODE` 与 `main.log` 中的 `LaTeX Error`（实战：缺 `\item` 时报 missing item 仍产出 PDF）

## 环境预置（开始前）

运行流水线前，确认本机已具备以下环境（缺哪个装哪个）。本机（2026-08 实测）已按此清单就绪：Python 3.13.5 + MiKTeX 25.12（xelatex 4.16），正式 main.tex 可本地编译。

### 必需

| 用途 | 软件 | 安装 / 校验 |
|------|------|------------|
| 求解 / 出图 / 结果文件 | Python 3.13+（Anaconda）+ numpy、scipy、matplotlib、openpyxl、pandas、pillow、pypdf、pypdfium2 | 安装：`pip install numpy scipy matplotlib openpyxl pandas pillow pypdf pypdfium2`；校验：python 可正常 import 上述库 |
| PDF 论文（中文） | XeLaTeX（MiKTeX 或 TeX Live，含 ctex / xecjk 宏包） | Windows 安装：`winget install MiKTeX.MiKTeX --silent`；配国内镜像与缺包自动安装：`mpm --set-repository=https://mirrors.ustc.edu.cn/CTAN/systems/win32/miktex/tm/packages/`、`initexmf --set-config-value=[MPM]AutoInstall=1`；校验：`xelatex --version` |
| PDF 合规检查 | pypdf / pypdfium2 | 随 Python 一并安装 |

### 可选

- 编辑器：VS Code + LaTeX Workshop（推荐）；或 TeXstudio；或 Overleaf Community Edition（Docker 自托管）
- 文献管理：Zotero
- 在线编译兜底：TeX Live.net / Overleaf（本地 xelatex 不可用时的备选）

### 注意

- PATH 更新只对新终端生效；当前会话可用完整路径调用 xelatex
- 首次编译会自动补装宏包，依赖 USTC / CTAN 镜像，需联网
- 论文 PDF 优先本地 xelatex 编译（离线可用，矢量/高清）；图表统一 PNG（≥300 dpi）或矢量

## 门禁分级（Acceptance Gate）— 核心原则

来自 ARIS：**循环可以 DRIVE（驱动），不能 ACQUIT（自我宣判无罪）**。Codex 可以驱动流程前进，但绝不能自己宣布"合格/完成"。

| 类型 | 定义 | 例子 | 谁判定 |
|------|------|------|--------|
| **Type-A 执行/客观门禁** | 机器可检查的事实 | PDF 编译成功、`evidence_check.py` 全过、`solution_audit.py` 全过（每问交付完整/优化纪律）、页数合规、公式无 undefined | Codex 可自行判定 |
| **Type-B 质量/正确性门禁** | 需要品味与领域判断 | "论文合格了""模型是对的""摘要很突出" | **必须由用户判定**（或用户提供的另一模型），Codex 绝不自我宣判 |

应用规则：
- 每步"完成" = 该步 Type-A 检查通过 **且** 用户对 Type-B 确认
- 步骤8 停止条件必须是 Type-A 全过 **且** 用户验收通过；Codex 不能因为"我觉得改好了"就停止
- 证据预检（`scripts/evidence_check.py`）与求解交付审计（`scripts/solution_audit.py`）是 Type-A；"这个结论站得住""这个范式最优"是 Type-B

## 工作区结构

```
cumcm-2026/            # 示例目录名，以用户指定为准
├── problem/             # 赛题 PDF + 提取文本 + DATA_PROFILE.md（步骤0 产出）
├── data/                # 原始数据（只读）+ data/processed/ 清洗后数据
├── PROBLEM_ANALYSIS.md  # 步骤1 产出（含全链路矩阵）
├── plan/
│   └── solution_manifest.json  # 步骤1 产出的机器可读全链路矩阵（solution_audit.py 读取）
├── MODELING_REPORT.md   # 步骤2 产出
├── SOLUTION_ACCEPTANCE_CONTRACT.md  # 步骤1-2 求解验收契约（优化题必写）
├── code/                # 步骤3 产出（problem1.py / problem2.py 等 + run_registry.json 运行台账）
├── RESULTS.md           # 步骤3 产出
├── figures/             # 步骤4/5 产出
├── paper/               # 步骤6/7 产出（main.tex / main.pdf）
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
- 读 `references/02-建模选型.md` 的 **A 题模式表**（2020-2025 统计/共同规律/默认解题顺序/三类高频方法包），按「解析基线 + 数值仿真 + 约束优化」三层结构规划；优化题另读 `references/11-带硬指标的设计优化.md`；把「设计/找最优」类问题写成规范「 max f(x) + s.t. + 大括号约束组」时，见 `references/15-优化模型表示.md`；判断「四大题型/算法适用/是否值得智能优化」看 `references/16-A题方法知识库.md`
- **全链路矩阵**：逐问填「依赖｜路线｜决策变量｜硬约束｜全模型｜代理｜单次成本｜预算｜代码入口｜结果文件｜官方模板及列名｜失败预案」；登记官方附件 `resultN.xlsx` 与模板列名；后续问题预算默认预留 ≥20%
- 生成机器可读 `plan/solution_manifest.json`（字段与矩阵一致，供步骤 8 审计）
- ✅ 检查点（approve，Type-B 由用户判定）：用户批准后进入步骤 2
- ✅ **Type-A 门禁**：全链路矩阵无空缺列、官方附件已登记、每问有失败预案，否则不得进入步骤 2

### 步骤 2 — 建模求解 → `MODELING_REPORT.md`
- 读 `references/02-建模选型.md`，套用 `templates/MODELING_REPORT.md`；数值方法/优化算法按问题类型选型，速查表见 `references/16-A题方法知识库.md`
- 建立模型（A 题：机理建模 + 数值方法 + 参数辨识 + 灵敏度/稳定性分析），写明假设、符号、求解方案
- **优化题（含硬指标+设计变量）必做**：先理论推导搜索空间（每个子问题先给出「 max + s.t. + 大括号」标准模型式，模板见 `references/15-优化模型表示.md`）→ 枚举 ≥2 个候选范式 → 硬约束进入搜索（可行性优先）→ 定义代理校准方案；写 `MODELING_REPORT.md` 第 0 节"求解治理总览"（范式/硬约束裕量/可行种子或上界/代理保真度/预算）
- **求解验收契约**：步骤 1-2 用 `templates/SOLUTION_ACCEPTANCE_CONTRACT.md` 写 `SOLUTION_ACCEPTANCE_CONTRACT.md`（每问必答量、硬约束、官方附件、代理阈值、预算、不可接受状态），请用户确认
- 🔁 检查点（feedback）：收集用户意见，修订后继续
- ✅ **Type-A 门禁**：搜索空间审计通过（含可行种子或理论上界）、硬约束已表达进优化、代理校准方案已定义，否则不得进入步骤 3

### 步骤 3 — 编程实现 → `code/` + `RESULTS.md`
- 读 `references/03-编程实现.md`，套用 `templates/RESULTS.md`
- **引擎选择**：调用 skill 时已确认并写入 `plan/solution_manifest.json` 的 `engine` 字段，此处沿用（如需变更在此时说明）；**混合模式按 `references/03-编程实现.md` 的『混合模式执行手册』自动分工（Python 数据/胶水 + MATLAB 重数值 + 另一引擎交叉验证），每问引擎分配见全链路矩阵**；本机已装 MATLAB R2025b（`references/10-MATLAB.md`，无头 `matlab -batch`）
- **出图引擎与求解一致**：图表可用 Python matplotlib 或 MATLAB（R2025b）生成，规范见 `references/04-图表规范.md`（含 MATLAB 出图统一样式）
- 实现模型求解并跑出结果，做 5 项可信度校验（Sanity/Consistency/Physical/Prediction/Evaluation）；优化题另做"优化过程专项验证"（可行种子/代理一致性/多起点/约束边界/上界夹逼/范式公平对比/高精度复验）
- **运行台账**：每次实验写入 `code/run_registry.json`（run_id/唯一变化假设/范式/状态/耗时/结果/下一步）；一次只改一个假设；`aborted`/`empty`/`failed` 不得计为完成；未完成不得命名 `final`；路径一律从工作区根目录派生
- 结果写 CSV/mat（供步骤8 证据预检），图导出 PDF+PNG 成对（进 `figures/`）
- ✅ 检查点（approve，Type-B 由用户判定）：用户批准后继续
- ✅ **Type-A 门禁**：每个子问题都有可运行入口、真实非空结果、硬约束判定和规定附件，否则不得进入步骤 4

### 步骤 4 — 图表生成 → `figures/`
- 读 `references/04-图表规范.md`
- **本步骤只出「数据图」**（基于数值结果/数据，见 `references/04` 的「数据图 vs 非数据图」分界）：用 matplotlib / MATLAB 从数据生成，图内数字**必须可溯源**（与 `resultN.xlsx`/运行输出一致）；专业彩色/灰度配色（色盲友好、灰度可区分）、矢量/高分辨率、坐标轴规范；正确性规则必守，风格可商量
- 示意图检查清单见 `references/12-实战复盘与常见坑.md`：黑白或学术彩色均可、严谨细致、箭头方向逐图核对、图内大字号不重叠、文字不出框
- A 题典型图：解曲面/热图/等高线、时空演化、参数扫描、收敛性、灵敏度；优化题另加：优化收敛曲线、范式对比图、约束边界图
- **先做图表规划再出图**：全题配技术路线图 + 工作机理示意图；每个已求解子问题默认 ≥3 张（工作机理示意图 + 算法流程图 + 结果图），验证/灵敏度分析另加 1 张检查图；只有表格明显更清楚时才少画图并说明原因
- 图注写「展示什么 + 关键结果/验证含义」；**不写**「支撑哪问/数据来源」这类流程解释（见 references/04 图注要点）

### 步骤 5 — 流程图/架构图 → `figures/`
- **本步骤只出「非数据图」**（不基于数据，见 `references/04` 的「数据图 vs 非数据图」分界）：①**全题技术路线图** ②**全题工作机理示意图**（可并入态势图）③每问**算法流程图/模型框架图**
- **首选 Draw.io**（流程见 `references/14-DrawIO出图.md`）：`python scripts/diagram_gen.py <清单.json> <图名.drawio>` 生成可编辑 `.drawio` → 需要人工微调就打开 Draw.io 改 → `drawio.exe --export --format svg|pdf|png` 导出矢量/PNG 到 `figures/`（源文件 `.drawio` 与 JSON 保留）
- 备选：mermaid / HTML→PDF；输出矢量文件给 LaTeX 引用
- ⚠️ **架构图用外部图片文件（`\includegraphics` 引用），避免内嵌 TikZ 代码**（便于替换/调整，利于文字不超出图形）

### 步骤 6 — 论文撰写 → `paper/main.tex`
- 读 `references/05-论文写作.md`，用 `templates/paper/main.tex` 骨架
- **动笔前先定验收标准**：用 `templates/PAPER_ACCEPTANCE_CONTRACT.md` 写 `PAPER_ACCEPTANCE_CONTRACT.md`（读 `references/08-验收契约.md`），请用户确认（10-20 条可检验断言）
- 写完整论文：摘要单独一页（≤1 页）、正文（不含参考文献与附录）≤ 30 页，25 页最好
- **AI 使用声明**：参考文献前独立成段（默认「使用 AI」版，见 `references/13-AI工具使用规范.md`）并 `\cite` 所用 AI 模型；参考文献中加 AI 模型版本条目（详见 references/05、13）
- **标题居中**：汉字编号一级标题与「参考文献」标题都要居中
- **问题重述**：五个子问题直接写「问题一：」…文本编号，不用 enumerate 自动编号（避免「1. 问题 1」重复编号）
- **按 `references/04-图表规范.md` 的插入时机放图表**：每章放对应图（问题分析流程图/模型准备态势图/每问流程+结果图/灵敏度图），图前有引导、图后必有解释，连续图表间必须有文字，正文解释文字多于图表
- ✅ 检查点（approve，Type-B 由用户判定）：用户批准后继续

### 步骤 7 — 编译 PDF
- 读 `references/06-编译与合规.md`
- **只出 PDF**：用 xelatex 本地编译 `paper/main.pdf`（参赛提交）；**不再导出 .docx / Word 版**
- **PDF**：优先本机本地编译（xelatex，见「环境预置」，本机已装 MiKTeX 25.12）；本地不可用时回退 Overleaf / TeX Live.net（上传 main.tex + figures/，编译器选 XeLaTeX，下载 main.pdf）
- **合规检查**：跑 `python scripts/compliance_check.py paper [paper/main.pdf]`，要求无 FAIL（摘要≤1页/页码页脚中部/图表居中/每条文献被\cite/页边距/匿名/图表明细/AI工具使用声明）
- **同步纪律**：每次改 main.tex 后重编 PDF（检查退出码与 log）+ 重跑合规；Windows 控制台先 `$env:PYTHONIOENCODING="utf-8"`（详见 references/06、12）
- ✅ 检查点（Type-A）：PDF 成功生成，且合规检查无 FAIL，用户批准进入步骤 8

### 步骤 8 — 改进循环 → 修订终稿
- 读 `references/07-改进循环.md`
- ① **Type-A 机器审计**：
  - **求解交付审计**（先做）：跑 `python scripts/solution_audit.py <工作区> --mode deliverable`，要求 PASS（每问代码/结果/官方附件齐全，resultN.xlsx 非空非模板且表头/列序合规，硬约束由全模型结果满足）；优化题再跑 `--mode optimization`（代理保真度、范式切换、预算、空/中断误判），要求 PASS
  - 证据预检：把摘要/结论里的关键数字整理成 `claims.json`，跑 `python scripts/evidence_check.py <工作区> --batch claims.json`，要求全部 `verified`
  - 页数/公式渲染/图表引用/匿名/参考文献/AI工具使用声明 逐项机器检查（查 PDF）
- ② **Type-B 验收**：按 `PAPER_ACCEPTANCE_CONTRACT.md` 逐条核对，**由用户判定**未过项；列出未过项 → 修复 → 重编译 → 复验
- ③ 可选：若用户提供另一个模型的 API，可做独立审稿（审稿人**直接读原始文件**，不喂摘要/不引导结论）
- ④ **支撑材料收集**：跑 `python scripts/collect_materials.py <工作区>`，生成 `materials/`（源程序+中间图表+结果数据+附录A/B清单+**AI工具使用详情** `AI工具使用详情.pdf`，使用 AI 时必含，见 `references/13-AI工具使用规范.md`）
- **停止条件 = Type-A 全过 + 用户验收通过**（含 `solution_audit.py` 与 `evidence_check.py` 全过、每问有全模型结果、全部官方附件存在且合规）。Codex 不得以"我觉得改好了"为由停止。
- **交付口径（只交 2 样）**：① `paper/main.pdf`（PDF 论文）② `materials/`（支撑材料文件夹）；其余中间产物留在过程目录不上交

## 硬性规则

- 每步先读对应 references 再执行；产出严格套用模板结构
- 所有数值结果必须可复现（固定随机种子、保存中间数据、写清运行命令）
- **代码可读性与中文注释**：生成的每个代码文件必须函数化、命名自描述、顶部写明用途/输入/输出；关键公式、物理意义、算法步骤、数据来源用**较详细中文注释**说明（讲「为什么」而非复述代码），见 `references/03-编程实现.md`
- **优化题硬规则**：先理论推导再定义变量与范围（模型按「 max f(x) + s.t. + 大括号约束组」标准式书写，见 `references/15-优化模型表示.md`）；至少枚举两个本质不同范式；额定/上限等硬约束必须进入搜索（可行性优先），不能只做事后判定；代理必须过全模型保真度校准，不得省略决定可行性的物理项；连续 N 轮（默认 3）不可行或理论上界低于目标时切换范式，不在同一范式内加密扫描（详见 `references/02` 与 `references/11`）
- **每问完整性**：每个子问题必须有全模型结果、硬约束判定与官方附件；任一缺失时步骤 8 的 `solution_audit.py --mode deliverable` 必须 FAIL，不得交付
- **运行纪律**：每次实验写入 `code/run_registry.json`，一次只改一个假设；空输出/中断/失败不得计为完成；未完成运行不得命名 `final`；断点续跑依据台账与结果有效性
- **论文里每个数字必须可溯源**：步骤8 用 `scripts/evidence_check.py` 做证据预检（Type-A 门禁）
- **Codex 不得自我宣判"论文合格/完成"**：Type-B 一律由用户判定
- 图表配色专业、灰度可区分（若需打印评审则提供灰度兼容版本）；正确性规则必守，风格规则可商量
- 论文必须匿名（不出现姓名/学校/指导教师），正文（不含参考文献与附录）≤ 30 页，25 页最好
- **AI 工具声明**：论文在参考文献前有「AI工具使用声明」（本 skill 默认「使用 AI」版）；使用 AI 则支撑材料须含 `AI工具使用详情.pdf`（命名固定，含工具/版本/用途/提示方式/采纳与核验）
- **只交付 PDF**：`paper/main.pdf`（参赛提交）+ 支撑材料文件夹（`materials/`）；不再导出 Word（.docx）
- **交付口径 2 样**：PDF 论文 + 支撑材料文件夹（`materials/`）；参考文献 ≥8 条且每条正文有 \\cite，无官网/组委会条目
- A 题优先机理建模：守恒/平衡方程 → 数值求解 → 灵敏度与稳定性分析，避免纯数据拟合
- 论文必须包含**公式推导过程**（禁止只贴最终公式）；全题配技术路线图 + 工作机理示意图；每个已求解子问题默认至少 3 张图（工作机理示意图 + 算法流程图 + 结果图）；图表必须在正文有引导、有解释、有编号引用
- **问题分析必写“总体分析 + 逐问五步法”**：2.1 总体分析（本质归类/核心矛盾与耦合主线/量级观察与风险锁定）+ 每问“机理层为什么”（含数值佐证），禁止只复述求解路线；范式与自查清单见 `references/05-论文写作.md`，骨架见 `templates/paper/main.tex`
- 完成全部 8 步后，向用户输出：终稿路径（PDF）、关键结果摘要、验收契约判定结果、待人工核对的点