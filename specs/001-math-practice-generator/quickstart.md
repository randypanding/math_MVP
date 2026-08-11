# Quickstart: 数学专题练习卷生成器

## 前置条件

- Python 3.11+
- Microsoft Word（用于 .doc 文件读取）
- LLM API Key（通义千问 / DeepSeek / OpenAI 兼容）

## 安装

```bash
cd math-practice-generator
pip install -e .
cp .env.example .env
# 编辑 .env 填入 API Key
```

## 快速验证流程

### Step 1: 初始化题库（程序化生成）

```bash
# 生成全知识点题目（约5000道）
mathgen generate-questions --all

# 或指定年级
mathgen generate-questions --grade 2

# 或指定知识点
mathgen generate-questions --kp "100以内进位加法" -n 50
```

**预期输出**:
```
Generating questions...
Grade 1: 800 questions generated
Grade 2: 900 questions generated
Grade 3: 850 questions generated
Grade 4: 850 questions generated
Grade 5: 800 questions generated
Grade 6: 800 questions generated
Total: 5000 questions
Database: data/mathgen.db
```

### Step 2: 查询题库

```bash
# 按知识点查询
mathgen query --kp "100以内进位加法" --limit 5

# 按年级查询
mathgen query --grade 2 --type mental_arithmetic

# 按难度查询
mathgen query --difficulty 3 --limit 10
```

**预期输出**:
```
ID  | 题型     | 题目           | 答案 | 难度 | 状态
----|---------|---------------|------|------|------
1   | 口算题   | 47 + 36 = ?   | 83   | 2    | approved
2   | 口算题   | 52 - 18 = ?   | 34   | 2    | approved
3   | 竖式计算 | 25+37         | 62   | 2    | approved
4   | 填未知数 | __ + 8 = 15   | 7    | 1    | approved
5   | 解决问题 | 小明有12个... | 17   | 3    | approved
```

### Step 3: 生成练习卷

```bash
# 单知识点练习卷
mathgen generate --kp "100以内进位加法" -n 20 --with-answer

# 多知识点混合
mathgen generate --kp "100以内进位加法,100以内退位减法" -n 30

# 指定题型
mathgen generate --kp "表内乘法" --type "mental_arithmetic,vertical_calculation" -n 50

# 按年级出卷
mathgen generate --grade 2 -n 50 --with-answer --with-error-tip
```

**预期输出**:
```
Generated: data/output/100以内加减法_20题_20260811.pdf
Questions: 20
Types: 口算题(10), 竖式计算(5), 解决问题(5)
Pages: 4 (2 question + 2 answer)
```

### Step 4: 查看统计

```bash
mathgen stats
```

**预期输出**:
```
题库统计
========
总题数: 5000
知识点数: 100
年级覆盖: 1-6年级
已生成练习卷: 1

年级分布:
  一年级: 1500 题
  二年级: 1400 题
  三年级: 1000 题
  四年级: 600 题
  五年级: 300 题
  六年级: 200 题

题型分布:
  口算题: 1200
  竖式计算: 800
  解决问题: 600
  ...
```

### Step 5: 从卷子提取题目（可选）

```bash
# 处理单个文件
mathgen extract "path/to/试卷.doc"

# 批量处理
mathgen batch "path/to/试卷文件夹"

# 审核提取结果
mathgen review
```

### Step 6: 错题重练（可选）

```bash
# 导入错题
mathgen import-error "path/to/错题图片.png"

# 生成错题专项练习
mathgen error-practice -n 20
```

## 支持的题型（20+种）

| 类别 | 题型 |
|------|------|
| 数与代数 | 口算、竖式、脱式、填未知数、数的组成、数的读写、比大小、规律填数、验算、估算、简便计算、列综合算式、解方程、百分数 |
| 几何与量 | 图形计数、周长面积、单位换算、角的度量 |
| 统计与解决问题 | 统计图表、解决问题、数学广角 |

## 验证检查点

- [ ] 数据库文件 `data/mathgen.db` 已创建
- [ ] 题库中有 5000+ 道题目
- [ ] 覆盖 100+ 知识点、20+ 题型
- [ ] PDF 文件可正常打开和打印
- [ ] 答案页包含正确答案和易错提示
- [ ] 统计报告数据准确
