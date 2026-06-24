# 出差报销工具

> 英文名为 `reimbursement-agent-toolkit`，方便 GitHub 克隆、命令行安装和跨 Agent 调用；中文用户看到的产品名统一叫「出差报销工具」。

跨 Agent 可用的报销材料整理工具包。Codex skill 只是其中一个入口，Claude Code、OpenClaw、Hermes 或其他能读文件并运行 Python 脚本的 Agent 也可以使用。

核心目标：用户只需要把报销材料和公司报销表格交给 Agent，Agent 负责识别、归类、逐笔确认、预审、填表和整理附件。第一次配置完成后，下次同一家公司使用时不需要重复上传表格，除非公司模板或规则变了。

![报销整理流程](docs/images/workflow.svg)

## 使用时会先看到什么

出差报销工具现在默认先做启动检查，不会一上来就直接长时间执行。用户只需要把材料发给 Agent，Agent 应先告诉你：

- 报销材料是否已经收到。
- 公司报销 Excel 表格是否已经收到，或者是否可以复用上次配置。
- 公司开票信息和报销规则是否缺失。
- 上传的图片、PDF、Excel 会保存到哪个工作目录。
- 缺少文件时能继续做什么，不能继续做什么。

典型启动检查：

```markdown
## 出差报销整理启动检查

- [x] 报销材料：已收到 18 个文件，保存到 `reimbursement-runs/20260624-153000/raw/`
- [ ] 公司报销表格：未找到，请上传 Excel；如果之前配置过，我可以复用上次模板
- [ ] 公司开票信息：未找到，稍后只问缺失字段
- [x] 输出位置：默认使用 `reimbursement-runs/20260624-153000/`

下一步：请上传公司报销 Excel 表格，或回复“先整理材料，稍后再填表”。
```

## 能解决什么

- 从一堆发票、微信/支付宝付款截图、打车票、火车票、酒店票、PDF 中整理可报销事项。
- 每一笔识别结果都暴露给用户确认，可以修改类别、日期、金额、备注和是否纳入报销。
- 支持不同公司的报销 Excel 模板，通过 `template-map.json` 做字段映射，不把某一家公司的格式写死。
- 支持不同公司的报销规则，通过 `company-profile.yaml` 和 `travel-policy.yaml` 配置，不硬编码补贴金额。
- 检查企业抬头、税号、重复票据、缺附件、日期异常、付款记录缺发票、金额合计异常。
- 输出报销单、附件目录、分类附件文件夹、问题清单和最终结构化 JSON。

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/mkshi77/reimbursement-agent-toolkit.git
cd reimbursement-agent-toolkit
```

### 2. 安装 Python 依赖

```bash
pip install openpyxl pyyaml
```

### 3. 安装到 Codex

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse ".\skills\reimbursement-assistant" "$env:USERPROFILE\.codex\skills\"
```

macOS / Linux：

```bash
mkdir -p ~/.codex/skills
cp -R skills/reimbursement-assistant ~/.codex/skills/
```

重启 Codex 后，`reimbursement-assistant` skill 会被自动发现。

### 4. Claude Code / OpenClaw / Hermes

这些 Agent 不需要 Codex skill 安装步骤。让 Agent 读取：

- `skills/reimbursement-assistant/AGENT.md`
- Claude Code 可优先读取 `skills/reimbursement-assistant/CLAUDE.md`

核心能力都在 `scripts/`、`schemas/`、`references/` 中，不依赖某一个 Agent 平台。

## 如何调用

### 在 Codex 里调用

安装并重启 Codex 后，不需要手动运行脚本，直接在对话里说：

> 使用出差报销工具，我上传了报销材料和公司报销表格，请开始整理。先识别每一笔费用并生成确认表。

也可以直接点名 skill：

> 用 `reimbursement-assistant` 整理这次差旅报销。材料在 `D:\报销材料\6月杭州出差`，公司报销表格在 `D:\公司模板\差旅报销.xlsx`。

Codex 看到“出差报销工具”“reimbursement-assistant”“报销材料”“发票”“付款截图”“公司报销表格”等表达时，会加载这个 skill。

### 在聊天窗口直接发材料

