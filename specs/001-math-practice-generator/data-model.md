# Data Model: 数学专题练习卷生成器

## 实体关系图

```
KnowledgePoint (1) ─── (N) Question (1) ─── (N) PaperQuestion (N) ─── (1) Paper
                                │
                                └──── (1) ErrorSet
                                
Material (1) ─── (N) Question
ProcessingLog
```

## 实体定义

### KnowledgePoint（知识点）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | String | PK | 知识点编号，如 "G2U03KP01" |
| name | String | NOT NULL | 知识点名称，如 "100以内进位加法" |
| grade | String | NOT NULL | 年级，如 "二年级" |
| semester | String | NOT NULL | 学期，如 "上册" |
| unit | String | | 所属单元 |
| parent_id | String | FK → KnowledgePoint.id | 父知识点（支持层级） |
| question_types | JSON | | 该知识点支持的题型列表 |
| difficulty_range | JSON | | 难度范围，如 [1, 3] |

**索引**: `grade`, `semester`, `parent_id`

**预置数据**: 100+ 知识点，覆盖 1-6 年级

### Question（题目）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 自增主键 |
| knowledge_point_id | String | FK → KnowledgePoint.id | 关联知识点 |
| question_type | String | NOT NULL | 题型（20+种） |
| stem | String | NOT NULL | 题目文本 |
| answer | String | | 答案（NULL=待确认） |
| solution | String | | 解题步骤 |
| common_error | String | | 易错点分析（兼容文案） |
| error_category | String | | 错误类别：conceptual/semantic/calculation/missing_step/logic/procedural |
| error_category_label | String | | 错误类别中文名 |
| pattern_id | String | | 易错模式ID（如 carry_omitted） |
| pattern_name | String | | 易错模式名（如 进位遗忘） |
| pattern_level | String | | 层级：computation_error 计算性错误 / misconception 概念性误解 |
| theme | String | | 主题（arithmetic/fraction/...） |
| theme_label | String | | 主题中文名 |
| wrong_rule | String | | 错误规则（学生常见做法） |
| correct_rule | String | | 正确规则 |
| wrong_value | String | | 常见错误答案 |
| error_step | String | | 错误插入点（第几步易错） |
| steps | String(JSON) | | 逐步解题步骤，含 is_error_point 标记 |
| wrong_path | String(JSON) | | 学生错误路径步骤 |
| socratic_hints | String(JSON) | | 苏格拉底式引导性追问（逐级提示） |
| distractor_mapping | String(JSON) | | 干扰项→误解维度映射 |
| solution_status | String | | 反馈针对性：targeted/optimal/suboptimal/wrong |
| enhanced_explanation | Bool | | 难点主题（分数/比例）是否需更详细解析 |
| difficulty | Integer | 1-5 | 难度等级 |
| source | String | | 来源（程序生成/卷子文件名） |
| image_path | String | | 关联图片路径 |
| image_required | Boolean | DEFAULT FALSE | 是否需要图片辅助 |
| review_status | String | DEFAULT "pending" | 审核状态：pending/approved/rejected |
| created_at | DateTime | DEFAULT NOW | 创建时间 |

**索引**: `knowledge_point_id`, `review_status`, `difficulty`, `question_type`

### Paper（练习卷）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 自增主键 |
| title | String | NOT NULL | 练习卷标题 |
| parameters | JSON | | 生成参数（知识点、题量、题型等） |
| question_ids | JSON | NOT NULL | 题目ID列表（有序） |
| pdf_path | String | | 输出 PDF 路径 |
| created_at | DateTime | DEFAULT NOW | 生成时间 |

### ErrorSet（错题集）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 自增主键 |
| question_id | Integer | FK → Question.id | 关联题目 |
| source_image | String | | 错题来源图片路径 |
| added_at | DateTime | DEFAULT NOW | 加入时间 |
| review_count | Integer | DEFAULT 0 | 练习次数 |
| last_reviewed | DateTime | | 最后练习时间 |

### ProcessingLog（处理日志）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO | 自增主键 |
| file_name | String | NOT NULL | 处理文件名 |
| status | String | NOT NULL | success/failed/partial |
| questions_extracted | Integer | DEFAULT 0 | 提取题目数 |
| questions_imported | Integer | DEFAULT 0 | 入库题目数 |
| errors | String | | 错误信息 |
| created_at | DateTime | DEFAULT NOW | 处理时间 |

## 题型枚举（20+种）

### 数与代数（14种）
1. `mental_arithmetic` - 口算题
2. `vertical_calculation` - 竖式计算
3. `step_calculation` - 脱式计算
4. `fill_unknown` - 填未知数
5. `number_composition` - 数的组成
6. `number_read_write` - 数的读写
7. `compare_size` - 比大小
8. `pattern_sequence` - 规律填数
9. `verification` - 验算题
10. `estimation` - 估算题
11. `simplified_calculation` - 简便计算
12. `composite_expression` - 列综合算式
13. `solve_equation` - 解方程
14. `percentage` - 百分数/折扣/税率

### 几何与量（4种）
15. `shape_counting` - 图形计数
16. `perimeter_area` - 周长面积计算
17. `unit_conversion` - 单位换算
18. `angle_measurement` - 角的度量

### 统计与解决问题（3种）
19. `chart_analysis` - 统计图表分析
20. `word_problem` - 解决问题
21. `math_puzzle` - 数学广角(搭配/植树/抽屉)

## 知识点覆盖范围

| 年级 | 知识点数量 | 核心内容 |
|------|-----------|----------|
| 一年级上册 | 8 | 1-20数的认识、加减法、认识钟表 |
| 一年级下册 | 7 | 20以内退位减法、100以内数、人民币 |
| 二年级上册 | 8 | 100以内加减法、表内乘法、认识时间 |
| 二年级下册 | 8 | 表内除法、混合运算、万以内数 |
| 三年级上册 | 8 | 万以内加减法、倍的认识、分数初步 |
| 三年级下册 | 7 | 除数是一位数除法、面积、小数初步 |
| 四年级上册 | 8 | 大数认识、三位数乘两位数、条形统计图 |
| 四年级下册 | 8 | 小数、三角形、平均数 |
| 五年级上册 | 6 | 小数乘除法、简易方程、多边形面积 |
| 五年级下册 | 7 | 因数倍数、长方体、分数加减法 |
| 六年级上册 | 7 | 分数乘除法、比、圆、百分数 |
| 六年级下册 | 6 | 负数、圆柱圆锥、比例 |
| **合计** | **~100** | |

## 状态流转

### Question 审核状态

```
pending ──→ approved（审核通过）
   │
   └──→ rejected（驳回，需修改后重新提交）
```

### 程序化生成题目

```
generate-questions → 自动生成 → review_status=approved（免审核）
```

### 卷子提取题目

```
extract → LLM解析 → review_status=pending → 人工审核 → approved/rejected
```

## 数据量估算

| 实体 | MVP 数量 | 长期目标 |
|------|----------|----------|
| KnowledgePoint | ~100 | ~150 |
| Question | ~5000 | ~15000 |
| Paper | ~20 | 不限 |
| ErrorSet | ~50 | ~1000 |
| ProcessingLog | ~25 | 不限 |
