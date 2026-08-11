# 小学数学专题练习卷生成器

基于 Spec-Driven Development (SDD) 方法论开发的小学数学练习卷自动生成工具。

## 功能特性

- **程序化题目生成**：覆盖 1-6 年级 88 个知识点，21 种题型
- **PDF 练习卷生成**：自动生成可打印的 A4 格式练习卷（含答案和易错提示）
- **DOC 卷子解析**：从 .doc 格式卷子提取题目（支持图片提取）
- **LLM 智能解析**：调用 LLM 自动解析卷子文本为结构化题目
- **题库管理**：搜索、审核、修改题目
- **错题重练**：导入错题图片，生成专项练习
- **统计报告**：题库概况、题型分布、年级分布

## 支持的题型（21种）

### 数与代数（14种）
口算题、竖式计算、脱式计算、填未知数、数的组成、数的读写、比大小、规律填数、验算题、估算题、简便计算、列综合算式、解方程、百分数/折扣/税率

### 几何与量（4种）
图形计数、周长面积计算、单位换算、角的度量

### 统计与解决问题（3种）
统计图表分析、解决问题、数学广角

## 安装

### 前置条件
- Python 3.11+
- Microsoft Word（用于 .doc 文件读取）

### 安装步骤

```bash
# 克隆项目
cd math-practice-generator

# 安装依赖
pip install -e .

# 配置 API Key（可选，用于 LLM 解析）
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

## 使用方法

### 1. 生成题目（程序化）

```bash
# 生成所有知识点题目
mathgen generate-questions --all

# 按年级生成
mathgen generate-questions --grade 二年级

# 按知识点生成
mathgen generate-questions --kp "100以内进位加法" -n 50
```

### 2. 生成练习卷

```bash
# 单知识点练习卷
mathgen generate --kp "100以内进位加法" -n 20 --with-answer

# 多知识点混合
mathgen generate --kp "100以内进位加法,100以内退位减法" -n 30

# 按年级出卷
mathgen generate --grade 二年级 -n 50 --with-answer --with-error-tip

# 指定题型
mathgen generate --kp "表内乘法" --type "mental_arithmetic,vertical_calculation" -n 50
```

### 3. 从卷子提取题目

```bash
# 处理单个文件
mathgen extract 试卷.doc

# 批量处理
mathgen batch 试卷文件夹/

# 审核提取结果
mathgen review
```

### 4. 查询题库

```bash
# 按知识点查询
mathgen query --kp "进位加法" --limit 10

# 按年级查询
mathgen query --grade 二年级 --type mental_arithmetic

# JSON 格式输出
mathgen query --kp "进位加法" --json
```

### 5. 统计报告

```bash
mathgen stats
```

### 6. 错题重练

```bash
# 导入错题图片
mathgen import-error 错题.png

# 生成错题专项练习
mathgen error-practice -n 20
```

### 7. 配置管理

```bash
# 查看配置
mathgen config show

# 设置模型
mathgen config set-model deepseek-chat
```

## 项目结构

```
math-practice-generator/
├── src/
│   ├── cli.py                    # CLI 入口
│   ├── cli_main.py               # 命令处理
│   ├── config.py                 # 配置管理
│   ├── generator/                # 题目生成器
│   │   ├── base.py               # 基类
│   │   ├── arithmetic_100.py     # 算术类生成器
│   │   └── knowledge_points.py   # 知识点注册表
│   ├── extractor/                # 文档解析
│   │   ├── doc_reader.py         # DOC 读取
│   │   └── llm_parser.py         # LLM 解析
│   ├── database/                 # 数据层
│   │   ├── models.py             # ORM 模型
│   │   └── repository.py         # 仓库层
│   ├── paper/                    # 练习卷生成
│   │   ├── generator.py          # 组卷逻辑
│   │   └── pdf_renderer.py       # PDF 渲染
│   ├── review/                   # 审核模块
│   ├── stats/                    # 统计模块
│   └── error_trainer/            # 错题重练
├── templates/                    # HTML 模板
├── data/                         # 数据目录
│   ├── mathgen.db                # SQLite 数据库
│   ├── raw/                      # 原始卷子
│   ├── images/                   # 提取的图片
│   ├── processed/                # 处理结果
│   └── output/                   # 生成的 PDF
├── config.yaml                   # 配置文件
├── .env.example                  # API Key 模板
└── pyproject.toml                # 项目配置
```

## 技术栈

| 组件 | 选择 |
|------|------|
| 语言 | Python 3.11+ |
| 数据库 | SQLite + SQLAlchemy |
| PDF 生成 | fpdf2（纯 Python） |
| DOC 读取 | win32com（Word COM） |
| LLM | OpenAI 兼容 API |
| 配置 | YAML + .env |

## 知识点覆盖

| 年级 | 知识点数 | 核心内容 |
|------|---------|----------|
| 一年级（上+下） | 15 | 1-100数的认识、加减法、人民币 |
| 二年级（上+下） | 16 | 100以内加减法、乘除法、混合运算 |
| 三年级（上+下） | 15 | 万以内加减法、倍数、分数小数初步 |
| 四年级（上+下） | 16 | 大数、乘除法、小数、三角形 |
| 五年级（上+下） | 13 | 小数乘除法、方程、分数加减法 |
| 六年级（上+下） | 13 | 分数乘除法、比、圆、百分数 |

## 开发流程

本项目遵循 Spec-Driven Development (SDD) 方法论：

1. **Constitution** - 定义项目宪法（`.specify/memory/constitution.md`）
2. **Specify** - 创建功能规格（`specs/001-math-practice-generator/spec.md`）
3. **Plan** - 制定技术计划（`specs/001-math-practice-generator/plan.md`）
4. **Tasks** - 生成任务列表（`specs/001-math-practice-generator/tasks.md`）
5. **Implement** - 执行实现

## License

MIT
