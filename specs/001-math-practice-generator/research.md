# Research: 数学专题练习卷生成器

## 决策记录

### 1. DOC 文件读取方案

**Decision**: 使用 `win32com.client` 通过 Word COM 自动化读取 .doc 文件

**Rationale**: 
- .doc 是 Word 97-2003 二进制格式，需要 Word 软件解析
- win32com 可直接调用本地 Word 应用，兼容性最好
- 支持文本提取和图片提取（通过另存为 .docx）

**Alternatives considered**:
- `antiword`：仅 Linux，不支持 Windows
- `python-docx2txt`：仅支持 .docx，不支持 .doc
- ` LibreOffice` 命令行：需要额外安装，COM 更直接

### 2. 图片提取方案

**Decision**: doc → docx 转换 → python-docx 提取图片

**Rationale**:
- 已验证可行：测试文档成功提取 49 张图片
- python-docx 可从 docx 的 media 目录提取图片
- WMF 格式需转换为 PNG（使用 Pillow）

**Alternatives considered**:
- 直接从 doc 提取：COM 的 InlineShapes.Export 方法不稳定
- 截图方式：精度低，不可靠

### 3. LLM 接口方案

**Decision**: OpenAI 兼容 API 格式，支持多后端

**Rationale**:
- 通义千问、DeepSeek、OpenAI 都支持兼容接口
- 通过配置文件切换，无需修改代码
- 使用 `requests` 库直接调用，无需额外依赖

**Alternatives considered**:
- 使用官方 SDK：增加依赖，绑定特定厂商
- LangChain：过度抽象，不适合 CLI 工具

### 4. PDF 生成方案

**Decision**: WeasyPrint + Jinja2 HTML 模板

**Rationale**:
- WeasyPrint 支持中文，CSS 控制精确
- HTML 模板易于维护和修改
- 支持 A4 页面格式、页眉页脚

**Alternatives considered**:
- ReportLab：编程式生成，模板维护困难
- pdfkit (wkhtmltopdf)：需要额外二进制，WeasyPrint 纯 Python

### 5. 题目生成策略

**Decision**: 程序化生成 + 卷子提取双轨并行

**Rationale**:
- MVP 阶段程序化生成 100以内加减法题目，快速验证流程
- 后续通过 OCR + LLM 从卷子提取更多题目
- 程序化生成可保证题目质量和答案准确

**Alternatives considered**:
- 仅依赖卷子提取：启动慢，初始题库为空
- 手动录入：效率低，不适合大量题目

### 6. 数据库方案

**Decision**: SQLite + SQLAlchemy ORM

**Rationale**:
- SQLite 单文件、零配置，适合本地工具
- SQLAlchemy 提供 ORM，简化数据操作
- 后续可迁移到 PostgreSQL（如需）

**Alternatives considered**:
- 纯 SQLite3：代码冗长，易错
- MongoDB：不适合结构化题目数据
