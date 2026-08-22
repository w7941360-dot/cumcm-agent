# 赛题分析报告

## 1. 问题重述
- 一句话目标：
- 子问题拆解：
  1.
  2.
  3.

## 2. 问题类型判断
- 类型（A 连续 / B 离散 / C 数据）：A
- 判断理由：

## 3. 关键假设
| # | 假设 | 对结果的影响 |
|---|------|-------------|
| 1 |  |  |

## 4. 已知量与待求量
| 名称 | 类型 | 来源 | 说明 |
|------|------|------|------|

## 5. 物理机制分析（A 题）
- 支配过程：
- 候选控制方程：
- 定解条件（初值/边值）：
- 参数来源：

## 6. 初步求解思路
- 路线 1：
- 路线 2：

## 7. 风险与难点
- 每题列出：数据缺失、非线性、计算量、量纲、**该问无可行解时的范式切换预案**（预案缺失 = 步骤 1 审计不通过）

## 8. 子问题全链路矩阵（每问必填，步骤 1 Type-A 门禁）
> 任一列缺失，不得进入步骤 2。总预算必须覆盖全部子问题，后续问题默认预留 ≥20%（可按题调整）。

> 混合模式（engine=python+matlab）：每问引擎（py / matlab / py+matlab）在步骤 1 定死，中途不摇摆。

| 子问题 | 依赖关系 | 建模路线 | 引擎 | 决策变量 | 硬约束（额定/上限/窗口） | 全模型（入口） | 代理模型（入口） | 单次计算成本 | 预算分配(min) | 代码入口 | 结果文件 | 官方模板及列名 | 失败预案 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | - | 机理建模 | py | - | - | code/q1_full.py | code/q1_fast.py | 约 Xs/次 | 120 | code/problem1.py | results/result1.xlsx | attachments/result1 模板：列 A..C | 无解→换截断模型 |

## 9. 官方附件清单（登记题面/官方要求的每个 resultN.xlsx 等）
| 附件名 | 用途 | 模板来源（题面/官方样例） | 表头/列序/取值约束 |
|--------|------|----------------------------|--------------------|
| result1.xlsx | Q1 结果 | 题面附件 | 与官方表头一致 |

## 10. 预算分配
- 总预算（72h 内实际可用于本题的分钟数）：
- 各问预算分配（矩阵中逐问填写）：
- 后续问题预留比例（默认 ≥20%）：
- 单次全模型/代理计算成本与总预算的关系（决定扫描规模与 refine 次数上限）：

## 11. 机器可读 manifest 字段（步骤 1 生成 `plan/solution_manifest.json`）
> 与全链路矩阵一致，供 `scripts/solution_audit.py` 读取；阈值均为默认值可按题调整。

```json
{
  "problem": "<题名>",
  "engine": "matlab | python | python+matlab",
  "rated_targets": {"<指标名>": <额定值>},
  "budget_total_min": <总预算分钟>,
  "thresholds": {
    "surrogate_rank_corr": 0.9,
    "surrogate_delta_pct": 0.02,
    "infeasible_rounds_before_switch": 3,
    "later_question_budget_pct": 0.2
  },
  "subproblems": [
    {
      "id": "Q1",
      "route": "<建模路线>",
      "engine": "python | matlab | python+matlab",
      "decision_variables": ["<变量>"],
      "hard_constraints": ["<硬约束>"],
      "paradigms": ["<范式1>", "<范式2>"],
      "full_model": "code/q1_full.py",
      "surrogate": "code/q1_fast.py",
      "surrogate_terms": ["<代理保留的物理项>"],
      "calibration_samples": <校准样本数>,
      "result_file": "results/result1.xlsx",
      "official_template": "attachments/result1_template.xlsx",
      "budget_min": <该问预算分钟>,
      "fallback": "<失败预案>"
    }
  ]
}
```

## 12. 为论文"问题分析"章节准备的素材（移交步骤 6）
> 步骤 1 顺手产出以下三样素材，步骤 6 写"总体分析"（范式见 `references/05-论文写作.md`）时直接取用：
1. **本质归类**（一句话）：<系统类型 + 落点 + 为什么不能降维>
2. **核心矛盾/耦合主线**（2~4 条）：<每条 = 一句话机理 + 对应建模手段>
3. **量级观察与风险锁定**（用题给数据估算）：<总长/跨度/间隙与尺寸对比/时间尺度 → 预测的关键现象>