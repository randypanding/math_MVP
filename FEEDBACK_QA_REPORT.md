# math_MVP 小学数学卷生成器 · QA 测试报告与修复建议

> 测试时间：2026-08-12  
> 测试范围：一年级～六年级，覆盖 `generate-questions` / `generate` / `query-types` / `query` / `stats` / 默认 `count` 出卷  
> 测试样本：6 份按年级组卷（`data/output/qa/一年级.pdf` 至 `六年级.pdf`），1 份默认 15 题卷，1 次空题型崩溃测试。

---

## 1. 测试执行摘要

我先把仓库 clone 到工作区，创建隔离 venv 安装依赖（`sqlalchemy` / `fpdf2` / `pyyaml` / `pymupdf`），然后执行：

```bash
# 为每个年级按知识点各生成 20 题
for g in 一年级 二年级 三年级 四年级 五年级 六年级; do
  python -m src.cli generate-questions --grade $g -n 20
done

# 出卷测试：只用该年级实际能抽到的题型
python -m src.cli generate --grade $g --title ... --section "口算题:8" ... --with-answer --with-error-tip
```

结果形成题库 **1760 题**（88 个知识点 × 20），并生成了 6 份年级综合卷。

---

## 2. 核心问题总览（按严重性排序）

| 编号 | 问题 | 严重度 | 影响面 |
|------|------|--------|--------|
| A | **生成器只产出 5 种题型，大量声明题型缺失**（`vertical_calculation` 全局为 0） | P0 | 所有年级 |
| B | **题目跨年级污染**：一年级卷子出现六年级内容 | P0 | 低年级尤其严重 |
| C | **题区编号硬编码、跳跃** | P1 | 所有卷子排版 |
| D | `query-types --grade` 参数无效，始终返回全库统计 | P1 | CLI 统计 |
| E | **请求空题型时 `generate` 直接崩溃**（Traceback） | P1 | 用户体验 |
| F | 默认 `count` 模式出卷题型单一 | P2 | 默认使用路径 |
| G | 生成 PDF 时反复报 `MERG NOT subset; don't know how to subset; dropped` | P2 | 日志/字体子集 |

---

## 3. 问题详情

### A. 题型塌缩：`vertical_calculation` 永远为 0，口算题占比 60%～91%

#### 现象

知识点声明了 21 种题型，但实际程序生成只产出 5 种：`mental_arithmetic`（口算题）、`step_calculation`（脱式计算）、`perimeter_area`（周长面积）、`unit_conversion`（单位换算）、`word_problem`（解决问题）。

**各年级实际产出分布（按知识点聚合）：**

| 年级 | 知识点数 | 声明题型数 | 实际产出题型数 | 口算题占比 | 主要缺失的声明题型 |
|------|----------|------------|----------------|------------|--------------------|
| 一年级 | 22 | 13 | 5 | 72.7% | `oral_counting`, `compare_size`, `shape_counting`, `number_read_write`, `number_composition`, `fill_unknown`, `pattern_sequence`, `chart_analysis`, `vertical_calculation` |
| 二年级 | 17 | 14 | 4 | 78.5% | `angle_measurement`, `chart_analysis`, `compare_size`, `composite_expression`, `estimation`, `fill_unknown`, `number_read_write`, `shape_counting`, `vertical_calculation`, `word_problem` |
| 三年级 | 14 | 12 | 3 | 91.1% | `chart_analysis`, `compare_size`, `fill_unknown`, `number_read_write`, `shape_counting`, `unit_conversion`, `verification`, `vertical_calculation`, `word_problem` |
| 四年级 | 14 | 16 | 3 | 90.4% | `chart_analysis`, `compare_size`, `composite_expression`, `estimation`, `fill_unknown`, `number_composition`, `number_read_write`, `shape_counting`, `simplified_calculation`, `unit_conversion`, `verification`, `vertical_calculation`, `word_problem` |
| 五年级 | 11 | 17 | 2 | 90.9% | `chart_analysis`, `compare_size`, `composite_expression`, `fill_unknown`, `math_puzzle`, `number_composition`, `number_read_write`, `pattern_sequence`, `shape_counting`, `simplified_calculation`, `solve_equation`, `step_calculation`, `unit_conversion`, `verification`, `vertical_calculation`, `word_problem` |
| 六年级 | 10 | 10 | 3 | 60.0% | `chart_analysis`, `compare_size`, `number_read_write`, `percentage`, `simplified_calculation`, `solve_equation`, `step_calculation`, `unit_conversion` |

**关键事实：**
- 全库 1760 题中，`vertical_calculation`（竖式计算）**0 题**。
- `perimeter_area` 在 5 个年级出现，但**一年级并未声明该题型**却产出了 40 题。
- 三年级、四年级、五年级 90% 以上是口算题。

