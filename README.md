# Reimbursement Agent Toolkit

跨 Agent 可用的报销材料整理与报销表生成工具包。Codex skill 只是其中一个入口，Claude Code、OpenClaw、Hermes 或其他能读文件并运行脚本的 Agent 也可以使用。

核心目标：用户丢一堆发票、付款截图、打车票、行程单、公司模板进来，Agent 自动整理、归类、填表、查错；用户只确认异常项和低置信度项。

![Workflow](docs/images/workflow.svg)

## 解决的问题

- 从混乱材料中识别发票、交通票、付款记录、审批材料和其他附件。
- 每一笔费用都暴露给用户确认，可修改类别、日期、金额、是否纳入报销。
- 支持不同公司的报销模板，通过 `template-map.json` 适配，不把某一家公司的表格写死。
- 支持不同公司的报销规则，通过 `company-profile.yaml` 和 `travel-policy.yaml` 配置，不硬编码补贴金额。
- 校验企业名称、税号、重复发票、缺附件、日期范围、金额合计和异常项。
- 生成报销单、附件目录、分类附件文件夹和问题清单。

## 工作流

1. 扫描报销材料文件夹。
2. 抽取结构化记录。图片/PDF 可由 Agent 视觉能力或外部 OCR 生成记录。
3. 自动分类费用并给出置信度。
4. 生成逐笔确认清单，用户只修正异常和低置信度项。
5. 按公司规则预审。
6. 按公司模板填表。
7. 输出完整报销包。

![Confirmation](docs/images/confirmation-panel.svg)

## 快速开始

```bash
cd skills/reimbursement-assistant

python scripts/scan_materials.py \
  --input ../../docs/examples/sample-materials \
  --output ../../docs/examples/sample-output/materials.json

python scripts/extract_receipts.py \
  --materials ../../docs/examples/sample-output/materials.json \
  --output ../../docs/examples/sample-output/extracted.json

python scripts/classify_expenses.py \
  --input ../../docs/examples/sample-output/extracted.json \
  --output ../../docs/examples/sample-output/classified.json

python scripts/validate_claim.py \
  --input ../../docs/examples/sample-output/classified.json \
  --company assets/examples/company-profile.example.yaml \
  --policy assets/examples/travel-policy.example.yaml \
  --output ../../docs/examples/sample-output/issues.md

python scripts/build_package.py \
  --input ../../docs/examples/sample-output/classified.json \
  --materials ../../docs/examples/sample-output/materials.json \
  --out-dir ../../docs/examples/sample-output/package
```

## Agent 用法示例

对任何 Agent 说：

> 使用这个 toolkit 帮我整理 `materials/` 里的差旅报销。公司配置在 `company-profile.yaml`，规则在 `travel-policy.yaml`，模板在 `template.xlsx`。

Agent 应执行：

1. 运行 `scan_materials.py`。
2. 对图片、PDF、截图进行视觉/OCR 抽取，写入 `extracted.json`；如果没有视觉能力，保留 `vision_required` 项。
3. 运行 `classify_expenses.py`。
4. 展示每一笔识别结果供用户确认。
5. 运行 `validate_claim.py`。
6. 按 `template-map.json` 运行 `fill_template.py`。
7. 运行 `build_package.py`。

## 第一次配置

准备两类配置：

- 企业信息：`company-profile.yaml`
- 报销规则：`travel-policy.yaml`

如果你的公司报销表不同，上传公司模板 Excel，并创建 `template-map.json`。模板映射示意：

![Template mapping](docs/images/template-mapping.svg)

## 核心原则

- Don't make me think：Agent 先判断、先归类、先列异常，用户只确认必要项。
- 不静默纳入低置信度记录：低置信度、疑似私人消费、缺发票、日期不匹配的记录必须展示。
- 不硬编码公司规则：补贴、限额、模板、企业抬头都来自配置。
- 跨 Agent：脚本和 JSON/YAML 协议是核心，具体 Agent 入口只是薄封装。

## 目录

```text
skills/reimbursement-assistant/
  SKILL.md                         # Codex skill entry
  AGENT.md                         # Universal agent entry
  CLAUDE.md                        # Claude Code entry
  scripts/                         # Reusable deterministic scripts
  schemas/                         # Cross-agent JSON schemas
  references/                      # Workflow and policy references
  assets/examples/                 # Example company config and policy
```

