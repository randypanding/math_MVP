"""
易错模式生成器 - 基于真实教育研究论文（结构化重构版）

设计依据（详见 specs/001-math-practice-generator/error-pattern-and-answer-suggestions.md）：
1. 双层结构：区分「计算性错误 / 规则未掌握」与「概念性误解」，并维护层级/子集关系图
   （A Benchmark for Math Misconceptions, 2412.03765）
2. 可执行规则 + 适用题型集合 + 参数化模板：把误解编码为可执行的错误规则，生成
   「正确路径 + 错误路径」双轨迹（MalruleLib, 2601.03217；LLM-based Cognitive Models, 2410.12294）
3. 单步化简 + 错误插入点：解法拆成逐步，指出第几步用了错误规则
4. 多类错误分类：conceptual / semantic / calculation / missing_step / logic / procedural
   （Achieving >97% on GSM8K, 2404.14963）
5. 干扰项编码误解维度：每个干扰项对应一种常见误解（Discovering Misconceptions, 2606.08986）
6. 反馈针对性：指出错在哪一步、用了什么错误规则、正确规则应是什么（Simulating Students, 2605.12748）
7. 反馈语言适配 + 苏格拉底式引导性追问（Automatic Generation of Socratic Subquestions, 2211.12835）

论文来源（原有基础）：
1. Purnomo, Y.W., et al. (2019). Infinity Journal, 8(1), 57-74. 分数除法概念性知识不完整
2. Gicale, A.K. (2026). RISE Journal, 3(4). 干扰项分析与错误路径
3. Abdrasilov, B., et al. (2026). Frontiers in Big Data, 9, 1772101. AI出题需专家校准
"""

import random
import json
from typing import List, Dict, Any, Tuple, Optional


# ============================================================
# 错误类别枚举（error_category）
# ============================================================
# conceptual: 概念性误解（概念理解层面的系统性问题）
# semantic:   语义误解（应用题/题意理解错误）
# calculation: 计算错误（算术计算失误）
# missing_step: 漏步（跳过必要步骤）
# logic:       逻辑/结构错误（运算顺序、数量关系、证明结构）
# procedural:  程序性错误（步骤模板/算法未掌握）
CATEGORY_LABELS = {
    "conceptual": "概念性误解",
    "semantic": "语义误解",
    "calculation": "计算错误",
    "missing_step": "漏步",
    "logic": "逻辑/结构错误",
    "procedural": "程序性错误",
}


# ============================================================
# 主题（theme）枚举
# ============================================================
THEME_LABELS = {
    "number_sense": "数感",
    "arithmetic": "数与运算",
    "fraction": "分数",
    "decimal": "小数",
    "proportion": "比与比例",
    "geometry": "几何与测量",
    "unit": "量与单位",
    "statistics": "统计与概率",
    "algebra": "代数思想",
}


