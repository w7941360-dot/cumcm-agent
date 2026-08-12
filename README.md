# cumcm-agent — 国赛数学建模全流程助手（Codex Skill）

全国大学生数学建模竞赛（CUMCM，国赛）全流程自动执行助手：赛题分析 → 建模求解 → 编程实现 → 图表生成 → 论文撰写（LaTeX）→ 编译 PDF + 导出 Word → 证据审计与验收。

## 特点

- **8 步流水线 + 检查点**：每步产出后停下等用户确认/反馈，人工把关
- **A 题（连续/物理类）专项**：物理机制识别、机理建模、数值方法（差分/Crank-Nicolson/有限元）、灵敏度与稳定性分析必做
- **A 题模式库**：内置 2020-2025 A 题统计与三类高频方法包（工程过程控制/几何光学曲面/轨迹覆盖避碰），默认按「解析基线 + 数值仿真 + 约束优化」三层结构推进
- **图表插入时机**：每问默认 2 图（模型流程图+结果图）、按论文章节插入、图前引导图后解释、图注五要素、图/表选择规则
- **双引擎求解与出图**：Python / MATLAB（R2025b）均为一等引擎，可按偏好选用或混合；图表支持专业彩色配色（色盲友好、灰度可区分）
- **门禁分级**：机器可查（Type-A）自动判定，质量判断（Type-B）由用户判定——"可 DRIVE，不可 ACQUIT"
- **证据预检**：防编造数字（`scripts/evidence_check.py`，确定性检查论文数字是否真实存在于结果文件）
- **输入处理**：赛题 PDF 自动提取文本 + 原始数据 xlsx 自动探查（`scripts/process_inputs.py`）
- **双格式交付 + 3 样出口**：Word 论文 + PDF 论文 + 支撑材料文件夹（`materials/`，collect_materials.py 自动收集）
- **自动合规检查**：`compliance_check.py`（摘要≤1页 / 页码页脚中部 / 图表居中 / 每条文献被\\cite / 页边距 / 匿名）
- **断点续跑**：中断后从失败步骤继续

## 安装## 预置功能）

如需更多竞赛模板或辅助预置，可参考下列开源项目。

| 预置功能 |
|---|---|
| 工作流管理（新建科研/竞赛流水线） | 8 步流水线 + 断点续跑（工作区即状态）+ 每步检查点 |
| 选题与数据辅助建模 | 赛题 PDF 自动提取 + xlsx 数据探查（`scripts/process_inputs.py`）+ 多题六维选题评估（`references/01`） |
| 内置 LaTeX 一键编译 | 本地 xelatex（MiKTeX）+ pandoc 导出 Word + `compliance_check.py` 自动合规 |
| 各类竞赛 LaTeX 模板 | CUMCM 模板（`templates/paper/main.tex`）；更多赛事模板见 zhanwen/MathModel、MathModelAgent 模板族 |
| 建模求解引擎 | Python 与 MATLAB（R2025b）双一等引擎，求解与出图一致，可按偏好选用/混合 |

可借鉴的开源预置（按需集成）：
- [mathodology](https://github.com/sweetcornna/mathodology)：9 个分工 subagents（建模/编码/论文/评审/盲评判审）+ 多竞赛 workflow 模板 + 免费文献检索 MCP
- [Meta-model-agent](https://github.com/WuXinbo-bo/Math-model-skills)：7 阶段可审计工作流（明确借鉴了 Modex-MH-Agent 的组织方式）
- [EZ_math_model](https://github.com/woodfishhhh/EZ_math_model)：formal/demo/blocked 交付状态 + chart manifest 质量门
- [mathmodel-skill](https://github.com/handsomeZR-netizen/mathmodel-skill)：10 阶段 + 共享决策日志 + doctor.py 环境诊断，支持 CUMCM/MCM/电工杯
- [zhanwen/MathModel](https://github.com/zhanwen/MathModel)：各赛事 Word/LaTeX 模板、Matlab 教程、算法思维导图

## 安装

放到 Codex 个人技能目录：

```
C:\Users\<你的用户名>\.codex\skills\cumcm-agent\
```

## 使用

对 Codex 说：

> 用 cumcm-agent 跑国赛 A 题全流程，赛题：[贴赛题/传 PDF]

比赛当天流程：输入处理（PDF+xlsx）→ 赛题分析 → 建模（你反馈）→ 编程跑数 → 图表 → 定验收契约 → 论文 → PDF+Word → 证据审计+验收。

## 目录结构

```
cumcm-agent/
├── SKILL.md                      # 主流程：8 步流水线 + 门禁分级 + 断点续跑
├── agents/openai.yaml            # UI 元数据
├── scripts/
│   ├── process_inputs.py         # 赛题 PDF 文本提取 + xlsx 数据探查
│   ├── evidence_check.py         # 论文数字证据预检（防幻觉结果）
│   ├── compliance_check.py       # 论文版式/引用/匿名自动合规检查
│   └── collect_materials.py      # 支撑材料收集器（附录A/B 清单）
├── references/                   # 9 份执行指南（01 赛题分析 ~ 09 数据处理）├── references/                   # 10 份执行指南（01 赛题分析 ~ 10 MATLAB；04 图表规范含插入时机/图表规划/图注五要素）
└── templates/                    # 赛题分析/建模报告/结果/论文tex/验收契约模板
```

## License

MIT License。`scripts/evidence_check.py` 改编自 [ARIS (Auto-claude-code-research-in-sleep)](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) `tools/evidence_check.py`（MIT, Copyright (c) 2026 wanshuiyin）。
