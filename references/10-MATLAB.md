# 10 MATLAB（R2025b）计算引擎

> 本机已装 MATLAB R2025b（`D:\matlab`），步骤3 编程实现可用 MATLAB 代替 Python（或互补）。
> 已实测：`matlab -batch` 无头运行 粒子群优化 + pdepe 热传导 + PNG 导出 全部成功。

## 检测与调用

### 检测 MATLAB
- `where matlab` 或检查 `D:\matlab\bin\matlab.exe`
- 版本/工具箱：`matlab -batch "v=ver; for k=1:numel(v), fprintf('%s\n', v(k).Name), end"`

### 无头运行 .m 脚本（核心用法）
```
cd <工作目录>
matlab -batch "run('script.m')"
```
- 退出码 0 = 成功；脚本里用 `fprintf` 打印关键结果
- ⚠️ 每次 `-batch` 冷启动约 20~40s（本机实测），**适合整批计算**；多个小任务合并进一个 .m 一次跑完
- 脚本里用 `rng(0)` 固定随机种子，保证可复现（配合 RESULTS.md 记录）

### 已核实可用的工具箱（本机 R2025b）
Optimization、Global Optimization（particleswarm/ga/patternsearch）、Statistics & ML、Symbolic、Curve Fitting、Parallel Computing、Mapping、Image Processing
⚠️ 无 PDE Toolbox → 用内置 `pdepe`（1D 抛物型/双曲型）或自写有限差分（2D/3D）

## A 题常用 MATLAB 函数
| 需求 | 函数 |
|------|------|
| ODE 初值 | `ode45` / `ode15s`（刚性） |
| 1D PDE（热传导/扩散/波动） | `pdepe`（抛物型） |
| 2D/3D 场 | 自写有限差分（Crank-Nicolson 隐式），用稀疏矩阵 `\` 求解 |
| 单目标连续优化 | `fmincon` / `fminunc` |
| 全局优化（多峰/平台效应） | `particleswarm` / `ga` / `patternsearch` / `multistart` |
| 参数辨识 | `lsqcurvefit` / `fitnlm` / `fminsearch` |
| 灵敏度分析 | 循环扰动参数重算；`parfor` 并行（Parallel Toolbox） |
| 数据插值/网格 | `griddata` / `scatteredInterpolant` / `interp1` |
| 统计 | `mean/std/quantile/corrcoef/fitlm` |

## 图导出（对齐 04-图表规范，支持专业彩色）
```matlab
fig = figure('Visible','off');          % 无头模式必须隐藏窗口
% 统一配色（Okabe-Ito 六色，色盲友好）
colors = [0.00 0.45 0.74; 0.85 0.33 0.10; 0.00 0.62 0.45; 0.80 0.47 0.65; 0.94 0.89 0.26; 0.34 0.71 0.91];
plot(x, y1, '-', 'Color', colors(1,:), 'LineWidth', 1.2); hold on;
plot(x, y2, '--', 'Color', colors(2,:), 'LineWidth', 1.2);
xlabel('x (m)'); ylabel('T (°C)'); grid on; set(gca,'FontSize',11);
legend('方案1','方案2','Location','best');
exportgraphics(fig, 'fig_xxx.png', 'Resolution', 300);       % 论文插图用 PNG（≥300 dpi）
```
- **彩色/灰度均可**：默认专业彩色（Okabe-Ito / parula 色板）；若需黑白打印，用线型（实/虚/点）+ 标记区分，并 `colormap(gray)` 预览确认可读
- 热图/曲面：`colormap('parula')` 或 `turbo`；**禁止 jet/rainbow 彩虹色**
- 多组对比用「颜色 + LineStyle + Marker」双编码
- 图内建议英文标签 + 中文图注（避免 MATLAB 中文字体在无头环境缺字体的问题）
- 图统一存 `figures/`，命名 `fig_<内容>.png`（只需 PNG，≥300 dpi）

## 结果输出规范（与 evidence_check 衔接）
- 关键数值写 CSV：`writematrix(result, 'result1.csv')` 或 `writetable`
- RESULTS.md 引用这些文件；步骤8 证据预检用 `evidence_check.py` 核对论文数字
- 结果同时存 `.mat` 便于复算：`save('result1.mat', 'xopt', 'fval')`

## 注意事项
- `matlab -batch` 不支持交互式图窗；所有图 `Visible','off'` + `exportgraphics`
- 长计算可用 `parpool` + `parfor`（Parallel Toolbox 已装）；用完 `delete(gcp('nocreate'))`
- MATLAB 脚本编码用 UTF-8；中文字符串注意 MATLAB 默认编码（必要时用英文变量/注释）
- 与 Python 互补：数据预处理可用 Python（pandas），重计算用 MATLAB；通过 CSV/mat 交换