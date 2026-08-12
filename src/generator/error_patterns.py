"""
易错模式生成器 - 基于真实教育研究论文（结构化重构版）

设计依据（详见 specs/001-math-practice-generator/error-pattern-and-answer-suggestions.md）：
1. 双层结构：区分「计算性错误 / 规则未掌握」与「概念性误解」，并维护层级/子集关系图
   （A Benchmark for Math Misconceptions, 2412.03765）
2. 可执行规则 + 适用题型集合 + 参数化模板：把误解编码为可执行的错误规则，生成
   「正确路径 + 错误路径」双轨迹（MalruleLib, 2601.03217；LLM-based Cognitive Models, 2410.12294）
3. 单步化简 + 错误插入点：解法拆成逐步，指出第几步用了错误规则
4. 多类错误分类：conceptual / semantic / calculation / missing_step / logic / procedural
5. 干扰项编码误解维度：每个干扰项对应一种常见误解
6. 反馈针对性：指出错在哪一步、用了什么错误规则、正确规则应是什么
7. 反馈语言适配 + 苏格拉底式引导性追问

QA 修复（FEEDBACK_QA_REPORT.md / 2026-08-12）：
- A/F：题型选择改为「尊重知识点声明的 types」，并补齐全部 22 种声明题型的模板，
       彻底解决「只产出 5 种题型、vertical_calculation 恒为 0、口算题占比过高」。
- B：   模板函数增加 grade/semester 感知，按年级调整数值范围；并通过 TEMPLATE_GRADE
       做「年级白名单」，杜绝半圆/比例/百分数等六年级内容出现在低年级卷子中。
"""

import inspect
import random
import json
from typing import List, Dict, Any, Tuple, Optional


# ============================================================
# 错误类别枚举（error_category）
# ============================================================
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
# 年级相关工具
# ============================================================
def _grade_bounds(grade: Optional[str]) -> int:
    """按年级返回加减法操作数的数量级上限"""
    return {
        "一年级": 20,
        "二年级": 100,
        "三年级": 1000,
        "四年级": 10000,
        "五年级": 10000,
        "六年级": 100000,
    }.get(grade, 100)


