# 数学练习卷生成器 Constitution

## Core Principles

### I. 数据准确性优先（NON-NEGOTIABLE）

所有题目数据必须经过人工审核后方可入库。

- 答案字段不允许猜测——无法确定时必须标记为 
ull
- OCR 识别结果必须与原图对比验证
- LLM 解析结果必须经 eview 命令审核后才能入库
- 审核不通过的题目不得进入练习题库

### II. CLI-First 接口

所有功能通过命令行暴露，无 GUI 依赖。

- 输入：文件路径、命令行参数、stdin
- 输出：stdout（人类可读）+ 结构化文件（JSON/Markdown）
- 错误：stderr + 非零退出码
- 支持 JSON 格式输出供脚本调用

### III. 模块化架构

每个功能封装为独立模块，通过明确接口通信。

- extractor：文档读取与 LLM 解析
- database：数据持久化
- paper：练习卷生成
- eview：人工审核
- stats：统计报告
- error_trainer：错题重练

### IV. 可观测性

每个处理阶段记录日志，标识成功/失败/待审核任务。

- 处理日志写入数据库 ProcessingLog 表
- 每日生成统计报告：已处理卷子数、入库题目数、错误率
- 无法自动处理的题目移至"待人工处理"队列

### V. 教育合规性

- 所有题目必须符合教学大纲要求
- 知识点标签与大纲分级一致
- 无超纲内容（除非明确标记）

### VI. 开源工具优先

- 优先使用开源模型和工具，避免商业锁定
- LLM 接口使用 OpenAI 兼容格式，支持多后端切换
- 依赖项必须有开源替代方案

## Additional Constraints

### 技术栈约束

- 语言：Python 3.11+
- 数据库：SQLite（轻量、单文件、适合本地工具）
- PDF 生成：WeasyPrint（HTML→PDF，支持中文）
- DOC 读取：win32com（Windows Word COM，处理旧版 .doc）
- 图片提取：doc→docx→python-docx 转换链

### 数据隐私

- 不存储敏感用户信息
- 仅处理本地数据
- 不上传任何内容到外部服务（LLM API 调用除外）

### 图片处理策略

- DOC 中嵌入的图片通过转换为 docx 后提取
- WMF 格式转换为 PNG 以便 PDF 兼容
- 装饰性图片（<100x100px）过滤
- 图片与题目通过段落位置关联

## Development Workflow

### 处理流水线

.doc 文件
  → win32com 提取文本
  → doc→docx 转换提取图片
  → LLM 结构化解析（可配置模型）
  → 生成 JSON（含图片关联）
  → 人工审核（CLI 交互）
  → 入库（SQLite）

### 质量门禁

1. **解析后**：自动校验 JSON 格式完整性
2. **审核前**：标记答案为 null 的题目为"需人工确认"
3. **入库前**：必须通过 eview 命令确认
4. **生成前**：检查题库题目数量是否满足需求

## Governance

- 本宪法是所有开发决策的最高准则
- 违反宪法的代码不得合并
- 宪法修改需文档化理由并审核
- 复杂度增加必须有明确理由

**Version**: 1.0.0 | **Ratified**: 2026-08-11 | **Last Amended**: 2026-08-11