如果 Agent 支持上传附件，用户可以直接把发票、微信截图、PDF、火车票、打车票、公司报销表格发到对话框，然后说：

> 我把报销材料和公司报销表格都发上来了，请开始整理。先给我逐笔确认表，不要直接生成最终报销单。

Agent 应先把附件保存到工作目录，再按 `AGENT.md` 的流程扫描、识别、分类和确认。默认目录结构如下：

```text
reimbursement-runs/YYYYMMDD-HHMMSS/
  raw/          原始上传文件
  materials/    标准化工作副本
  extracted/    识别和结构化结果
  review/       待确认清单和问题清单
  output/       最终报销表和附件包
  session.json  本次运行记录
```

如果你希望保存到指定位置，可以直接说：

> 请把这次报销整理结果保存到 `D:\报销整理\2026年6月杭州出差`。

### 在 Claude Code / OpenClaw / Hermes 里调用

让 Agent 读取通用入口：

```text
skills/reimbursement-assistant/AGENT.md
```

然后说：

> 按 `AGENT.md` 的流程帮我整理报销。我上传了报销材料和公司 Excel 报销表格；如果缺少公司规则，只问我缺失项。

Claude Code 可以优先读取：

```text
skills/reimbursement-assistant/CLAUDE.md
```

### 第一次和第二次调用的区别

第一次使用时，通常需要提供公司报销表格、开票信息和报销规则。Agent 会生成或更新：

- `company-profile.yaml`
- `travel-policy.yaml`
- `template-map.json`

第二次同一家公司使用时，可以直接说：

> 还是用上次的公司配置和报销表格，我这次上传了新的报销材料，请开始整理。

只有公司报销表格、税号、开票信息或补贴规则发生变化时，才需要重新确认。

## 第一次使用前准备

用户至少需要提供：

1. 一份公司报销 Excel 表格，例如 `template.xlsx`。
2. 公司开票信息，例如公司名称、税号、开户行、账号。
3. 公司报销规则，例如补贴标准、是否必须发票、是否需要事前审批。

如果还没有配置文件，可以直接把公司报销表格和规则文档交给 Agent，让它先生成草稿：

> 我把公司报销表格和规则文件发给你了，先帮我配置出差报销工具。不要直接填表，先列出你需要我确认的开票信息、报销规则和表格字段。

配置文件示例在：

- `skills/reimbursement-assistant/assets/examples/company-profile.example.yaml`
- `skills/reimbursement-assistant/assets/examples/travel-policy.example.yaml`
- `skills/reimbursement-assistant/assets/examples/template-map.example.json`

配置完成后，Agent 应保存这些文件。下次同一家公司再次使用时，直接复用配置；只有当用户说“公司表格换了”“补贴规则改了”“税号变了”时才重新确认。

## 日常使用方式

用户不需要记脚本参数。常见有两种材料提供方式。

### 方式一：材料在文件夹里

推荐说法：

> 我把这次报销材料放在 `materials/` 文件夹里，公司报销表格是 `template.xlsx`。请开始帮我整理，先识别并列出每一笔费用让我确认。

或者：

> 帮我整理这个文件夹里的差旅报销：`D:\报销材料\6月杭州出差`。公司报销表格在 `D:\公司模板\差旅报销.xlsx`。如果缺少公司配置，先问我需要确认的信息。

### 方式二：直接在对话里发材料

用户也可以直接在 Agent 对话框、飞书、企业微信等通信软件里发送报销截图、发票 PDF、火车票、打车票和公司报销表格。

推荐说法：

> 我把发票、付款截图和公司报销表格都发到对话里了，请开始整理。先识别每一笔费用，给我一个确认表。

Agent 收到附件后应先把附件保存到工作目录，再按同一套流程处理。用户不需要自己先建 `materials/` 文件夹。

Agent 应该自动执行：

1. 先做启动检查，告诉用户缺什么、默认保存在哪里。
2. 保存上传文件或复制材料文件夹到本次运行目录。
3. 扫描材料文件夹。
4. 识别发票、付款截图、交通票、住宿票、审批材料。
5. 生成逐笔勾选确认清单。
6. 让用户确认异常项、低置信度项和是否纳入报销。
7. 按公司规则预审。
8. 按公司 Excel 报销表格填表。
9. 输出完整报销包。