def _grade_add_pair(grade: Optional[str]) -> Tuple[int, int]:
    """生成一对适合该年级的进位加法操作数"""
    if grade == "一年级":
        # 20 以内进位加：个位相加满十
        a = random.choice([6, 7, 8, 9])
        b = random.randint(2, 9)
        while not (11 <= a + b <= 18):
            b = random.randint(2, 9)
        return a, b
    hi = _grade_bounds(grade)
    o1 = random.randint(2, 9)
    o2 = random.randint(10 - o1, 9)          # 保证个位进位
    hi_t = max(1, hi // 10)
    t1 = random.randint(0, max(0, hi_t - 2))
    t2 = random.randint(0, max(0, hi_t - t1 - 1))
    a, b = t1 * 10 + o1, t2 * 10 + o2
    if a + b > hi or a == 0 or b == 0:
        a = random.randint(11, min(hi - 1, 99))
        b = random.randint(10, min(hi - a, 99))
    return a, b


def _grade_sub_pair(grade: Optional[str]) -> Tuple[int, int]:
    """生成一对适合该年级的退位减法操作数"""
    if grade == "一年级":
        a = random.randint(11, 18)
        while True:
            b = random.randint(2, a - 1)
            if (a % 10) < (b % 10):
                return a, b
    hi = _grade_bounds(grade)
    o_a = random.randint(1, 8)
    o_b = random.randint(o_a + 1, 9)         # 个位不够减 → 退位
    t_a = random.randint(2, max(2, hi // 10))
    t_b = random.randint(0, t_a - 1)
    a, b = t_a * 10 + o_a, t_b * 10 + o_b
    if a <= b:
        a += 10
    return a, b


def _cn_number(n: int) -> str:
    """把 1 ~ 9999 的整数转成中文读法（用于数的读写题）"""
    digits = "零一二三四五六七八九"
    if n < 10:
        return digits[n]
    if n < 20:
        return "十" + (digits[n % 10] if n % 10 else "")
    if n < 100:
        t, o = divmod(n, 10)
        return digits[t] + "十" + (digits[o] if o else "")
    if n < 1000:
        h, rest = divmod(n, 100)
        s = digits[h] + "百"
        if rest:
            if rest < 10:
                s += "零" + digits[rest]
            else:
                s += _cn_number(rest)
        return s
    th, rest = divmod(n, 1000)
    s = digits[th] + "千"
    if rest:
        if rest < 100:
            s += "零" + _cn_number(rest)
        else:
            s += _cn_number(rest)
    return s


# ============================================================
# 易错模式库（可执行规则 + 层级关系 + 适用题型 + 多模板）
# ============================================================
PATTERNS: Dict[str, Dict[str, Any]] = {
    # ---------- 数与运算 ----------
    "carry_omitted": {
        "id": "carry_omitted", "name": "进位遗忘",
        "level": "computation_error", "theme": "arithmetic", "category": "procedural",
        "parent": None,
        "wrong_rule": "个位相加满十后忘记向十位进1",
        "correct_rule": "个位满十向十位进1，十位相加时加上进位的1",
        "applicable_types": ["mental_arithmetic", "vertical_calculation", "step_calculation"],
        "templates": ["add_carry", "add_carry_vertical"],
        "hint_prefix": "先看个位是否满十，满十要向十位进1",
    },
    "borrow_omitted": {
        "id": "borrow_omitted", "name": "退位遗忘",
        "level": "computation_error", "theme": "arithmetic", "category": "procedural",
        "parent": None,
        "wrong_rule": "个位不够减从十位退1后，十位忘记减1",
        "correct_rule": "个位不够减从十位退1当10，十位相应减1",
        "applicable_types": ["mental_arithmetic", "vertical_calculation", "step_calculation"],
        "templates": ["sub_borrow", "sub_borrow_vertical"],
        "hint_prefix": "个位不够减时，要从十位退1，先看十位怎么变",
    },
    "sign_confusion": {
        "id": "sign_confusion", "name": "符号混淆",
        "level": "computation_error", "theme": "arithmetic", "category": "logic",
        "parent": None,
        "wrong_rule": "把加减符号看错或运算顺序颠倒",
        "correct_rule": "按题干符号与运算顺序（先乘除后加减）计算",
        "applicable_types": ["mental_arithmetic", "step_calculation"],
        "templates": ["add_sub_mixed"],
        "hint_prefix": "先确认题目是加还是减，再按顺序计算",
    },
    "order_of_operations": {
        "id": "order_of_operations", "name": "运算顺序错",
        "level": "computation_error", "theme": "arithmetic", "category": "logic",
        "parent": None,
        "wrong_rule": "不按先乘除后加减、先括号内的顺序计算",
        "correct_rule": "先算括号内，再乘除，最后加减",
        "applicable_types": ["step_calculation", "composite_expression"],
        "templates": ["mixed_ops", "composite_expression"],
        "hint_prefix": "有括号先算括号，再算乘除，最后算加减",
    },
    "multiplication_error": {
        "id": "multiplication_error", "name": "口诀记错",
        "level": "computation_error", "theme": "arithmetic", "category": "calculation",
        "parent": None,
        "wrong_rule": "乘法口诀记错或记反",
        "correct_rule": "牢记乘法口诀，先确定因数再得积",
        "applicable_types": ["mental_arithmetic", "vertical_calculation"],
        "templates": ["mul", "vertical_mul"],
        "hint_prefix": "想一想乘法口诀，两个因数对应哪句口诀",
    },
    "remainder_not_less": {
        "id": "remainder_not_less", "name": "余数不小于除数",
        "level": "computation_error", "theme": "arithmetic", "category": "logic",
        "parent": None,
        "wrong_rule": "余数大于或等于除数仍直接写出",
        "correct_rule": "余数必须小于除数，否则继续分",
        "applicable_types": ["mental_arithmetic"],
        "templates": ["div_remainder"],
        "hint_prefix": "检查余数是不是比除数小",
    },
    # ---------- 分数 ----------
    "fraction_rat_vs_quantity": {
        "id": "fraction_rat_vs_quantity", "name": "量率混淆",
        "level": "misconception", "theme": "fraction", "category": "conceptual",
        "parent": None,
        "wrong_rule": "把'每段占全长的分率'与'每段的实际长度'混淆",
        "correct_rule": "分率是把整体看作1，长度是具体数量，要区分是求'分率'还是求'长度'",
        "applicable_types": ["mental_arithmetic", "word_problem"],
        "templates": ["fraction_ratio"],
        "hint_prefix": "先问清楚：这题是求'占全长的几分之几'还是求'每段长多少'",
    },
    "fraction_no_invert": {
        "id": "fraction_no_invert", "name": "分数除法不颠倒",
        "level": "misconception", "theme": "fraction", "category": "procedural",
        "parent": None,
        "wrong_rule": "除以一个分数时直接相乘，忘记把除数颠倒(取倒数)",
        "correct_rule": "除以一个数等于乘以它的倒数",
        "applicable_types": ["mental_arithmetic", "word_problem"],
        "templates": ["frac_div"],
        "hint_prefix": "除法变乘法时，除数要颠倒分子分母",
    },
    "fraction_add_bypart": {
        "id": "fraction_add_bypart", "name": "分子分母分别加减",
        "level": "misconception", "theme": "fraction", "category": "conceptual",
        "parent": None,
        "wrong_rule": "分数相加减时分子加分子、分母加分母，忘记通分",
        "correct_rule": "先通分成同分母，再分母不变、分子相加减",
        "applicable_types": ["mental_arithmetic", "step_calculation"],
        "templates": ["frac_add"],
        "hint_prefix": "分数加减要先通分，分母一样了才能加分子",
    },
    # ---------- 小数 ----------
    "decimal_align": {
        "id": "decimal_align", "name": "小数点不对齐",
        "level": "misconception", "theme": "decimal", "category": "conceptual",
        "parent": None,
        "wrong_rule": "小数加减按末位对齐而非小数点对齐",
        "correct_rule": "小数加减要把小数点对齐，再按整数加减",
        "applicable_types": ["mental_arithmetic", "vertical_calculation"],
        "templates": ["dec_add", "dec_sub"],
        "hint_prefix": "列竖式时小数点要对齐",
    },
    "decimal_point_shift": {
        "id": "decimal_point_shift", "name": "小数点位置错",
        "level": "computation_error", "theme": "decimal", "category": "calculation",
        "parent": None,
        "wrong_rule": "乘除时小数点移动位数错误",
        "correct_rule": "乘10/100/1000小数点右移对应位，除则左移",
        "applicable_types": ["mental_arithmetic", "vertical_calculation"],
        "templates": ["dec_mul", "dec_div"],
        "hint_prefix": "小数点移动的位数要和0的个数一致",
    },
    # ---------- 几何与测量 ----------
    "perimeter_area_confusion": {
        "id": "perimeter_area_confusion", "name": "周长面积混淆",
        "level": "misconception", "theme": "geometry", "category": "conceptual",
        "parent": None,
        "wrong_rule": "把周长公式与面积公式混淆使用",
        "correct_rule": "周长是围一圈的长度(长度单位)，面积是表面的大小(面积单位)",
        "applicable_types": ["perimeter_area", "word_problem"],
        "templates": ["rect_perimeter_area", "square_perimeter_area"],
        "hint_prefix": "分清求的是周长（一圈有多长）还是面积（表面有多大）",
    },
    "half_circle_missing_diameter": {
        "id": "half_circle_missing_diameter", "name": "半圆周长漏直径",
        "level": "computation_error", "theme": "geometry", "category": "missing_step",
        "parent": None,
        "wrong_rule": "半圆周长只算圆弧长度，漏加直径",
        "correct_rule": "半圆周长 = 圆弧长 + 直径",
        "applicable_types": ["perimeter_area", "word_problem"],
        "templates": ["half_circle"],
        "hint_prefix": "半圆是围起来的，除了弯的弧，还有一条直的直径",
    },
    "area_no_square_unit": {
        "id": "area_no_square_unit", "name": "面积单位漏平方",
        "level": "computation_error", "theme": "geometry", "category": "missing_step",
        "parent": None,
        "wrong_rule": "计算面积时单位写成'厘米'而非'平方厘米'",
        "correct_rule": "面积单位要用平方单位(平方米/平方厘米)",
        "applicable_types": ["perimeter_area", "unit_conversion"],
        "templates": ["rect_perimeter_area"],
        "hint_prefix": "面积的结果后面单位要带'平方'",
    },
    # ---------- 比与比例 ----------
    "ratio_vs_area_ratio": {
        "id": "ratio_vs_area_ratio", "name": "半径比当面积比",
        "level": "misconception", "theme": "proportion", "category": "conceptual",
        "parent": None,
        "wrong_rule": "把长度比(半径比)直接当成面积比",
        "correct_rule": "相似图形面积比 = 对应长度比的平方",
        "applicable_types": ["word_problem", "mental_arithmetic"],
        "templates": ["ratio_area"],
        "hint_prefix": "面积比是长度比的平方，不是直接相等",
    },
    "proportional_misjudge": {
        "id": "proportional_misjudge", "name": "正反比例误判",
        "level": "misconception", "theme": "proportion", "category": "conceptual",
        "parent": None,
        "wrong_rule": "把正比例与反比例关系混淆",
        "correct_rule": "成正比(比值一定)还是成反比(乘积一定)要看两个量的关系",
        "applicable_types": ["word_problem", "mental_arithmetic"],
        "templates": ["proportion_judge"],
        "hint_prefix": "判断成正反比：成正比看比值，成反比看乘积",
    },
    # ---------- 量与单位 ----------
    "unit_conversion_factor": {
        "id": "unit_conversion_factor", "name": "单位换算倍数错",
        "level": "computation_error", "theme": "unit", "category": "calculation",
        "parent": None,
        "wrong_rule": "单位换算时进率(倍数)用错",
        "correct_rule": "先确定两个单位间的进率，再乘或除",
        "applicable_types": ["unit_conversion", "word_problem"],
        "templates": ["unit_convert"],
        "hint_prefix": "先想清楚这两个单位之间的进率是多少",
    },
    "unit_omitted": {
        "id": "unit_omitted", "name": "漏写单位",
        "level": "computation_error", "theme": "unit", "category": "missing_step",
        "parent": None,
        "wrong_rule": "计算结果漏写单位或单位不统一",
        "correct_rule": "结果要带正确单位，且统一单位再计算",
        "applicable_types": ["unit_conversion", "word_problem"],
        "templates": ["unit_convert", "word_problem_unit"],
        "hint_prefix": "最后的结果要记得写单位",
    },
    # ---------- 数量关系 / 应用题 ----------
    "quantity_relation_error": {
        "id": "quantity_relation_error", "name": "数量关系错误",
        "level": "misconception", "theme": "arithmetic", "category": "semantic",
        "parent": None,
        "wrong_rule": "应用题中单位1/数量关系理解错误",
        "correct_rule": "先找出单位1与所求量之间的关系，再列式",
        "applicable_types": ["word_problem", "composite_expression"],
        "templates": ["word_problem_relation"],
        "hint_prefix": "先想想'谁是谁的几倍/几分之几'，单位1是哪个",
    },
    "keyword_shortcut": {
        "id": "keyword_shortcut", "name": "关键词捷径",
        "level": "misconception", "theme": "arithmetic", "category": "semantic",
        "parent": None,
        "wrong_rule": "只看关键词(如'多''少''一共')机械决定运算，不看数量关系",
        "correct_rule": "理解题意后再判断用加还是减/乘还是除",
        "applicable_types": ["word_problem"],
        "templates": ["word_problem_keyword"],
        "hint_prefix": "不要只看'多''少'两个字，要理解整句话的意思",
    },
    # ---------- 新增：补齐缺失题型（QA 问题 A） ----------
    "oral_counting_error": {
        "id": "oral_counting_error", "name": "数数漏首尾",
        "level": "computation_error", "theme": "number_sense", "category": "calculation",
        "parent": None,
        "wrong_rule": "数个数时漏数端点的第一个数",
        "correct_rule": "求总共几个数用 '大数 - 小数 + 1'",
        "applicable_types": ["oral_counting"],
        "templates": ["oral_counting"],
        "hint_prefix": "从 a 数到 b，别忘了把 a 自己也算进去",
    },
    "number_read_write_error": {
        "id": "number_read_write_error", "name": "读数写数数位错",
        "level": "misconception", "theme": "number_sense", "category": "conceptual",
        "parent": None,
        "wrong_rule": "把中文读法转成数字时数位写错",
        "correct_rule": "个位在右，十位在左，依次写出",
        "applicable_types": ["number_read_write"],
        "templates": ["number_read_write"],
        "hint_prefix": "把中文读法按十位、个位的位置写下来",
    },
    "number_composition_error": {
        "id": "number_composition_error", "name": "数的组成错",
        "level": "misconception", "theme": "number_sense", "category": "conceptual",
        "parent": None,
        "wrong_rule": "几个十几个一的组成关系算错",
        "correct_rule": "几个十是几十，几个一是几，加在一起",
        "applicable_types": ["number_composition"],
        "templates": ["number_composition"],
        "hint_prefix": "先数有几个十，再数有几个一",
    },
    "compare_size_error": {
        "id": "compare_size_error", "name": "比较方向错",
        "level": "misconception", "theme": "number_sense", "category": "logic",
        "parent": None,
        "wrong_rule": "把大于小于号填反方向",
        "correct_rule": "开口朝大数，尖角朝小数",
        "applicable_types": ["compare_size"],
        "templates": ["compare_size"],
        "hint_prefix": "想一想 '>' 的开口对着大的那个数",
    },
    "pattern_sequence_error": {
        "id": "pattern_sequence_error", "name": "规律误判",
        "level": "misconception", "theme": "number_sense", "category": "logic",
        "parent": None,
        "wrong_rule": "把等差数列的规律看错，填成上一个数",
        "correct_rule": "相邻两个数的差不变，用上一个数加差得到下一个",
        "applicable_types": ["pattern_sequence"],
        "templates": ["pattern_sequence"],
        "hint_prefix": "先看相邻两个数相差多少，再继续加",
    },
    "shape_counting_error": {
        "id": "shape_counting_error", "name": "图形计数漏数",
        "level": "misconception", "theme": "geometry", "category": "missing_step",
        "parent": None,
        "wrong_rule": "数图形时漏数某一种图形",
        "correct_rule": "分类数，每种图形分别数完再相加",
        "applicable_types": ["shape_counting"],
        "templates": ["shape_counting"],
        "hint_prefix": "先数三角形，再数正方形，别漏",
    },
    "chart_analysis_error": {
        "id": "chart_analysis_error", "name": "图表读数错",
        "level": "misconception", "theme": "statistics", "category": "semantic",
        "parent": None,
        "wrong_rule": "读统计表时把数量关系算反",
        "correct_rule": "先看统计表里每个数量，再判断用加还是减",
        "applicable_types": ["chart_analysis"],
        "templates": ["chart_analysis"],
        "hint_prefix": "在统计表里分别找到两个数量再看关系",
    },
    "angle_measurement_error": {
        "id": "angle_measurement_error", "name": "角度相加错",
        "level": "computation_error", "theme": "geometry", "category": "calculation",
        "parent": None,
        "wrong_rule": "把两个角的度数相减而不是相加",
        "correct_rule": "求两个角合起来是多少，用加法",
        "applicable_types": ["angle_measurement"],
        "templates": ["angle_measurement"],
        "hint_prefix": "合起来是共有的角，用加法",
    },
    "percentage_error": {
        "id": "percentage_error", "name": "百分数小数点错",
        "level": "computation_error", "theme": "arithmetic", "category": "calculation",
        "parent": None,
        "wrong_rule": "求一个数的百分之几时小数点位置错",
        "correct_rule": "百分数化成小数后再相乘",
        "applicable_types": ["percentage"],
        "templates": ["percentage"],
        "hint_prefix": "把百分数先化成小数，再相乘",
    },
    "solve_equation_error": {
        "id": "solve_equation_error", "name": "移项符号错",
        "level": "computation_error", "theme": "algebra", "category": "logic",
        "parent": None,
        "wrong_rule": "解方程移项时忘记变号",
        "correct_rule": "等式两边同时减去同一个数，两边仍相等",
        "applicable_types": ["solve_equation"],
        "templates": ["solve_equation"],
        "hint_prefix": "两边同时减去同一个数，x 就求出来了",
    },
    "simplified_calculation_error": {
        "id": "simplified_calculation_error", "name": "简便计算滥用",
        "level": "computation_error", "theme": "arithmetic", "category": "logic",
        "parent": None,
        "wrong_rule": "没有凑整就乱用结合律，改变运算顺序",
        "correct_rule": "先把能凑成整百的数结合，再相加",
        "applicable_types": ["simplified_calculation"],
        "templates": ["simplified_calc"],
        "hint_prefix": "先找哪两个数能凑成整百",
    },
    "verification_error": {
        "id": "verification_error", "name": "验算方法错",
        "level": "computation_error", "theme": "arithmetic", "category": "procedural",
        "parent": None,
        "wrong_rule": "验算时用了错误的逆运算",
        "correct_rule": "加法用减法验算，和减一个加数应等于另一个加数",
        "applicable_types": ["verification"],
        "templates": ["verification"],
        "hint_prefix": "加法算完用减法再验算一遍",
    },
    "estimation_error": {
        "id": "estimation_error", "name": "估算取整错",
        "level": "computation_error", "theme": "number_sense", "category": "calculation",
        "parent": None,
        "wrong_rule": "估算时把结果写成精确值",
        "correct_rule": "先把数看成接近的整十整百，再口算",
        "applicable_types": ["estimation"],
        "templates": ["estimation"],
        "hint_prefix": "先把数看成接近的整十整百再算",
    },
    "math_puzzle_error": {
        "id": "math_puzzle_error", "name": "植树问题漏端点",
        "level": "misconception", "theme": "arithmetic", "category": "missing_step",
        "parent": None,
        "wrong_rule": "植树问题时漏算端点上的一棵",
        "correct_rule": "从头到尾种，棵数 = 间隔数 + 1",
        "applicable_types": ["math_puzzle"],
        "templates": ["math_puzzle"],
        "hint_prefix": "从头到尾种树，棵数比间隔数多 1",
    },
    "fill_unknown_error": {
        "id": "fill_unknown_error", "name": "填未知数错",
        "level": "computation_error", "theme": "arithmetic", "category": "calculation",
        "parent": None,
        "wrong_rule": "求未知加数时用错加减关系",
        "correct_rule": "未知加数 = 和 - 已知加数",
        "applicable_types": ["fill_unknown"],
        "templates": ["fill_unknown"],
        "hint_prefix": "求括号里的数，用和减去已知的加数",
    },
    "composite_expression_error": {
        "id": "composite_expression_error", "name": "列综合算式错",
        "level": "misconception", "theme": "arithmetic", "category": "logic",
        "parent": None,
        "wrong_rule": "合并算式时运算顺序写错",
        "correct_rule": "先算的部分要加括号，再按顺序合并",
        "applicable_types": ["composite_expression"],
        "templates": ["composite_expression"],
        "hint_prefix": "先算哪一步，那一部分就要保留运算顺序",
    },
}


# ============================================================
# 主题 → 知识点路由（仅在知识点未声明 types 时兜底）
# ============================================================
def _route_patterns(kp_name: str) -> List[str]:
    """根据知识点名称返回适用的易错模式 id 列表（兜底）"""
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


def _keyword_question_type(kp_name: str) -> str:
    """根据知识点名称推断题型（兜底，仅供无 types 声明时使用）"""
    name = kp_name
    if "应用题" in name or "解决问题" in name:
        return "word_problem"
    if "面积" in name or "周长" in name:
        return "perimeter_area"
    if "单位" in name or "人民币" in name or "克" in name or "吨" in name:
        return "unit_conversion"
    if "除法" in name:
        return "mental_arithmetic"
    if "解方程" in name or "方程" in name:
        return "solve_equation"
    if "规律" in name or "找规律" in name:
        return "pattern_sequence"
    if "图形" in name or "三角形" in name or "正方形" in name:
        return "shape_counting"
    if "统计" in name or "图表" in name or "钟表" in name:
        return "chart_analysis"
    if "百分" in name:
        return "percentage"
    if "简便" in name or "定律" in name:
        return "simplified_calculation"
    if "分数" in name or "小数" in name or "乘法" in name or "内" in name or "加法" in name or "减法" in name:
        return "mental_arithmetic"
    return "mental_arithmetic"


# ============================================================
# 模板生成函数（参数化，返回 stem/answer/solution 及步骤）
# ============================================================
def _tpl_add_carry(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a, b = _grade_add_pair(grade)
    correct = a + b
    ones = (a % 10) + (b % 10)
    carry = "满十" if ones >= 10 else "不满十"
    wrong = correct - 10  # 忘记进位
    stem = f"{a} + {b} = ___"
    steps = [
        {"step": f"先算个位 {a % 10} + {b % 10} = {ones}（{carry}）", "is_error_point": False},
        {"step": f"再算十位 {a // 10} + {b // 10}" + (f"（满十进1记得加1）" if carry == "满十" else ""), "is_error_point": carry == "满十"},
        {"step": f"结果为 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} + {b} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_vertical_add(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a, b = _grade_add_pair(grade)
    correct = a + b
    wrong = correct - 10
    stem = f"用竖式计算：{a} + {b} = ___"
    steps = [
        {"step": "相同数位对齐，从个位加起", "is_error_point": False},
        {"step": f"个位 {a % 10} + {b % 10}，满十向十位进1", "is_error_point": True},
        {"step": f"结果为 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} + {b} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_sub_borrow(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a, b = _grade_sub_pair(grade)
    correct = a - b
    wrong = correct + 1  # 忘记十位减1
    stem = f"{a} - {b} = ___"
    needs_borrow = (a % 10) < (b % 10)
    steps = [
        {"step": f"个位 {a % 10} - {b % 10}" + ("，不够减，从十位退1" if needs_borrow else ""), "is_error_point": needs_borrow},
        {"step": f"从十位退1后，十位要减1（{a // 10} 变 {a // 10 - 1}）" if needs_borrow else f"十位 {a // 10} - {b // 10}", "is_error_point": needs_borrow},
        {"step": f"结果为 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} - {b} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_vertical_sub(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a, b = _grade_sub_pair(grade)
    correct = a - b
    wrong = correct + 1
    stem = f"用竖式计算：{a} - {b} = ___"
    steps = [
        {"step": "相同数位对齐，从个位减起", "is_error_point": False},
        {"step": f"个位 {a % 10} - {b % 10} 不够减，从十位退1当10", "is_error_point": True},
        {"step": f"结果为 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} - {b} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_add_sub_mixed(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
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
    steps = [
        {"step": f"确认符号：{'减法' if a > b else '加法'}", "is_error_point": False},
        {"step": f"按位计算得 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} {'-' if a > b else '+'} {b} = {correct}",
        "wrong_value": str(wrong1), "wrong2": str(wrong2), "steps": steps,
    }


def _tpl_mixed_ops(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = random.randint(2, 12)
    b = random.randint(2, 12)
    c = random.randint(2, 12)
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


def _tpl_composite_expression(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = random.randint(2, 9)
    b = random.randint(3, 9)
    c = random.randint(2, 9)
    mid = a * b
    correct = mid + c
    wrong = (a + b) * c  # 乱加括号改变顺序
    stem = f"把下面两个算式合并成一个综合算式：\n{a} × {b} = {mid}，{mid} + {c} = ___"
    steps = [
        {"step": f"先算 {a} × {b} = {mid}", "is_error_point": False},
        {"step": f"再用 {mid} + {c} = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} × {b} + {c} = {mid} + {c} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_fraction_ratio(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
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


def _tpl_frac_div(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    # a 从 2 开始：除数需 >1，否则「不颠倒直接乘」的误解与正确答案相同，失去区分度
    a = random.randint(2, 5)
    b = random.randint(2, 5)
    stem = f"{a}/{b} ÷ {a} = ___"
    correct = f"1/{b}"
    wrong = f"{a * a}/{b}"  # 不颠倒直接乘：a/b × a = a²/b
    if wrong == correct:
        wrong = f"{a * a}/({b} × {a})"
    steps = [
        {"step": f"除法变乘法，除数 {a} 变 1/{a}：{a}/{b} × 1/{a}", "is_error_point": True},
        {"step": f"分子分母约分：{a} 与 {a} 约掉，得 1/{b}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": correct,
        "solution": f"{a}/{b} ÷ {a} = {a}/{b} × 1/{a} = 1/{b}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_frac_add(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
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


def _tpl_dec_add(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = round(random.uniform(1.0, 9.9), 2)
    b = round(random.uniform(1.0, 9.9), 2)
    correct = round(a + b, 2)
    wrong = round(a + b, 1)
    if wrong == correct:
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


def _tpl_dec_mul(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = round(random.uniform(1.0, 9.9), 2)
    b = random.choice([10, 100])
    correct = round(a * b, 2)
    wrong = round(a * b / 10, 2)  # 少移一位
    if wrong == correct:
        wrong = round(a * b * 10, 2)
    stem = f"{a} × {b} = ___"
    steps = [
        {"step": f"×{b} 小数点向右移动 {len(str(b)) - 1} 位", "is_error_point": True},
        {"step": f"结果为 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} × {b} = {correct}",
        "wrong_value": str(wrong), "steps": steps,
    }


def _tpl_rect_perimeter_area(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
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


def _tpl_half_circle(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    r = random.randint(3, 10)
    arc = round(3.14 * r, 2)
    diameter = 2 * r
    correct = round(arc + diameter, 2)
    wrong = arc  # 漏直径
    stem = f"一个半圆半径是{r}厘米，求半圆的周长（π取3.14）"
    steps = [
        {"step": f"弧长 = π×r = 3.14×{r} = {arc}", "is_error_point": False},
        {"step": "半圆周长 = 弧长 + 直径，别忘了加直径", "is_error_point": True},
        {"step": f"{arc} + {diameter} = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": f"{correct}厘米",
        "solution": f"C = 3.14×{r} + 2×{r} = {correct}厘米",
        "wrong_value": f"{wrong}厘米", "steps": steps,
    }


# 单位换算（按年级选择合适进率）
_GRADE_CONVERSIONS = {
    "一年级": [("元", "角", 10), ("角", "分", 10)],
    "二年级": [("米", "厘米", 100), ("元", "角", 10), ("克", "千克", 1000), ("厘米", "米", 100)],
    "三年级": [("千米", "米", 1000), ("小时", "分钟", 60), ("分钟", "秒", 60), ("吨", "千克", 1000), ("年", "月", 12)],
    "四年级": [("平方米", "平方分米", 100), ("平方千米", "公顷", 100), ("公顷", "平方米", 10000)],
    "五年级": [("立方分米", "立方厘米", 1000), ("升", "毫升", 1000), ("平方米", "平方厘米", 10000)],
    "六年级": [("立方分米", "立方厘米", 1000), ("升", "毫升", 1000), ("千米", "米", 1000)],
}
_ALL_CONVERSIONS = [
    ("米", "厘米", 100), ("千米", "米", 1000), ("元", "角", 10),
    ("小时", "分钟", 60), ("年", "月", 12), ("吨", "千克", 1000),
    ("平方米", "平方分米", 100), ("克", "千克", 1000),
]


def _tpl_unit_convert(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    pool = _GRADE_CONVERSIONS.get(grade) or _ALL_CONVERSIONS
    unit1, unit2, factor = random.choice(pool)
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


def _tpl_mul(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
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


def _tpl_vertical_mul(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    if grade in ("四年级", "五年级", "六年级"):
        a, b = random.randint(100, 999), random.randint(10, 99)   # 三位数×两位数
    elif grade in ("二年级", "三年级"):
        a, b = random.randint(10, 99), random.randint(2, 9)       # 两位数×一位数
    else:
        a, b = random.randint(2, 9), random.randint(2, 9)
    correct = a * b
    wrong = correct + a  # 口诀错
    stem = f"用竖式计算：{a} × {b} = ___"
    steps = [
        {"step": "相同数位对齐，从个位乘起", "is_error_point": False},
        {"step": f"用 {b} 依次乘 {a} 的每一位，注意进位", "is_error_point": True},
        {"step": f"结果为 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} × {b} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_div_remainder(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
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


def _tpl_ratio_area(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    r1 = random.randint(2, 5)
    r2 = r1 + random.randint(1, 3)
    correct = f"{r1 * r1}:{r2 * r2}"
    wrong = f"{r1}:{r2}"
    stem = f"大圆半径和小圆半径比是{r1}:{r2}，大圆和小圆面积比是多少？"
    steps = [
        {"step": f"面积比 = 半径比² = {r1}²:{r2}² = {r1 * r1}:{r2 * r2}", "is_error_point": True},
    ]
    return {
        "stem": stem, "answer": correct,
        "solution": f"面积比 = {r1}²:{r2}² = {r1 * r1}:{r2 * r2}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_proportion_judge(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    stem = "判断：圆的半径和周长成什么比例？"
    correct = "正比例"
    solution = "C = 2πr，C/r = 2π（定值），所以成正比例"
    wrong = "反比例"
    steps = [
        {"step": "写关系式：C = 2πr", "is_error_point": False},
        {"step": "看 C 与 r 的比：C/r = 2π 是定值 → 正比例", "is_error_point": True},
    ]
    return {
        "stem": stem, "answer": correct, "solution": solution,
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_word_problem_relation(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
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


def _tpl_word_problem_keyword(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
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


# ============================================================
# 新增题型模板（补齐 22 种声明题型）
# ============================================================
def _tpl_oral_counting(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = random.randint(1, 9)
    b = a + random.randint(3, 9)
    correct = b - a + 1
    wrong = b - a  # 漏首
    stem = f"从{a}数到{b}，一共有几个数？"
    steps = [
        {"step": f"从 {a} 数到 {b}，注意把 {a} 也算进去", "is_error_point": True},
        {"step": f"{b} - {a} + 1 = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{b} - {a} + 1 = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_number_read_write(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    tens = random.randint(1, 9)
    ones = random.randint(0, 9)
    num = tens * 10 + ones
    cn = _cn_number(num)
    stem = f"写出下面各数：{cn} 写作（___）"
    answer = str(num)
    wrong = str(num + 10)
    if wrong == answer:
        wrong = str(num - 10)
    steps = [
        {"step": f"{cn}，十位是 {tens}，个位是 {ones}", "is_error_point": False},
        {"step": f"写作 {num}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": answer,
        "solution": f"{cn} = {num}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_number_composition(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    tens = random.randint(1, 9)
    ones = random.randint(0, 9)
    num = tens * 10 + ones
    stem = f"{tens}个十和{ones}个一组成的数是（___）"
    answer = str(num)
    wrong = str(num + 10)
    if wrong == answer:
        wrong = str(num - 10)
    steps = [
        {"step": f"{tens}个十是 {tens * 10}", "is_error_point": False},
        {"step": f"再加 {ones} 个一：{tens * 10} + {ones} = {num}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": answer,
        "solution": f"{tens}×10 + {ones} = {num}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_compare_size(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = random.randint(1, 99)
    b = random.randint(1, 99)
    if a == b:
        b += 1
    sign = ">" if a > b else "<"
    wrong = "<" if sign == ">" else ">"
    stem = f"在○里填上“＞”“＜”或“＝”：{a} ○ {b}"
    steps = [
        {"step": f"比较 {a} 和 {b}：{a} {sign} {b}", "is_error_point": False},
        {"step": f"开口朝大的数 {max(a, b)}", "is_error_point": True},
    ]
    return {
        "stem": stem, "answer": sign,
        "solution": f"{a} {sign} {b}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_pattern_sequence(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    start = random.randint(1, 5)
    step = random.randint(2, 5)
    seq = [start + step * i for i in range(4)]
    correct = seq[3]
    wrong = seq[2]  # 填成上一个数
    stem = f"找规律，填一填：{seq[0]}, {seq[1]}, {seq[2]}, ___"
    steps = [
        {"step": f"相邻两个数相差 {step}", "is_error_point": False},
        {"step": f"{seq[2]} + {step} = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{seq[0]}, {seq[1]}, {seq[2]}, {correct}（每次加 {step}）",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_shape_counting(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = random.randint(2, 6)
    b = random.randint(2, 6)
    correct = a + b
    wrong = b  # 漏数三角形
    stem = f"数一数：三角形有{a}个，正方形有{b}个，图形一共有（___）个。"
    steps = [
        {"step": f"先数三角形 {a} 个，再数正方形 {b} 个", "is_error_point": False},
        {"step": f"一共 {a} + {b} = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} + {b} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_chart_analysis(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    if random.random() < 0.5:
        correct = a + b
        stem = f"统计表中苹果有{a}个，梨有{b}个，苹果和梨一共有（___）个。"
        wrong = max(a, b) - min(a, b)
    else:
        hi, lo = max(a, b), min(a, b)
        correct = hi - lo
        stem = f"统计表中苹果有{hi}个，梨有{lo}个，苹果比梨多（___）个。"
        wrong = hi + lo
    steps = [
        {"step": f"从统计表里读出两个数量", "is_error_point": False},
        {"step": f"判断关系后计算得 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"答案为 {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_angle_measurement(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = random.randint(20, 80)
    b = random.randint(20, 90 - a if a < 90 else 10)
    correct = a + b
    wrong = abs(a - b)  # 误用减法
    stem = f"一个角是{a}°，另一个角是{b}°，两个角合起来是（___）°。"
    steps = [
        {"step": "合起来用加法", "is_error_point": True},
        {"step": f"{a} + {b} = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} + {b} = {correct}°",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_percentage(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = random.randint(20, 200)
    p = random.choice([10, 20, 25, 50])
    correct = a * p // 100
    wrong = a * p // 1000  # 小数点错位
    if wrong == 0:
        wrong = correct + 1
    stem = f"{a} 的 {p}% 是多少？"
    steps = [
        {"step": f"把 {p}% 化成小数 {p / 100}", "is_error_point": False},
        {"step": f"{a} × {p / 100} = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} × {p}% = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_solve_equation(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    x = random.randint(2, 20)
    a = random.randint(1, 9)
    b = x + a
    stem = f"解方程：x + {a} = {b}"
    answer = str(x)
    wrong = str(x + 2 * a)  # 移项符号错
    steps = [
        {"step": f"等式两边同时减去 {a}", "is_error_point": False},
        {"step": f"x = {b} - {a} = {x}", "is_error_point": True},
    ]
    return {
        "stem": stem, "answer": answer,
        "solution": f"x = {b} - {a} = {x}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_simplified_calc(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = random.randint(20, 50)
    b = random.randint(20, 40)
    c = random.randint(60, 100 - (b % 100) if b % 100 else 80)
    correct = a + b + c
    wrong = (a + b) * (c // 10) if c // 10 else a + b  # 乱用结合律
    stem = f"用简便方法计算：{a} + {b} + {c}"
    steps = [
        {"step": f"把 {b} 和 {c} 结合凑整", "is_error_point": False},
        {"step": f"{a} + ({b} + {c}) = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} + {b} + {c} = {a} + ({b}+{c}) = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_verification(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = random.randint(100, 500)
    b = random.randint(100, 500)
    correct = a + b
    wrong = correct - 1
    stem = f"计算并验算：{a} + {b}"
    steps = [
        {"step": f"先算 {a} + {b} = {correct}", "is_error_point": False},
        {"step": f"验算：{correct} - {a} = {b}，与原式一致", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} + {b} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_estimation(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = random.randint(100, 900)
    b = random.randint(100, 900)
    exact = a + b
    correct = round(exact, -2)
    wrong = exact
    stem = f"估算：{a} + {b} ≈ ___"
    steps = [
        {"step": f"把 {a} 看成接近的整百，把 {b} 看成接近的整百", "is_error_point": False},
        {"step": f"估算结果约为 {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a} + {b} ≈ {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_math_puzzle(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = random.randint(20, 60)
    b = random.randint(5, 10)
    correct = a // b + 1
    wrong = a // b  # 漏端点
    stem = f"在一条{a}米长的路的一边从头到尾种树，每隔{b}米种一棵，一共要种（___）棵。"
    steps = [
        {"step": f"间隔数 = {a} ÷ {b} = {a // b}", "is_error_point": False},
        {"step": "从头到尾种，棵数 = 间隔数 + 1", "is_error_point": True},
        {"step": f"{a // b} + 1 = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{a}÷{b} + 1 = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


def _tpl_fill_unknown(grade: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
    a = random.randint(2, 20)
    correct = random.randint(2, 20)
    b = a + correct
    stem = f"{a} + (  ) = {b}"
    wrong = b - correct + 1
    if wrong == correct:
        wrong = correct + 1
    steps = [
        {"step": f"求未知加数：{b} - {a} = {correct}", "is_error_point": False},
    ]
    return {
        "stem": stem, "answer": str(correct),
        "solution": f"{b} - {a} = {correct}",
        "wrong_value": wrong, "steps": steps,
    }


# 模板分发表
TEMPLATES = {
    "add_carry": _tpl_add_carry,
    "add_carry_vertical": _tpl_vertical_add,
    "sub_borrow": _tpl_sub_borrow,
    "sub_borrow_vertical": _tpl_vertical_sub,
    "add_sub_mixed": _tpl_add_sub_mixed,
    "mixed_ops": _tpl_mixed_ops,
    "composite_expression": _tpl_composite_expression,
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
    "vertical_mul": _tpl_vertical_mul,
    "div_remainder": _tpl_div_remainder,
    "oral_counting": _tpl_oral_counting,
    "number_read_write": _tpl_number_read_write,
    "number_composition": _tpl_number_composition,
    "compare_size": _tpl_compare_size,
    "pattern_sequence": _tpl_pattern_sequence,
    "shape_counting": _tpl_shape_counting,
    "chart_analysis": _tpl_chart_analysis,
    "angle_measurement": _tpl_angle_measurement,
    "percentage": _tpl_percentage,
    "solve_equation": _tpl_solve_equation,
    "simplified_calc": _tpl_simplified_calc,
    "verification": _tpl_verification,
    "estimation": _tpl_estimation,
    "math_puzzle": _tpl_math_puzzle,
    "fill_unknown": _tpl_fill_unknown,
}

# 每个模板产出哪种题型（用于类型驱动的模板选择）
TEMPLATE_TYPES = {
    "add_carry": "mental_arithmetic", "add_carry_vertical": "vertical_calculation",
    "sub_borrow": "mental_arithmetic", "sub_borrow_vertical": "vertical_calculation",
    "add_sub_mixed": "mental_arithmetic", "mixed_ops": "step_calculation",
    "composite_expression": "composite_expression",
    "fraction_ratio": "word_problem", "frac_div": "mental_arithmetic",
    "frac_add": "step_calculation",
    "dec_add": "mental_arithmetic", "dec_sub": "mental_arithmetic",
    "dec_mul": "mental_arithmetic", "dec_div": "mental_arithmetic",
    "rect_perimeter_area": "perimeter_area", "square_perimeter_area": "perimeter_area",
    "half_circle": "perimeter_area", "unit_convert": "unit_conversion",
    "word_problem_unit": "word_problem", "ratio_area": "word_problem",
    "proportion_judge": "word_problem", "word_problem_relation": "word_problem",
    "word_problem_keyword": "word_problem", "mul": "mental_arithmetic",
    "vertical_mul": "vertical_calculation", "div_remainder": "mental_arithmetic",
    "oral_counting": "oral_counting", "number_read_write": "number_read_write",
    "number_composition": "number_composition", "compare_size": "compare_size",
    "pattern_sequence": "pattern_sequence", "shape_counting": "shape_counting",
    "chart_analysis": "chart_analysis", "angle_measurement": "angle_measurement",
    "percentage": "percentage", "solve_equation": "solve_equation",
    "simplified_calc": "simplified_calculation", "verification": "verification",
    "estimation": "estimation", "math_puzzle": "math_puzzle",
    "fill_unknown": "fill_unknown",
}

# 每个模板允许出现的年级白名单（None=不限制），杜绝跨年级污染
TEMPLATE_GRADE = {
    "fraction_ratio": ["三年级", "四年级", "五年级", "六年级"],
    "frac_div": ["三年级", "四年级", "五年级", "六年级"],
    "frac_add": ["三年级", "四年级", "五年级", "六年级"],
    "dec_add": ["三年级", "四年级", "五年级", "六年级"],
    "dec_sub": ["三年级", "四年级", "五年级", "六年级"],
    "dec_mul": ["四年级", "五年级", "六年级"],
    "dec_div": ["四年级", "五年级", "六年级"],
    "rect_perimeter_area": ["三年级", "四年级", "五年级", "六年级"],
    "square_perimeter_area": ["三年级", "四年级", "五年级", "六年级"],
    "half_circle": ["六年级"],
    "ratio_area": ["六年级"],
    "proportion_judge": ["六年级"],
    "percentage": ["六年级"],
    "solve_equation": ["五年级", "六年级"],
    "simplified_calc": ["四年级", "五年级", "六年级"],
    "verification": ["三年级", "四年级", "五年级", "六年级"],
    "estimation": ["二年级", "三年级", "四年级"],
    "math_puzzle": ["四年级", "五年级", "六年级"],
    "angle_measurement": ["二年级", "三年级", "四年级"],
    "composite_expression": ["三年级", "四年级", "五年级", "六年级"],
    "vertical_mul": ["三年级", "四年级", "五年级", "六年级"],
    "oral_counting": ["一年级"],
}


def _template_grade_ok(tpl_name: str, grade: Optional[str]) -> bool:
    """判断模板是否允许用于该年级"""
    if not grade:
        return True
    allowed = TEMPLATE_GRADE.get(tpl_name)
    if allowed is None:
        return True
    return grade in allowed


def _type_has_support(qtype: str, grade: Optional[str]) -> bool:
    """判断该题型在该年级下是否有可用的（模式+模板）"""
    for p in PATTERNS.values():
        if qtype not in p["applicable_types"]:
            continue
        for t in p["templates"]:
            if TEMPLATE_TYPES.get(t) == qtype and _template_grade_ok(t, grade):
                return True
    return False


def _call_tpl(tpl_fn, grade: Optional[str], semester: Optional[str]) -> Dict[str, Any]:
    """调用模板函数，仅向接受 grade/semester 的函数传递年级参数"""
    try:
        sig = inspect.signature(tpl_fn)
        params = sig.parameters
        if "grade" in params and "semester" in params:
            return tpl_fn(grade=grade, semester=semester)
    except (ValueError, TypeError):
        pass
    return tpl_fn()


def _choose_question_type(kp_name: str, kp_types: List[str], grade: Optional[str]) -> str:
    """选择目标题型：优先尊重知识点声明的 types，且只选该年级下可真正产出的题型"""
    if kp_types:
        # 只保留该年级有「模式+模板」支持的题型（严格年级白名单）
        pool = [t for t in kp_types if _type_has_support(t, grade)]
        if pool:
            return random.choice(pool)
        # 声明的题型在当前年级都无法产出时，退化为按知识点名称兜底
        return _keyword_question_type(kp_name)
    return _keyword_question_type(kp_name)


def _choose_template(pattern: Dict[str, Any], target_type: str, grade: Optional[str]) -> Optional[str]:
    """从模式中挑选产出目标题型且年级允许的模板；若无，返回 None（绝不越过年级白名单）"""
    cands = [t for t in pattern["templates"]
             if TEMPLATE_TYPES.get(t) == target_type and _template_grade_ok(t, grade)]
    if not cands:
        # 该模式没有产出目标题型且年级合法的模板 → 该模式对当前(题型,年级)不可用
        return None
    return random.choice(cands)


# ============================================================
# 结构化反馈组装
# ============================================================
def _build_feedback(pattern: Dict[str, Any], tpl: Dict[str, Any],
                    difficulty: int) -> Dict[str, Any]:
    """组装结构化反馈：错误类别、错误点、双路径、苏格拉底提示、干扰项映射"""
    steps = tpl.get("steps", [])
    error_step = None
    for s in steps:
        if s.get("is_error_point"):
            error_step = s["step"]
            break
    if error_step is None and steps:
        error_step = f"在第 {len(steps)} 步易出错"

    wrong_path_steps = [s["step"] for s in steps]

    socratic_hints = [
        pattern["hint_prefix"],
        f"用正确规则：{pattern['correct_rule']}",
        "再检查一遍你的每一步，看看是哪一步和你原来的做法不一样",
    ]

    wrong_value = tpl.get("wrong_value")
    wrong2 = tpl.get("wrong2")
    distractor_mapping = [
        {"value": str(wrong_value), "misconception": pattern["name"]},
    ]
    if wrong2:
        distractor_mapping.append({"value": str(wrong2), "misconception": "同类计算偏差"})

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
        "solution_status": "targeted",
        "enhanced_explanation": enhanced,
    }


# ============================================================
# 主入口
# ============================================================
def generate_question_with_errors(kp_id: str, kp_name: str, difficulty: int,
                                  kp: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """根据知识点生成带易错模式的题目（结构化输出）

    kp 为知识点字典（含 types/grade/semester），用于类型驱动 + 年级感知选题。
    不传 kp 时退化为按知识点名称兜底选题（保持向后兼容）。
    """
    kp_types = (kp or {}).get("types") or []
    grade = (kp or {}).get("grade")
    semester = (kp or {}).get("semester")

    # 1. 确定目标题型（尊重知识点声明，且年级可产出）
    target_type = _choose_question_type(kp_name, kp_types, grade)

    # 2. 选择支持该题型、且该年级下确有可用模板的易错模式
    pattern_ids = []
    for pid, p in PATTERNS.items():
        if target_type not in p["applicable_types"]:
            continue
        if _choose_template(p, target_type, grade) is not None:
            pattern_ids.append(pid)
    if not pattern_ids:
        # 兜底：按知识点名称路由（仍校验年级模板可用性）
        for pid in _route_patterns(kp_name):
            p = PATTERNS.get(pid)
            if p and _choose_template(p, target_type, grade) is not None:
                pattern_ids.append(pid)
    if not pattern_ids:
        # 极端兜底：任选一个在该年级可用的模式模板
        for p in PATTERNS.values():
            t = _choose_template(p, target_type, grade)
            if t is not None:
                pattern_ids.append(p["id"])
                break
    pid = random.choice(pattern_ids)
    pattern = PATTERNS[pid]

    # 3. 选择产物与目标题型一致、且年级允许的模板（此时必非 None）
    tpl_name = _choose_template(pattern, target_type, grade)
    tpl_fn = TEMPLATES[tpl_name]
    tpl = _call_tpl(tpl_fn, grade, semester)

    # 4. 组装结构化反馈
    fb = _build_feedback(pattern, tpl, difficulty)

    common_error = (
        f"{fb['error_category_label']}：{pattern['wrong_rule']}。"
        f"正确做法是：{pattern['correct_rule']}。"
    )

    return {
        "knowledge_point_id": kp_id,
        "question_type": target_type,
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