# cumcm-agent — 国赛数学建模全流程助手（Codex Skill）

全国大学生数学建模竞赛（CUMCM，国赛）全流程自动执行助手：赛题分析 → 建模求解 → 编程实现 → 图表生成 → 论文撰写（LaTeX）→ 编译 PDF + 导出 Word → 证据审计与验收。

## 特点

- **8 步流水线 + 检查点**：每步产出后停下等用户确认/反馈，人工把关
- **A 题（连续/物理类）专项**：物理机制识别、机理建模、数值方法（差分/Crank-Nicolson/有限元）、灵敏度与稳定性分析必做
- **门禁分级**：机器可查（Type-A）自动判定，质量判断（Type-B）由用户判定——"可 DRIVE，不可 ACQUIT"
- **证据预检**：防编造数字（`scripts/evidence_check.py`，确定性检查论文数字是否真实存在于结果文件）
- **输入处理**：赛题 PDF 自动提取文本 + 原始数据 xlsx 自动探查（`scripts/process_inputs.py`）
- **双格式交付**：`main.pdf`（参赛提交）+ `main.docx`（pandoc 从 LaTeX 导出 Word）
- **断点续跑**：中断后从失败步骤继续

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
│   └── evidence_check.py         # 论文数字证据预检（防幻觉结果）
├── references/                   # 9 份执行指南（01 赛题分析 ~ 09 数据处理）
└── templates/                    # 赛题分析/建模报告/结果/论文tex/验收契约模板
```

## License

MIT License。`scripts/evidence_check.py` 改编自 [ARIS (Auto-claude-code-research-in-sleep)](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) `tools/evidence_check.py`（MIT, Copyright (c) 2026 wanshuiyin）。