# ============================================================
# 易错模式库（可执行规则 + 层级关系 + 适用题型 + 多模板）
# ============================================================
# 每个模式字段：
#   id, name, level, theme, category, parent(依赖), wrong_rule(错误规则描述),
#   correct_rule(正确规则), applicable_types(适用题型), templates(参数化模板函数列表),
#   hint_prefix(提示前缀)
# level: "computation_error"=计算性错误(规则未掌握)；"misconception"=概念性误解
PATTERNS: Dict[str, Dict[str, Any]] = {
    # ---------- 数与运算 ----------
    "carry_omitted": {
        "id": "carry_omitted",
        "name": "进位遗忘",
        "level": "computation_error",
        "theme": "arithmetic",
        "category": "procedural",
        "parent": None,
        "wrong_rule": "个位相加满十后忘记向十位进1",
        "correct_rule": "个位满十向十位进1，十位相加时加上进位的1",
        "applicable_types": ["mental_arithmetic", "vertical_calculation", "step_calculation"],
        "templates": ["add_carry", "add_carry_vertical"],
        "hint_prefix": "先看个位是否满十，满十要向十位进1",
    },
    "borrow_omitted": {
        "id": "borrow_omitted",
        "name": "退位遗忘",
        "level": "computation_error",
        "theme": "arithmetic",
        "category": "procedural",
        "parent": None,
        "wrong_rule": "个位不够减从十位退1后，十位忘记减1",
        "correct_rule": "个位不够减从十位退1当10，十位相应减1",
        "applicable_types": ["mental_arithmetic", "vertical_calculation", "step_calculation"],
        "templates": ["sub_borrow"],
        "hint_prefix": "个位不够减时，要从十位退1，先看十位怎么变",
    },
    "sign_confusion": {
        "id": "sign_confusion",
        "name": "符号混淆",
        "level": "computation_error",
        "theme": "arithmetic",
        "category": "logic",
        "parent": None,
        "wrong_rule": "把加减符号看错或运算顺序颠倒",
        "correct_rule": "按题干符号与运算顺序（先乘除后加减）计算",
        "applicable_types": ["mental_arithmetic", "step_calculation"],
        "templates": ["add_sub_mixed"],
        "hint_prefix": "先确认题目是加还是减，再按顺序计算",
    },
    "order_of_operations": {
        "id": "order_of_operations",
        "name": "运算顺序错",
        "level": "computation_error",
        "theme": "arithmetic",
        "category": "logic",
        "parent": None,
        "wrong_rule": "不按先乘除后加减、先括号内的顺序计算",
        "correct_rule": "先算括号内，再乘除，最后加减",
        "applicable_types": ["step_calculation", "composite_expression"],
        "templates": ["mixed_ops"],
        "hint_prefix": "有括号先算括号，再算乘除，最后算加减",
    },
    # ---------- 分数 ----------
    "fraction_rat_vs_quantity": {
        "id": "fraction_rat_vs_quantity",
        "name": "量率混淆",
        "level": "misconception",
        "theme": "fraction",
        "category": "conceptual",
        "parent": None,
        "wrong_rule": "把'每段占全长的分率'与'每段的实际长度'混淆",
        "correct_rule": "分率是把整体看作1，长度是具体数量，要区分是求'分率'还是求'长度'",
        "applicable_types": ["mental_arithmetic", "word_problem"],
        "templates": ["fraction_ratio"],
        "hint_prefix": "先问清楚：这题是求'占全长的几分之几'还是求'每段长多少'",
    },
    "fraction_no_invert": {
        "id": "fraction_no_invert",
        "name": "分数除法不颠倒",
        "level": "misconception",
        "theme": "fraction",
        "category": "procedural",
        "parent": None,
        "wrong_rule": "除以一个分数时直接相乘，忘记把除数颠倒(取倒数)",
        "correct_rule": "除以一个数等于乘以它的倒数",
        "applicable_types": ["mental_arithmetic", "word_problem"],
        "templates": ["frac_div"],
        "hint_prefix": "除法变乘法时，除数要颠倒分子分母",
    },
    "fraction_add_bypart": {
        "id": "fraction_add_bypart",
        "name": "分子分母分别加减",
        "level": "misconception",
        "theme": "fraction",
        "category": "conceptual",
        "parent": None,
        "wrong_rule": "分数相加减时分子加分子、分母加分母，忘记通分",
        "correct_rule": "先通分成同分母，再分母不变、分子相加减",
        "applicable_types": ["mental_arithmetic", "step_calculation"],
        "templates": ["frac_add"],
        "hint_prefix": "分数加减要先通分，分母一样了才能加分子",
    },
    # ---------- 小数 ----------
    "decimal_align": {
        "id": "decimal_align",
        "name": "小数点不对齐",
        "level": "misconception",
        "theme": "decimal",
        "category": "conceptual",
        "parent": None,
        "wrong_rule": "小数加减按末位对齐而非小数点对齐",
        "correct_rule": "小数加减要把小数点对齐，再按整数加减",
        "applicable_types": ["mental_arithmetic", "vertical_calculation"],
        "templates": ["dec_add", "dec_sub"],
        "hint_prefix": "列竖式时小数点要对齐",
    },
    "decimal_point_shift": {
        "id": "decimal_point_shift",
        "name": "小数点位置错",
        "level": "computation_error",
        "theme": "decimal",
        "category": "calculation",
        "parent": None,
        "wrong_rule": "乘除时小数点移动位数错误",
        "correct_rule": "乘10/100/1000小数点右移对应位，除则左移",
        "applicable_types": ["mental_arithmetic", "vertical_calculation"],
        "templates": ["dec_mul", "dec_div"],
        "hint_prefix": "小数点移动的位数要和0的个数一致",
    },
    # ---------- 几何与测量 ----------
    "perimeter_area_confusion": {
        "id": "perimeter_area_confusion",
        "name": "周长面积混淆",
        "level": "misconception",
        "theme": "geometry",
        "category": "conceptual",
        "parent": None,
        "wrong_rule": "把周长公式与面积公式混淆使用",
        "correct_rule": "周长是围一圈的长度(长度单位)，面积是表面的大小(面积单位)",
        "applicable_types": ["perimeter_area", "word_problem"],
        "templates": ["rect_perimeter_area", "square_perimeter_area"],
        "hint_prefix": "分清求的是周长（一圈有多长）还是面积（表面有多大）",
    },
    "half_circle_missing_diameter": {
        "id": "half_circle_missing_diameter",
        "name": "半圆周长漏直径",
        "level": "computation_error",
        "theme": "geometry",
        "category": "missing_step",
        "parent": None,
        "wrong_rule": "半圆周长只算圆弧长度，漏加直径",
        "correct_rule": "半圆周长 = 圆弧长 + 直径",
        "applicable_types": ["perimeter_area", "word_problem"],
        "templates": ["half_circle"],
        "hint_prefix": "半圆是围起来的，除了弯的弧，还有一条直的直径",
    },
    "area_no_square_unit": {
        "id": "area_no_square_unit",
        "name": "面积单位漏平方",
        "level": "computation_error",
        "theme": "geometry",
        "category": "missing_step",
        "parent": None,
        "wrong_rule": "计算面积时单位写成'厘米'而非'平方厘米'",
        "correct_rule": "面积单位要用平方单位(平方米/平方厘米)",
        "applicable_types": ["perimeter_area", "unit_conversion"],
        "templates": ["rect_perimeter_area"],
        "hint_prefix": "面积的结果后面单位要带'平方'",
    },
    # ---------- 比与比例 ----------
    "ratio_vs_area_ratio": {
        "id": "ratio_vs_area_ratio",
        "name": "半径比当面积比",
        "level": "misconception",
        "theme": "proportion",
        "category": "conceptual",
        "parent": None,
        "wrong_rule": "把长度比(半径比)直接当成面积比",
        "correct_rule": "相似图形面积比 = 对应长度比的平方",
        "applicable_types": ["word_problem", "mental_arithmetic"],
        "templates": ["ratio_area"],
        "hint_prefix": "面积比是长度比的平方，不是直接相等",
    },
    "proportional_misjudge": {
        "id": "proportional_misjudge",
        "name": "正反比例误判",
        "level": "misconception",
        "theme": "proportion",
        "category": "conceptual",
        "parent": None,
        "wrong_rule": "把正比例与反比例关系混淆",
        "correct_rule": "成正比(比值一定)还是成反比(乘积一定)要看两个量的关系",
        "applicable_types": ["word_problem", "mental_arithmetic"],
        "templates": ["proportion_judge"],
        "hint_prefix": "判断成正反比：成正比看比值，成反比看乘积",
    },
    # ---------- 量与单位 ----------
    "unit_conversion_factor": {
        "id": "unit_conversion_factor",
        "name": "单位换算倍数错",
        "level": "computation_error",
        "theme": "unit",
        "category": "calculation",
        "parent": None,
        "wrong_rule": "单位换算时进率(倍数)用错",
        "correct_rule": "先确定两个单位间的进率，再乘或除",
        "applicable_types": ["unit_conversion", "word_problem"],
        "templates": ["unit_convert"],
        "hint_prefix": "先想清楚这两个单位之间的进率是多少",
    },
    "unit_omitted": {
        "id": "unit_omitted",
        "name": "漏写单位",
        "level": "computation_error",
        "theme": "unit",
        "category": "missing_step",
        "parent": None,
        "wrong_rule": "计算结果漏写单位或单位不统一",
        "correct_rule": "结果要带正确单位，且统一单位再计算",
        "applicable_types": ["unit_conversion", "word_problem"],
        "templates": ["unit_convert", "word_problem_unit"],
        "hint_prefix": "最后的结果要记得写单位",
    },
    # ---------- 数量关系 / 应用题 ----------
    "quantity_relation_error": {
        "id": "quantity_relation_error",
        "name": "数量关系错误",
        "level": "misconception",
        "theme": "arithmetic",
        "category": "semantic",
        "parent": None,
        "wrong_rule": "应用题中单位1/数量关系理解错误",
        "correct_rule": "先找出单位1与所求量之间的关系，再列式",
        "applicable_types": ["word_problem", "composite_expression"],
        "templates": ["word_problem_relation"],
        "hint_prefix": "先想想'谁是谁的几倍/几分之几'，单位1是哪个",
    },
    "keyword_shortcut": {
        "id": "keyword_shortcut",
        "name": "关键词捷径",
        "level": "misconception",
        "theme": "arithmetic",
        "category": "semantic",
        "parent": None,
        "wrong_rule": "只看关键词(如'多''少''一共')机械决定运算，不看数量关系",
        "correct_rule": "理解题意后再判断用加还是减/乘还是除",
        "applicable_types": ["word_problem"],
        "templates": ["word_problem_keyword"],
        "hint_prefix": "不要只看'多''少'两个字，要理解整句话的意思",
    },
    # ---------- 乘除 ----------
    "multiplication_error": {
        "id": "multiplication_error",
        "name": "口诀记错",
        "level": "computation_error",
        "theme": "arithmetic",
        "category": "calculation",
        "parent": None,
        "wrong_rule": "乘法口诀记错或记反",
        "correct_rule": "牢记乘法口诀，先确定因数再得积",
        "applicable_types": ["mental_arithmetic", "vertical_calculation"],
        "templates": ["mul"],
        "hint_prefix": "想一想乘法口诀，两个因数对应哪句口诀",
    },
    "remainder_not_less": {
        "id": "remainder_not_less",
        "name": "余数不小于除数",
        "level": "computation_error",
        "theme": "arithmetic",
        "category": "logic",
        "parent": None,
        "wrong_rule": "余数大于或等于除数仍直接写出",
        "correct_rule": "余数必须小于除数，否则继续分",
        "applicable_types": ["mental_arithmetic"],
        "templates": ["div_remainder"],
        "hint_prefix": "检查余数是不是比除数小",
    },
}