#### 根因

在 `src/generator/error_patterns.py:801-827`：

```python
question_type = pattern["applicable_types"][0]
if "应用题" in kp_name or "解决问题" in kp_name:
    question_type = "word_problem"
elif "面积" in kp_name or "周长" in kp_name:
    question_type = "perimeter_area"
elif "单位" in kp_name:
    question_type = "unit_conversion"
```

题型由**易错模式的首个适用题型 + 知识点名称关键词**决定，完全未读取 `knowledge_point["types"]`。

而所有 `PATTERNS` 的 `applicable_types` 中，没有任何一个把 `vertical_calculation` 放在第一位，因此竖式计算永远不会被赋值。

#### 修复建议

1. **优先尊重知识点声明的 `types`**：生成时从 KP 的 `types` 列表中随机（或按声明顺序）选择目标题型，再挑选支持该题型的易错模式与模板。
2. **补全题型模板**：为 `vertical_calculation`、`chart_analysis`、`shape_counting`、`number_read_write`、`compare_size`、`angle_measurement`、`percentage`、`simplified_calculation`、`solve_equation` 等缺失题型增加参数化模板。
3. **调整模板注册表**：确保 `vertical_calculation` 对应模板能产出竖式形式的题干（例如 `用竖式计算：...`）。

---

### B. 题目跨年级/跨学期污染

#### 现象

- **一年级**卷子出现：
  - 「一个半圆半径是 5 厘米，求半圆的周长（π 取 3.14）」——六年级内容。
  - 「判断：圆的半径和周长成什么比例？」——六年级内容。
  - 「一个长方形长 8 厘米，宽 6 厘米，周长和面积分别是多少？」——二年级以上内容。
- **五年级**卷子出现半圆周长题——六年级内容。
- **四年级**卷子主要是 `19+67`、`10+6×7` 这种二三年级难度，未出现「三位数乘两位数」「除数是两位数的除法」等四年级核心题型。
- **三年级**默认 `count` 模式 15 题全部为简单加减法口算，没有 `时分秒` 单位换算、`两位数乘两位数` 等三年级题型。

#### 根因

1. `error_patterns.py` 的模板参数是固定范围，未按 `grade`/`semester` 调整难度与知识点范围。例如 `_tpl_add_carry` 永远在 `25-89` 之间取数，一年级和四年级用的同一套。
2. `_route_patterns` 只按知识点**名称关键词**路由，不区分年级。例如 `长度单位` 和 `公顷和平方千米` 都可能命中同一单位换算模板。
3. 几何模板 `_tpl_rect_perimeter_area` / `_tpl_half_circle` 被所有年级共享，且只与知识点名称中的「面积/周长/圆」相关，不限制年级。

#### 修复建议

1. 为模板函数增加 `grade` / `semester` 参数，根据年级调整数值范围、图形复杂度、是否使用 π/分数/小数。
2. 高年级模板应能产出符合课标的数：四年级三位数×两位数、五年级小数竖式、六年级分数/比例/百分数等。
3. 几何题增加年级白名单：半圆、圆锥、圆柱、梯形面积等应只在对应年级出现。
4. 生成器入口 `generate_for_knowledge_point` 应将 `kp["grade"]` 传入模板选择逻辑。

---

### C. 题区编号硬编码、跳跃

#### 现象

`src/paper/generator.py:222-245` 把题型标题写成固定值：

```python
"mental_arithmetic": "一、口算题",
"vertical_calculation": "二、竖式计算",
"step_calculation": "三、脱式计算",
...
"perimeter_area": "十六、周长面积",
"unit_conversion": "十七、单位换算",
"word_problem": "二十、解决问题",
```

导致实际卷子上出现**不连续的题区编号**：

- 三年级只有 3 个区，却显示「一、口算题」「三、脱式计算」「十六、周长面积」。
- 五年级只有 2 个区，却显示「一、口算题」「十六、周长面积」。

#### 修复建议

在 `_group_by_type` 生成 `sections` 后，按实际出现顺序重新编号：`一、...`、`二、...`、`三、...`。

---

### D. `query-types --grade` 无效

#### 现象

```bash
python -m src.cli query-types --grade 一年级
python -m src.cli query-types --grade 六年级
```

两行输出**完全相同**，均为全库统计（1760 题、口算题 1415 题等）。

#### 根因

`src/cli_main.py:189-194` 中 `cmd_query_types` 直接查询所有已审核题目，未使用 `args.grade`：

```python
questions = repos["question"].query(review_status="approved", limit=100000)
```

#### 修复建议

按 `args.grade` 过滤后再统计；若未传 `--grade`，再返回全库。

---

### E. 请求空题型时 `generate` 直接崩溃

#### 现象

