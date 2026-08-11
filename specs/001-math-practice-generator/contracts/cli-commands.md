# CLI Command Contracts

## Command: `mathgen extract`

解析单个 .doc 文件，提取文本和图片，调用 LLM 结构化解析。

**Input**: 
- `<file>` (positional, required): .doc 文件路径

**Output**:
- JSON 文件（`data/processed/<basename>.json`）
- 图片文件（`data/images/<basename>_<index>.png`）

**Exit Codes**:
- 0: 成功
- 1: 文件不存在或格式错误
- 2: LLM API 调用失败

**Example**:
```bash
mathgen extract "path/to/试卷.doc"
```

---

## Command: `mathgen batch`

批量处理文件夹中的所有 .doc 文件。

**Input**:
- `<folder>` (positional, required): 文件夹路径
- `--recursive` (flag): 递归子文件夹

**Output**:
- 每个文件对应的 JSON
- 处理摘要（成功/失败统计）

**Exit Codes**:
- 0: 全部成功
- 1: 部分失败
- 2: 全部失败

---

## Command: `mathgen review`

进入交互式审核模式，逐题确认或修改。

**Input**:
- `--status pending` (filter): 只显示待审核题目
- `--kp <知识点>` (filter): 按知识点筛选

**Output**:
- 数据库更新（审核状态变更）

**Interactive Flow**:
1. 显示题目文本、答案、知识点
2. 用户选择：确认(c) / 编辑(e) / 跳过(s) / 退出(q)
3. 编辑模式：可修改答案、易错点、知识点

---

## Command: `mathgen query`

查询题库中的题目。

**Input**:
- `--kp <知识点>`: 按知识点筛选
- `--difficulty <1-5>`: 按难度筛选
- `--type <题型>`: 按题型筛选
- `--limit <N>`: 返回数量限制
- `--json`: JSON 格式输出

**Output**:
- 题目列表（表格或 JSON 格式）

---

## Command: `mathgen generate`

生成练习卷 PDF。

**Input**:
- `--kp <知识点>`: 知识点（required）
- `-n <题量>`: 题目数量（default: 50）
- `--with-answer`: 包含答案页
- `--with-error-tip`: 包含易错提示
- `--output <path>`: 输出路径
- `--title <标题>`: 练习卷标题

**Output**:
- PDF 文件

**Exit Codes**:
- 0: 成功
- 1: 题库题目不足
- 2: PDF 生成失败

---

## Command: `mathgen import-error`

导入错题图片，OCR 识别后加入错题集。

**Input**:
- `<image>`: 图片文件路径

**Output**:
- 错题记录（加入 ErrorSet 表）

---

## Command: `mathgen error-practice`

基于错题集生成专项练习。

**Input**:
- `-n <题量>`: 题目数量
- `--output <path>`: 输出路径

**Output**:
- PDF 文件（仅从错题集抽题）

---

## Command: `mathgen stats`

显示题库统计报告。

**Input**:
- `--format text|json`: 输出格式

**Output**:
- 题库概况（总题数、知识点分布、难度分布）
- 处理统计（已处理卷子数、成功率）

---

## Command: `mathgen config`

配置管理。

**Input**:
- `set-model <name>`: 设置 LLM 模型
- `set-api-key <key>`: 设置 API Key
- `show`: 显示当前配置

**Output**:
- 配置更新确认