# ============================================================
# 主题 → 知识点路由
# ============================================================
def _route_patterns(kp_name: str) -> List[str]:
    """根据知识点名称返回适用的易错模式 id 列表"""
    name = kp_name
    if "小数" in name:
        return ["decimal_align", "decimal_point_shift"]
    if "分数" in name:
        return ["fraction_rat_vs_quantity", "fraction_no_invert", "fraction_add_bypart"]
    if "比例" in name or "正反" in name or "比" in name:
        return ["ratio_vs_area_ratio", "proportional_misjudge", "quantity_relation_error"]
    if "几何" in name or "图形" in name or "周长" in name or "面积" in name or "圆" in name:
        return ["perimeter_area_confusion", "half_circle_missing_diameter", "area_no_square_unit"]
    if "长度" in name or "单位" in name or "千克" in name or "克" in name or "人民币" in name:
        return ["unit_conversion_factor", "unit_omitted"]
    if "除法" in name:
        return ["remainder_not_less", "multiplication_error"]
    if "乘法" in name or "表内" in name:
        return ["multiplication_error"]
    if "内" in name or "加法" in name or "减法" in name or "运算" in name:
        return ["carry_omitted", "borrow_omitted", "sign_confusion", "order_of_operations"]
    if "解决问题" in name or "应用" in name:
        return ["keyword_shortcut", "quantity_relation_error"]
    return ["sign_confusion", "carry_omitted", "borrow_omitted"]