```bash
python -m src.cli generate --grade 二年级 \
  --title "竖式计算专项" \
  --section "竖式计算:5" \
  --output ...
```

输出：

```
错误: 题库中没有符合条件的题目
Traceback (most recent call last):
  File "...", line 57, in generate
    raise ValueError("题库中没有符合条件的题目")
ValueError: 题库中没有符合条件的题目
  警告: 题型 'vertical_calculation' 只有 0 道题，少于请求的 5 道
```

程序以 **Traceback** 形式退出，没有生成任何文件。

#### 根因

1. `src/paper/generator.py` 中如果某题型抽到 0 题，最后直接抛 `ValueError`。
2. CLI 的 `handle_command` 捕获所有异常并打印 traceback。

#### 修复建议

- 行为改为「警告 + 跳过空题型」，生成剩余部分；或至少给用户一个清晰的单条错误信息，不要抛 traceback。
- 在 CLI 解析阶段可预先检查：若 `--section` 请求的题型在该年级题库中数量为 0，给出提示并退出。

---

### F. 默认 `count` 模式出卷题型单一

#### 现象

```bash
python -m src.cli generate --grade 三年级 --count 15 --title "三年级默认15题"
```

生成的一页卷子 15 题**全部是口算题**（简单加减法），没有测量、面积、时分秒等三年级内容。

#### 根因

默认 `count` 模式随机抽题，而由于题型塌缩（问题 A），三年级题库 91.1% 是口算题，自然只能抽到口算题。

#### 修复建议

修复问题 A 后，默认模式应能抽到多样化题目。也可在 `count` 模式下默认按各题型均衡配比抽取。

---

### G. 字体子集化警告 `MERG NOT subset; don't know how to subset; dropped`

#### 现象

每次 `generate` 都会打印两行：

```
MERG NOT subset; don't know how to subset; dropped
MERG NOT subset; don't know how to subset; dropped
```

PDF 仍能正常显示中文，但日志 noisy。

#### 根因

`src/paper/pdf_renderer.py` 使用 `fpdf2` + 系统 CJK 字体，字体子集化（subsetting）阶段被 fonttools 拒绝。可能字体格式或 `uni=True` 用法有关。

#### 修复建议

- 换用已知可子集化的 TTF（如 Noto Sans CJK）或关闭子集化。
- 若不影响显示，可在生成器内捕获/抑制该警告。

---

## 4. 补充观察

### 4.1 答案页内容基本正确

我抽查了 6 份卷子的答案页，口算、脱式、单位换算、周长面积、分数运算、半圆周长等答案与题干均匹配，未发现计算错误。易错点提示与题目所对应的易错模式一致。

### 4.2 同一模板可产生重复题干

六年级卷子中同时出现「1/5 ÷ 1 = ___」两次（第 5、8 题）。建议模板选择/题目入库时增加去重机制（按题干哈希）。

### 4.3 `stats` 工作正常

```
总题数: 1760
  已审核: 1760
  待审核: 0
知识点数: 88
```

### 4.4 依赖声明不一致

`pyproject.toml` 声明依赖 `weasyprint`，但实际 PDF 渲染使用 `fpdf2`（`fpdf`）。建议同步 README 与 `pyproject.toml`，移除未使用的 `weasyprint` 依赖声明。

---

## 5. 建议修复优先级

| 优先级 | 任务 | 预期收益 |
|--------|------|----------|
| P0 | 重写 `error_patterns.py` 的题型选择逻辑，尊重 `knowledge_point["types"]` | 直接解决 A、F，使竖式/应用题/图表/解方程等题型可生成 |
| P0 | 为模板增加 `grade`/`semester` 参数并调整难度/范围 | 解决 B 的跨年级污染和难度错位 |
| P1 | 修复 `_group_by_type` 题区编号 | 解决 C，使卷子排版专业 |
| P1 | 修复 `query-types --grade` | 解决 D，CLI 统计准确 |
| P1 | `generate` 空题型降级为警告而非崩溃 | 解决 E，提升容错 |
| P2 | 补齐缺失题型的模板 + 增加去重 | 完整实现 21 种题型覆盖，减少重复题 |
| P2 | 清理/抑制 `MERG NOT subset` 警告 + 修正 `pyproject.toml` 依赖 | 日志整洁、依赖准确 |

---

## 6. 复现材料位置

- 6 份年级综合卷：`data/output/qa/一年级.pdf` ～ `六年级.pdf`
- 预览图：`data/output/qa/一年级_p1.png` / `_p2.png` 等
- 默认 15 题卷：`data/output/qa/三年级默认15.pdf` / `三年级默认15_p1.png`
- 竖式计算崩溃测试命令：见第 3.E 节

---

*报告由 QA 跑通流程后整理，可用于向开发团队反馈修复。*
