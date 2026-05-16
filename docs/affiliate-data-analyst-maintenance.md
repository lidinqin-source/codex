# Affiliate Data Analyst 维护指南

## 目的

这个仓库用于维护可复用的 affiliate reporting skill，不用于保存每一次本地报告运行的全部产物。维护目标是让 skill 保持小、清晰、可审计，并且能适配不同市场、不同周期和不同平台。

## 提交规则

默认应该提交：

- `.agents/skills/affiliate-data-analyst/SKILL.md`
- `.agents/skills/affiliate-data-analyst/agents/`
- `.agents/skills/affiliate-data-analyst/assets/`
- `.agents/skills/affiliate-data-analyst/references/`
- `requirements.txt`
- `.gitignore`
- `docs/`

默认不要提交：

- `affiliate_reports/`
- `reports/`
- `output/`
- 顶层 `scripts/`
- 顶层临时参考文件，例如 `goal-pacing.md`
- 任何凭证、token、浏览器 session、原始平台导出、缓存文件

如果某个报告产物必须作为审计证据保存，需要显式使用 `git add -f <path>`，并在 commit message 里说明为什么这个产物值得进入版本库。

## 安全 Git 流程

这个仓库不要使用 `git add .`。原因是本地经常会生成报告、截图、脚本和数据文件，直接全量 add 容易误提交。

推荐流程：

```bash
git status --short --untracked-files=all
git add .agents/skills/affiliate-data-analyst requirements.txt .gitignore docs/affiliate-data-analyst-maintenance.md
git status --short
git commit -m "Maintain affiliate data analyst skill"
```

push 前先看 staged diff：

```bash
git diff --cached --stat
git diff --cached
git push origin main
```

## Skill 修改检查表

修改前先判断任务层级：

- L0：快速解释、只读查看、方向判断。
- L1：轻量本地文件修改。
- L2：报告逻辑、数据源规则、验证行为。
- L3：生产报告生成或最终 HTML 报告 QA。

如果是 L2/L3 修改，要确认这些规则没有被破坏：

- L2/L3 的第一个用户侧 todo 应该是 blocking-scope gate，而不是 source exploration。
- 生产月报、周报、日报如果缺时间范围，必须先用绝对日期向用户确认，不能用旧目录或旧脚本自动决定范围。
- L2/L3 需要用户选择时，Codex App Server `tool/requestUserInput` / `request_user_input` 必须作为 required capability 接受可用性检查；未暴露时停止，不能默认降级成 Markdown 问题，也不要在 `agents/openai.yaml` 里伪造 unsupported dependency schema。
- 生产任务开始前必须做 Tool Availability Preflight。
- 必需工具不可用时，最多尝试修复 3 次；仍不可用就停止并告知用户。
- 不能用手工估算、替代工具或弱证据绕过必需 source tool。
- L2/L3 要使用 `requirement-checker` 做需求覆盖核验。
- `browser:browser` 是生产 HTML QA 工具。
- Playwright 可以辅助调试，但不是 L3 生产 QA 的 fallback。
- `report_bundle.json` 命名规则保持统一：`report_title`、`report`、`report.source_files`。

## 平台上下文维护

平台规则应该放在 references 里，不要散落在主流程里：

- `references/platform-context.md`：平台上线时间、0 行数据解释、平台 caveat。
- `references/codex-question-tool.md`：Question Tool 的官方能力边界和 fallback 规则。
- `references/impact-actions-standard.md`：Impact Actions 拉数和 reconciliation 规则。
- `references/measurement-contract.md`：指标定义和对账口径。
- `references/reconciliation-and-artifacts.md`：产物要求和证据打包规则。
- `references/weekly-report-standard.md`：周报周期的输出标准。
- `references/goal-pacing.md`：目标和 pacing 逻辑。

CJ、Impact、TradeDoubler、GA4 或 Google Sheets 的行为如果变化，优先更新对应 reference。只有当主流程必须强制执行某条规则时，才把最小必要规则写进 `SKILL.md`。

## Runtime 维护

Python 依赖统一维护在 `requirements.txt`。不要假设 Codex 环境或系统 Python 已经安装 GA4 / Google API 相关包。

本地验证环境：

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

如果这个仓库后续用于自动化 Codex 环境，需要补一个专门的 local environment setup step，在生产任务前安装 `requirements.txt`。

## 审计命令

每次 skill 维护完成后，建议跑：

```bash
git status --short --untracked-files=all
rg -n "coupon|orderCoupon|KOL|Codex bundled Python|lookup/|docs/weekly-report-standard|must not directly connect|analyze data by yourself|Playwright fallback|single US monthly|canonical status|one-off script" .agents/skills/affiliate-data-analyst --glob '!**/run-log.md'
find .agents/skills/affiliate-data-analyst -name '.DS_Store' -print
python3 -m py_compile scripts/*.py 2>/dev/null || true
```

`rg` 命令不应该命中 active rule。历史 `run-log.md` 里可能保留旧事故语言，除非历史事实本身写错，否则不要为了“清爽”重写历史。

## 报告产物如何进入版本库

生成的报告默认被 `.gitignore` 忽略，因为它们可能包含订单级商业数据和一次性运行证据。

只有同时满足这些条件时，才考虑提交报告产物：

- 用户明确要求保存到版本库。
- 已检查原始行级数据和敏感字段。
- 这个产物对后续复盘或复用有价值，不只是一次本地运行结果。
- commit message 写清楚市场、时间范围、周期和提交原因。

优先把可复用规则沉淀到 skill references，不要把一次性报告产物当作长期标准。
