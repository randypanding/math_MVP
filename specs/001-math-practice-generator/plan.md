# Implementation Plan: 数学专题练习卷生成器

**Branch**: `001-math-practice-generator` | **Date**: 2026-08-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-math-practice-generator/spec.md`

## Summary

构建一个 CLI 工具，覆盖小学 1-6 年级数学核心知识点（100+知识点），支持 20+ 种题型的程序化生成，同时支持从 .doc 卷子提取题目，最终生成可打印的 PDF 练习卷。初始题库通过程序化生成构建（≥5000题），后续通过卷子解析扩展。

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: 
- `win32com`（读取 .doc 文件）
- `python-docx`（从转换后的 docx 提取图片）
- `pymupdf`（PDF 页面转图片、PDF 读取）
- `SQLAlchemy` + `sqlite3`（数据存储）
- `WeasyPrint`（PDF 生成）
- `Jinja2`（HTML 模板渲染）
- `PyYAML`（配置文件）
- `requests`（LLM API 调用）

**Storage**: SQLite（单文件数据库 `data/mathgen.db`）

**Testing**: pytest

**Target Platform**: Windows 10/11（依赖 Word COM 组件）

**Project Type**: CLI application（命令行工具）

**Performance Goals**:
- 程序化生成速度 ≥ 100题/秒
- 单份卷子处理时间 < 30 秒（不含人工审核）
- PDF 生成时间 < 10 秒（50题）
- 支持 200+ 文件批量处理

**Constraints**:
- 依赖 Microsoft Word（COM 自动化）
- LLM 调用需要网络连接
- 图片题需额外处理时间

**Scale/Scope**:
- 知识点：100+（覆盖 1-6 年级）
- 题型：20+（数与代数、几何与量、统计与解决问题）
- 初始题库：≥5000 道题（程序化生成）
- 目标题库：≥10000 道题（含卷子提取）
- 单份 PDF：20-100 题

## Constitution Check

### Simplicity Gate (Article VII)
- [x] Using ≤3 projects（单项目结构）
- [x] No future-proofing（MVP 优先，不过度设计）

### Anti-Abstraction Gate (Article VIII)
- [x] Using framework directly（直接使用 SQLAlchemy、Jinja2）
- [x] Single model representation（无冗余抽象层）

### Integration-First Gate (Article IX)
- [x] Contracts defined（模块接口明确）
- [x] Contract tests written（核心模块有测试）

## Project Structure

### Documentation (this feature)

```text
specs/001-math-practice-generator/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
├── spec.md              # Spec input
├── tasks.md             # Phase 2 output
└── checklists/          # Quality checklists
```

### Source Code (repository root)

```text
math-practice-generator/
├── src/
│   ├── __init__.py
│   ├── cli.py                    # CLI 入口（argparse）
│   ├── config.py                 # 配置管理
│   ├── generator/
│   │   ├── __init__.py
│   │   ├── base.py              # 题目生成器基类
│   │   ├── arithmetic.py        # 算术类题目生成
│   │   ├── number_theory.py     # 数的认识类生成
│   │   ├── geometry.py          # 几何类题目生成
│   │   ├── measurement.py       # 量与计量类生成
│   │   ├── word_problem.py      # 解决问题类生成
│   │   └── knowledge_points.py  # 知识点注册表(100+)
│   ├── extractor/
│   │   ├── __init__.py
│   │   ├── doc_reader.py        # .doc 文本+图片提取
│   │   └── llm_parser.py        # LLM 结构化解析
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py            # ORM 模型
│   │   └── repository.py        # 数据访问层
│   ├── paper/
│   │   ├── __init__.py
│   │   ├── generator.py         # 组卷逻辑
│   │   └── pdf_renderer.py      # PDF 渲染
│   ├── review/
│   │   ├── __init__.py
│   │   └── cli_review.py        # 交互式审核
│   ├── stats/
│   │   ├── __init__.py
│   │   └── reports.py           # 统计报告
│   └── error_trainer/
│       ├── __init__.py
│       └── error_set.py         # 错题重练
├── templates/
│   ├── paper.html               # 练习卷模板
│   └── answer.html              # 答案页模板
├── config.yaml                  # 配置文件
├── .env.example                 # API Key 模板
├── data/
│   ├── raw/                     # 原始 .doc
│   ├── images/                  # 提取的图片
│   ├── processed/               # LLM JSON
│   └── output/                  # PDF 输出
├── tests/
│   ├── conftest.py
│   ├── test_generators.py
│   ├── test_doc_reader.py
│   ├── test_llm_parser.py
│   ├── test_paper_generator.py
│   └── test_pdf_renderer.py
├── pyproject.toml
└── README.md
```

**Structure Decision**: 单项目结构，所有源码在 `src/` 下按功能模块划分。generator 模块按题型类别拆分为多个文件，支持 20+ 种题型的灵活扩展。

## Complexity Tracking

无宪法检查违规项。