# ============================================================
# 模板生成函数（参数化，返回 stem/answer/solution 及步骤）
# ============================================================
def _tpl_add_carry() -> Dict[str, Any]:
    a = random.randint(25, 89)
    b = random.randint(7, 99 - a)
    correct = a + b
    ones = (a % 10) + (b % 10)
    carry = "满十" if ones >= 10 else "不满十"
    wrong = correct - 10  # 忘记进位
    stem = f"{a} + {b} = ___"
    steps = [
        {"step": f"先算个位 {a % 10} + {b % 10} = {ones % 10}（{carry}）", "is_error_point": False},
        {"step": f"再算十位 {a // 10} + {b // 10}" + (f"（满十进1记得加1）" if carry == "满十" else ""), "is_error_point": carry == "满十"},
        {"step": f"结果为 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} + {b} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_sub_borrow() -> Dict[str, Any]:
    a = random.randint(30, 99)
    b = random.randint(11, a - 10)
    correct = a - b
    wrong = correct + 1  # 忘记十位减1
    stem = f"{a} - {b} = ___"
    needs_borrow = (a % 10) < (b % 10)
    steps = [
        {"step": f"个位 {a % 10} - {b % 10}" + ("，不够减，从十位退1" if needs_borrow else ""), "is_error_point": False},
        {"step": f"从十位退1后，十位要减1（{a // 10} 变 {a // 10 - 1}）" if needs_borrow else f"十位 {a // 10} - {b // 10}", "is_error_point": needs_borrow},
        {"step": f"结果为 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} - {b} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_add_sub_mixed() -> Dict[str, Any]:
    a = random.randint(10, 99)
    b = random.randint(10, 99)
    if a > b:
        correct = a - b
        stem = f"{a} - {b} = ___"
    else:
        correct = a + b
        stem = f"{a} + {b} = ___"
    wrong1 = correct - 1
    wrong2 = correct + 1
    stem = f"{a} " + ("- " if a > b else "+ ") + f"{b} = ___"
    steps = [
        {"step": f"确认符号：{'减法' if a > b else '加法'}", "is_error_point": False},
        {"step": f"按位计算得 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} {'-' if a > b else '+'} {b} = {correct}",
        "wrong_value": str(wrong1), "wrong2": str(wrong2), "steps": steps,
    }


def _tpl_mixed_ops() -> Dict[str, Any]:
    a = random.randint(2, 12)
    b = random.randint(2, 12)
    c = random.randint(2, 12)
    # 先乘除后加减：a + b × c
    correct = a + b * c
    wrong = (a + b) * c  # 先算加法再乘
    stem = f"{a} + {b} × {c} = ___"
    steps = [
        {"step": f"先算乘法 {b} × {c} = {b * c}", "is_error_point": False},
        {"step": f"再算加法 {a} + {b * c} = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} + {b} × {c} = {a} + {b * c} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_fraction_ratio() -> Dict[str, Any]:
    den = random.randint(2, 9)
    num = random.randint(1, den - 1)
    total = den * random.randint(2, 5)
    stem = f"把一条{total}厘米长的绳子平均分成{den}段，每段占全长的几分之几？"
    correct = f"1/{den}"
    wrong = f"1/{num}"
    steps = [
        {"step": f"求'占全长的几分之几'是求分率，把全长看作单位1", "is_error_point": False},
        {"step": f"平均分成{den}段，每段占 1 ÷ {den} = 1/{den}", "is_error_point": False},
        {"step": f"注意：这里求的是分率，不是每段的长度（{total}÷{den}={total // den}厘米）", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": correct,
        "solution": f"把全长看作1，每段占 1/{den}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_frac_div() -> Dict[str, Any]:
    a = random.randint(1, 5)
    b = random.randint(2, 5)
    stem = f"{a}/{b} ÷ {a} = ___"
    correct = f"1/{b}"
    wrong = f"{a * a}/{b * a}"  # 不颠倒直接乘
    steps = [
        {"step": f"除法变乘法，除数 {a} 变 1/{a}：{a}/{b} × 1/{a}", "is_error_point": False},
        {"step": f"分子分母约分：{a} 与 {a} 约掉，得 1/{b}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": correct,
        "solution": f"{a}/{b} ÷ {a} = {a}/{b} × 1/{a} = 1/{b}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_frac_add() -> Dict[str, Any]:
    a, c = random.randint(1, 3), random.randint(1, 3)
    b, d = random.randint(2, 5), random.randint(2, 5)
    correct = f"{a * d + c * b}/{b * d}"
    wrong = f"{a + c}/{b + d}"  # 分子分母分别相加
    stem = f"{a}/{b} + {c}/{d} = ___"
    steps = [
        {"step": f"通分：公分母为 {b} × {d} = {b * d}", "is_error_point": False},
        {"step": f"分子相加：{a * d} + {c * b} = {a * d + c * b}", "is_error_point": False},
        {"step": f"结果 {a * d + c * b}/{b * d}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": correct,
        "solution": f"通分后 = {a * d + c * b}/{b * d}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_dec_add() -> Dict[str, Any]:
    a = round(random.uniform(1.0, 9.9), 2)
    b = round(random.uniform(1.0, 9.9), 2)
    correct = round(a + b, 2)
    # 小数点不对齐：按末位对齐会丢失/错位小数位 → 取 1 位小数（丢百分位）
    wrong = round(a + b, 1)
    if wrong == correct:  # 兜底：确保错误答案与正确答案不同
        wrong = round(correct, 1)
    if wrong == correct:
        wrong = correct + 0.01
    stem = f"{a} + {b} = ___"
    steps = [
        {"step": f"小数点对齐后相加：{a} + {b}", "is_error_point": False},
        {"step": f"结果为 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} + {b} = {correct}",
        "wrong_value": str(round(wrong, 2)), "steps": steps,
    }


def _tpl_dec_mul() -> Dict[str, Any]:
    a = round(random.uniform(1.0, 9.9), 2)
    b = random.choice([10, 100])
    correct = round(a * b, 2)
    wrong = round(a * b / 10, 2)  # 少移一位
    if wrong == correct:  # 兜底：确保错误答案与正确答案不同
        wrong = round(a * b * 10, 2)
    stem = f"{a} × {b} = ___"
    steps = [
        {"step": f"×{b} 小数点向右移动 {len(str(b)) - 1} 位", "is_error_point": False},
        {"step": f"结果为 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} × {b} = {correct}",
        "wrong_value": str(wrong), "steps": steps,
    }


def _tpl_rect_perimeter_area() -> Dict[str, Any]:
    length = random.randint(5, 20)
    width = random.randint(3, min(15, length))
    perimeter = (length + width) * 2
    area = length * width
    stem = f"一个长方形长{length}厘米，宽{width}厘米，周长和面积分别是多少？"
    answer = f"周长={perimeter}厘米，面积={area}平方厘米"
    wrong = f"周长={area}厘米，面积={perimeter}平方厘米"  # 混淆
    steps = [
        {"step": f"周长=(长+宽)×2=({length}+{width})×2={perimeter}厘米", "is_error_point": False},
        {"step": f"面积=长×宽={length}×{width}={area}平方厘米", "is_error_point": False},
        {"step": "注意周长用长度单位，面积用平方单位", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": answer,
        "solution": f"周长={(length + width) * 2}厘米，面积={area}平方厘米",
        "wrong_value": wrong, "wrong2": f"周长={perimeter}平方厘米", "steps": steps,
    }


def _tpl_half_circle() -> Dict[str, Any]:
    r = random.randint(3, 10)
    arc = round(3.14 * r, 2)
    diameter = 2 * r
    correct = round(arc + diameter, 2)
    wrong = arc  # 漏直径
    stem = f"一个半圆半径是{r}厘米，求半圆的周长（π取3.14）"
    steps = [
        {"step": f"弧长 = π×r = 3.14×{r} = {arc}", "is_error_point": False},
        {"step": f"半圆周长 = 弧长 + 直径 = {arc} + {diameter} = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": f"{correct}厘米",
        "solution": f"C = 3.14×{r} + 2×{r} = {correct}厘米",
        "wrong_value": f"{wrong}厘米", "steps": steps,
    }


def _tpl_unit_convert() -> Dict[str, Any]:
    conversions = [
        ("米", "厘米", 100), ("千米", "米", 1000), ("元", "角", 10),
        ("小时", "分钟", 60), ("年", "月", 12), ("吨", "千克", 1000),
        ("平方米", "平方分米", 100), ("克", "千克", 1000),
    ]
    unit1, unit2, factor = random.choice(conversions)
    value = random.randint(1, 10)
    correct = value * factor
    wrong = value * 10
    stem = f"{value}{unit1} = （___）{unit2}"
    steps = [
        {"step": f"{unit1} 与 {unit2} 之间的进率是 {factor}", "is_error_point": False},
        {"step": f"{value} × {factor} = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": f"{correct}{unit2}",
        "solution": f"{value}{unit1} = {correct}{unit2}",
        "wrong_value": f"{wrong}{unit2}", "steps": steps,
    }


def _tpl_mul() -> Dict[str, Any]:
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    correct = a * b
    wrong = correct + a
    stem = f"{a} × {b} = ___"
    steps = [
        {"step": f"乘法口诀：{a} × {b}", "is_error_point": False},
        {"step": f"积为 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} × {b} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_div_remainder() -> Dict[str, Any]:
    b = random.randint(2, 9)
    q = random.randint(3, 12)
    r = random.randint(1, b - 1)
    a = b * q + r
    correct = f"{q}...{r}"
    wrong = f"{q}...{r * 10}"
    stem = f"{a} ÷ {b} = ___ ... ___"
    steps = [
        {"step": f"{a} ÷ {b}，商 {q}，余数 {r}", "is_error_point": False},
        {"step": f"检查余数 {r} < 除数 {b}，成立", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": correct,
        "solution": f"{a} ÷ {b} = {q} 余 {r}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_ratio_area() -> Dict[str, Any]:
    r1 = random.randint(2, 5)
    r2 = r1 + random.randint(1, 3)
    correct = f"{r1 * r1}:{r2 * r2}"
    wrong = f"{r1}:{r2}"
    stem = f"大圆半径和小圆半径比是{r1}:{r2}，大圆和小圆面积比是多少？"
    steps = [
        {"step": f"面积比 = 半径比² = {r1}²:{r2}² = {r1 * r1}:{r2 * r2}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": correct,
        "solution": f"面积比 = {r1}²:{r2}² = {r1 * r1}:{r2 * r2}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_proportion_judge() -> Dict[str, Any]:
    stem = "判断：圆的半径和周长成什么比例？"
    correct = "正比例"
    solution = "C = 2πr，C/r = 2π（定值），所以成正比例"
    wrong = "反比例"
    steps = [
        {"step": "写关系式：C = 2πr", "is_error_point": False},
        {"step": "看 C 与 r 的比：C/r = 2π 是定值 → 正比例", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": correct, "solution": solution,
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_word_problem_relation() -> Dict[str, Any]:
    base = random.randint(3, 9)
    times = random.randint(2, 5)
    correct = base * times
    wrong = base + times  # 把倍误当加
    stem = f"小明有{base}个苹果，小红的是小明的{times}倍，小红有多少个？"
    steps = [
        {"step": f"单位1是小明（{base}个），求小红的 = 单位1 × 倍数", "is_error_point": False},
        {"step": f"{base} × {times} = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{base} × {times} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_word_problem_keyword() -> Dict[str, Any]:
    a = random.randint(10, 30)
    stem = f"有{a}个苹果，分掉了{a - 5}个，还剩多少个？"
    correct = 5
    wrong = a + (a - 5)  # 看到"分掉"机械相加
    steps = [
        {"step": f"理解：从{a}个里减掉分掉的{a - 5}个", "is_error_point": False},
        {"step": f"{a} - {a - 5} = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} - {a - 5} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


# 模板分发表
TEMPLATES = {
    "add_carry": _tpl_add_carry,
    "add_carry_vertical": _tpl_add_carry,
    "sub_borrow": _tpl_sub_borrow,
    "add_sub_mixed": _tpl_add_sub_mixed,
    "mixed_ops": _tpl_mixed_ops,
    "fraction_ratio": _tpl_fraction_ratio,
    "frac_div": _tpl_frac_div,
    "frac_add": _tpl_frac_add,
    "dec_add": _tpl_dec_add,
    "dec_sub": _tpl_dec_add,
    "dec_mul": _tpl_dec_mul,
    "dec_div": _tpl_dec_mul,
    "rect_perimeter_area": _tpl_rect_perimeter_area,
    "square_perimeter_area": _tpl_rect_perimeter_area,
    "half_circle": _tpl_half_circle,
    "unit_convert": _tpl_unit_convert,
    "word_problem_unit": _tpl_word_problem_relation,
    "ratio_area": _tpl_ratio_area,
    "proportion_judge": _tpl_proportion_judge,
    "word_problem_relation": _tpl_word_problem_relation,
    "word_problem_keyword": _tpl_word_problem_keyword,
    "mul": _tpl_mul,
    "div_remainder": _tpl_div_remainder,
}


# ============================================================
# 结构化反馈组装
# ============================================================
def _build_feedback(pattern: Dict[str, Any], tpl: Dict[str, Any],
                    difficulty: int) -> Dict[str, Any]:
    """组装结构化反馈：错误类别、错误点、双路径、苏格拉底提示、干扰项映射"""
    steps = tpl.get("steps", [])
    # 标记错误插入点（把最容易错的一步标为 error_point）
    error_step = None
    for s in steps:
        if s.get("is_error_point"):
            error_step = s["step"]
            break
    if error_step is None and steps:
        # 默认把最后一步前标为易错点
        error_step = f"在第 {len(steps)} 步易出错"

    # 错误路径（学生按错误规则得到的结果）
    wrong_path_steps = []
    for s in steps:
        wrong_path_steps.append(s["step"])

    # 苏格拉底式引导性追问（逐级提示）
    socratic_hints = [
        pattern["hint_prefix"],
        f"用正确规则：{pattern['correct_rule']}",
        "再检查一遍你的每一步，看看是哪一步和你原来的做法不一样",
    ]

    # 干扰项/错误答案映射（每个干扰项对应一种常见误解）
    wrong_value = tpl.get("wrong_value")
    wrong2 = tpl.get("wrong2")
    distractor_mapping = [
        {"value": str(wrong_value), "misconception": pattern["name"]},
    ]
    if wrong2:
        distractor_mapping.append({"value": str(wrong2), "misconception": "同类计算偏差"})

    # 难度附加：难点主题（分数/比例/几何坐标）标记需更详细解析
    hard_topics = {"fraction", "proportion"}
    enhanced = pattern["theme"] in hard_topics

    return {
        "error_category": pattern["category"],
        "error_category_label": CATEGORY_LABELS.get(pattern["category"], pattern["category"]),
        "pattern_id": pattern["id"],
        "pattern_name": pattern["name"],
        "pattern_level": pattern["level"],
        "theme": pattern["theme"],
        "theme_label": THEME_LABELS.get(pattern["theme"], pattern["theme"]),
        "wrong_rule": pattern["wrong_rule"],
        "correct_rule": pattern["correct_rule"],
        "error_step": error_step,
        "steps": steps,
        "wrong_path": wrong_path_steps,
        "socratic_hints": socratic_hints,
        "distractor_mapping": distractor_mapping,
        "solution_status": "targeted",  # targeted=针对性反馈
        "enhanced_explanation": enhanced,
    }


# ============================================================
# 主入口
# ============================================================
def generate_question_with_errors(kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
    """根据知识点生成带易错模式的题目（结构化输出）"""
    pattern_ids = _route_patterns(kp_name)
    pid = random.choice(pattern_ids)
    pattern = PATTERNS[pid]

    # 从该模式的模板中随机选一个
    tpl_name = random.choice(pattern["templates"])
    tpl_fn = TEMPLATES[tpl_name]
    tpl = tpl_fn()

    # 组装结构化反馈
    fb = _build_feedback(pattern, tpl, difficulty)

    # 生成易错点文案（兼容原有 renderer 的字符串 common_error）
    common_error = (
        f"{fb['error_category_label']}：{pattern['wrong_rule']}。"
        f"正确做法是：{pattern['correct_rule']}。"
    )

    question_type = pattern["applicable_types"][0]
    if "应用题" in kp_name or "解决问题" in kp_name:
        question_type = "word_problem"
    elif "面积" in kp_name or "周长" in kp_name:
        question_type = "perimeter_area"
    elif "单位" in kp_name:
        question_type = "unit_conversion"

    # 返回结构化字典（新增字段，保持原有字段兼容）
    return {
        "knowledge_point_id": kp_id,
        "question_type": question_type,
        "stem": tpl["stem"],
        "answer": tpl["answer"],
        "solution": tpl["solution"],
        "common_error": common_error,
        "difficulty": difficulty,
        "source": "程序生成（基于教育研究论文结构化易错模式）",
        "review_status": "approved",
        # ---- 结构化易错模式字段 ----
        "error_category": fb["error_category"],
        "error_category_label": fb["error_category_label"],
        "pattern_id": fb["pattern_id"],
        "pattern_name": fb["pattern_name"],
        "pattern_level": fb["pattern_level"],
        "theme": fb["theme"],
        "theme_label": fb["theme_label"],
        "wrong_rule": fb["wrong_rule"],
        "correct_rule": fb["correct_rule"],
        "wrong_value": str(tpl.get("wrong_value", "")),
        "error_step": fb["error_step"],
        "steps": json.dumps(fb["steps"], ensure_ascii=False),
        "wrong_path": json.dumps(fb["wrong_path"], ensure_ascii=False),
        "socratic_hints": json.dumps(fb["socratic_hints"], ensure_ascii=False),
        "distractor_mapping": json.dumps(fb["distractor_mapping"], ensure_ascii=False),
        "solution_status": fb["solution_status"],
        "enhanced_explanation": fb["enhanced_explanation"],
    }


def get_pattern_hierarchy() -> Dict[str, Any]:
    """返回易错模式层级关系图（错误/误解 → 分类树）"""
    tree = {}
    for pid, p in PATTERNS.items():
        theme = p["theme"]
        tree.setdefault(theme, {"label": THEME_LABELS.get(theme, theme), "patterns": []})
        tree[theme]["patterns"].append({
            "id": p["id"], "name": p["name"], "level": p["level"],
            "category": p["category"], "parent": p["parent"],
        })
    return tree