![逐笔确认面板](docs/images/confirmation-panel.svg)

确认清单会采用复选框形式，方便用户直接回复要纳入、排除或修改哪一笔：

```markdown
## 待确认费用

- [x] R001 | 2026-06-10 | 滴滴出行 | 38.50 元 | 市内交通 | 来源：wechat_01.png | 置信度：0.92
- [ ] R002 | 2026-06-10 | 微信转账 | 200.00 元 | 疑似私人支出 | 来源：wechat_02.png | 建议排除
- [ ] R003 | 2026-06-11 | 酒店 | 420.00 元 | 住宿费 | 来源：hotel.pdf | 税号需确认
```

用户可以直接回复：

> 确认 R001，排除 R002，R003 改成住宿费并纳入。

## Agent 内部命令流

Agent 可按下面命令编排，不要求普通用户手动执行：

```bash
cd skills/reimbursement-assistant

python scripts/prepare_run.py \
  --input MATERIALS_DIR \
  --out-root reimbursement-runs

python scripts/scan_materials.py \
  --input RUN_DIR/materials \
  --output RUN_DIR/extracted/materials.json

python scripts/extract_receipts.py \
  --materials RUN_DIR/extracted/materials.json \
  --output RUN_DIR/extracted/extracted.json

python scripts/classify_expenses.py \
  --input RUN_DIR/extracted/extracted.json \
  --output RUN_DIR/review/classified.json

python scripts/validate_claim.py \
  --input RUN_DIR/review/classified.json \
  --company company-profile.yaml \
  --policy travel-policy.yaml \
  --output RUN_DIR/review/issues.md

python scripts/build_package.py \
  --input RUN_DIR/review/classified.json \
  --materials RUN_DIR/extracted/materials.json \
  --out-dir RUN_DIR/output/package

python scripts/fill_template.py \
  --input RUN_DIR/review/classified.json \
  --template template.xlsx \
  --map template-map.json \
  --output RUN_DIR/output/reimbursement.xlsx
```

如果图片或 PDF 需要视觉识别，Agent 可以先用自己的视觉能力或 OCR 工具抽取记录，再通过 `extract_receipts.py --agent-records records.json` 接入同一套流程。

## 公司报销表格

这里的“模板”就是用户自己公司的报销 Excel 表格。用户第一次上传后，Agent 会学习这个表格里哪些单元格要填申请人、部门、日期、费用明细、合计、银行卡信息等。

`template-map.json` 是 Agent 内部保存的表格位置说明，普通用户不用手写。它的作用是让 Agent 下次能继续填同一张公司表格，不需要用户重复上传。

![模板映射](docs/images/template-mapping.svg)

如果公司没有固定表格，才使用仓库里的示例表格作为默认模板。只要用户已经提供了自己的公司表格，就优先使用用户公司的表格。

公司表格变更时，只需要让 Agent 重新读取新版表格并更新映射：

- 申请人在哪个单元格
- 部门在哪个单元格
- 费用明细从第几行开始
- 金额、类别、发票号、备注分别在哪一列

如果用户已经配置过一次，下次同一家公司使用时可以直接说：

> 这次还是用上次的公司报销表格，材料我已经上传了，请开始整理。

## Don't Make Me Think 原则

- Agent 先做启动检查，明确告诉用户“已收到什么、缺什么、文件保存在哪里、下一步做什么”。
- Agent 自动扫描、识别、归类、列异常，不让用户从空表开始填。
- 每一笔费用都可见，可修改，可排除。
- 明显可报销项默认建议纳入，但仍展示来源和置信度。
- 低置信度、付款记录缺发票、税号不一致、日期不在行程内、疑似私人消费必须提示用户确认。
- 公司规则和表格格式来自用户配置，不写死在 skill 里。

## 仓库结构

```text
skills/reimbursement-assistant/
  SKILL.md                         # Codex skill 入口
  AGENT.md                         # 通用 Agent 入口
  CLAUDE.md                        # Claude Code 入口
  scripts/                         # 可复用脚本
  schemas/                         # 跨 Agent JSON 协议
  references/                      # 工作流、确认规则、分类标准
  assets/examples/                 # 示例公司配置和模板映射
```
