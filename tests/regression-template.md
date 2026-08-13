# 回归验收模板（通用优化题）

> 用途：skill 修改后，用一道"硬指标 + 设计变量"的优化题重跑流水线，验证优化治理门禁确实生效。
> 所有验收标准**参数化**，不绑定任何具体赛题答案；可复制本模板为 `tests/<题目>-regression.md` 实例（如 `2023A-regression.md`）。
> 实例化时替换占位符：`<P_rated>` 额定指标、`<N_switch>` 不可行轮数、`<预算>` 等。

## 实例信息
- 题目：<年份-题号>
- 额定指标 P_rated：<值+单位>
- 预算上限：<min>
- 阈值：N_switch=<3>，代理排序相关≥<0.9>，目标变化阈值<2%>

## 验收标准（全部通过 = 回归 PASS）
1. **达标**：在预算内，全模型方案达到 `≥ P_rated`（含 ΔP 裕量）
2. **附件合规**：生成的 `resultN.xlsx` 符合官方表头、列序与取值约束（`solution_audit.py --mode deliverable` PASS）
3. **范式多样性**：至少完整评估一个理论推导的非基线范式（非密排/非单机/非同规格）
4. **范式切换**：若前 N_switch 轮搜索不可行，日志（run_registry）显示已返回建模选型并切换范式
5. **代理保真度**：无保真度校准的代理被 `--mode optimization` 拒绝，或补入经过校准的近似
6. **多阶段扩展**：多阶段题的后一问同时尝试自由度扩展（尺寸+高度等），并生成合规结果文件
7. **审计必败用例**：删除某问结果或保留空模板时，`--mode deliverable` 必须 FAIL
8. **台账完整**：所有运行有状态、耗时、唯一假设变化记录（run_registry.json）
9. **高精度复验**：最终可行解在更高精度全模型下复验，并留出误差安全裕量
10. **论文内容完整**：论文含公式推导过程（非只贴最终公式）、全题技术路线图与全题工作机理示意图、每问工作机理示意图与算法流程图（允许全题/每问合并并说明覆盖关系）

## 必败用例（负向测试）
- [ ] 空 `resultN.xlsx`（= 模板副本）→ deliverable FAIL
- [ ] 某问无 `full_model` 入口 → deliverable FAIL
- [ ] 连续 N_switch 轮不可行且未切范式 → optimization FAIL
- [ ] 声明代理但无 surrogate_terms → optimization FAIL
- [ ] 总耗时超预算 → optimization FAIL

## 运行记录
- 重跑日期 / skill 版本：
- 结果：PASS / FAIL（附 `solution_audit.py` 输出与逐条对照）