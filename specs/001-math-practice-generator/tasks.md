# Tasks: 数学专题练习卷生成器

**Input**: Design documents from `/specs/001-math-practice-generator/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: 不包含测试任务（MVP 阶段）

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan (pyproject.toml, src/, tests/, templates/)
- [ ] T002 Initialize Python project with dependencies (SQLAlchemy, WeasyPrint, Jinja2, PyYAML, python-docx, requests, pymupdf)
- [ ] T003 Create config.yaml template and .env.example
- [ ] T004 Create HTML templates (templates/paper.html, templates/answer.html)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create database models in src/database/models.py (KnowledgePoint, Question, Paper, ErrorSet, ProcessingLog)
- [ ] T006 Create database initialization and repository layer in src/database/repository.py
- [ ] T007 Implement config management in src/config.py (YAML + .env loading)
- [ ] T008 Implement CLI skeleton in src/cli.py (argparse with subcommands)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: US1 — 程序化题目生成 (Priority: P1) MVP

**Goal**: 为1-6年级核心知识点程序化生成题目，构建初始题库（≥5000题）

**Independent Test**: 运行 generate-questions 命令，数据库中有覆盖各年级的题目

### Implementation for US1

- [ ] T09 [P] [US1] Implement QuestionGenerator base class in src/generator/base.py
- [ ] T10 [P] [US1] Implement arithmetic generators (加减乘除口算、竖式、脱式)
- [ ] T11 [P] [US1] Implement number theory generators (数的组成、读写、比大小、规律填数)
- [ ] T12 [P] [US1] Implement geometry generators (图形计数、周长面积)
- [ ] T13 [P] [US1] Implement measurement generators (单位换算、角的度量)
- [ ] T14 [P] [US1] Implement word problem generators (解决问题、数学广角)
- [ ] T15 [P] [US1] Implement knowledge point registry (100+知识点定义)
- [ ] T16 [P] [US1] Implement generate-questions CLI command
- [ ] T17 [US1] Add auto-approval for programmatically generated questions
- [ ] T18 [US1] Implement difficulty assignment logic (1-5级难度自动判定)

**Checkpoint**: 5000+道题目自动入库，覆盖1-6年级核心知识点

---

## Phase 4: US2 — 练习卷生成 (Priority: P1) MVP

**Goal**: 从题库抽题生成 PDF 练习卷，支持多知识点多题型混合

**Independent Test**: 运行 generate 命令，输出包含题目、答案、易错提示的 A4 PDF

### Implementation for US2

- [ ] T19 [P] [US2] Implement PaperGenerator in src/paper/generator.py (选题策略、随机排序)
- [ ] T20 [P] [US2] Implement multi-knowledge-point question selection (按比例分配)
- [ ] T21 [P] [US2] Implement multi-question-type layout (按题型分板块)
- [ ] T22 [P] [US2] Implement PDF renderer in src/paper/pdf_renderer.py (WeasyPrint)
- [ ] T23 [US2] Create paper HTML template in templates/paper.html
- [ ] T24 [US2] Create answer HTML template in templates/answer.html
- [ ] T25 [US2] Implement generate CLI command
- [ ] T26 [US2] Add question count validation (请求题量 > 库存时提示)

**Checkpoint**: 可从题库抽题生成完整 PDF 练习卷

---

## Phase 5: US3 — DOC 文档解析 (Priority: P1)

**Goal**: 从 .doc 卷子提取文本和图片，LLM 结构化解析

**Independent Test**: 运行 extract 命令处理 .doc 文件，输出结构化 JSON

### Implementation for US3

- [ ] T27 [P] [US3] Implement DOC text extraction in src/extractor/doc_reader.py (win32com)
- [ ] T28 [P] [US3] Implement image extraction (doc→docx→python-docx conversion)
- [ ] T29 [P] [US3] Implement WMF to PNG conversion for image compatibility
- [ ] T30 [US3] Implement LLM parser interface in src/extractor/llm_parser.py (OpenAI compatible)
- [ ] T31 [US3] Implement extract CLI command
- [ ] T32 [US3] Implement batch CLI command

**Checkpoint**: 可从 .doc 卷子提取题目并结构化解析

---

## Phase 6: US4 — 题库审核与管理 (Priority: P2)

**Goal**: 支持查看、搜索、修改已入库题目

**Independent Test**: 运行 query 命令搜索题目，运行 review 命令交互式审核

### Implementation for US4

- [ ] T33 [P] [US4] Implement query CLI command (按知识点/年级/难度/题型筛选)
- [ ] T34 [P] [US4] Implement interactive review mode in src/review/cli_review.py
- [ ] T35 [US4] Implement question update functionality in repository layer
- [ ] T36 [US4] Add review status management (pending/approved/rejected)

**Checkpoint**: 可搜索和审核题库题目

---

## Phase 7: US5 — 错题重练 (Priority: P2)

**Goal**: 导入错题图片，生成错题专项练习

**Independent Test**: 导入错题图片，运行 error-practice 生成专项练习 PDF

### Implementation for US5

- [ ] T37 [P] [US5] Implement ErrorSet model operations in repository layer
- [ ] T38 [P] [US5] Implement import-error CLI command (图片 OCR + 手动录入)
- [ ] T39 [US5] Implement error-practice CLI command (仅从错题集抽题)

**Checkpoint**: 可导入错题并生成专项练习

---

## Phase 8: US6 — 统计报告 (Priority: P3)

**Goal**: 显示题库统计信息和使用报告

**Independent Test**: 运行 stats 命令显示完整统计信息

### Implementation for US6

- [ ] T40 [P] [US6] Implement stats calculation in src/stats/reports.py
- [ ] T41 [P] [US6] Implement stats CLI command
- [ ] T42 [US6] Implement ProcessingLog recording in extract/batch commands

**Checkpoint**: 可查看完整统计报告

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T43 [P] Add structured logging throughout the application
- [ ] T44 [P] Write README.md with installation and usage guide
- [ ] T45 End-to-end validation with real .doc files
- [ ] T46 Generate sample PDF outputs (10 example papers)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 (Phase 3) can start after Foundational
  - US2 (Phase 4) depends on US1 (needs questions in DB)
  - US3 (Phase 5) independent of other stories
  - US4 (Phase 6) can run in parallel with US1/US2/US3 after Foundational
  - US5 (Phase 7) depends on US4 + US2
  - US6 (Phase 8) depends on US4

### User Story Dependencies

```
Foundational ──→ US1 (generate questions) ──→ US2 (PDF generation)
             ├──→ US3 (doc extraction, independent) 
             ├──→ US4 (query & review) ──→ US5 (error practice)
             │                         └──→ US6 (stats)
```

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- After Foundational: US1, US3, US4 can run in parallel
- US2 depends on US1 completion
- US5 depends on US2 + US4
- US6 depends on US4

---

## Implementation Strategy

### MVP First (Phases 1-5)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: US1 (generate 5000+ questions)
4. Complete Phase 4: US2 (PDF generation)
5. Complete Phase 5: US3 (doc extraction)
6. **STOP and VALIDATE**: Generate first practice paper PDF
7. If MVP works → continue with Phases 6-9

### Incremental Delivery

After MVP validation:
8. Phase 6: US4 (query & review)
9. Phase 7: US5 (error practice)
10. Phase 8: US6 (stats)
11. Phase 9: Polish

---

## Parallel Example: Phase 3 (US1)

```bash
# Launch all parallel generator tasks together:
Task T09: Implement QuestionGenerator base class
Task T10: Implement arithmetic generators
Task T11: Implement number theory generators
Task T12: Implement geometry generators
Task T13: Implement measurement generators
Task T14: Implement word problem generators
Task T15: Implement knowledge point registry

# After all generators complete:
Task T16: Implement generate-questions CLI command
Task T17: Add auto-approval logic
Task T18: Implement difficulty assignment
```
