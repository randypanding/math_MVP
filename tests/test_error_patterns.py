"""自测：验证重构后的易错模式生成器（结构化输出）"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generator.error_patterns import (
    generate_question_with_errors,
    get_pattern_hierarchy,
    PATTERNS,
    TEMPLATES,
    CATEGORY_LABELS,
    TEMPLATE_GRADE,
    _tpl_angle_measurement,
    _tpl_dec_sub,
    _tpl_dec_div,
    _tpl_word_problem_relation,
    _tpl_word_problem_unit,
)

KP_CASES = [
    ("G1U01KP01", "20以内进位加法"),
    ("G1U02KP01", "20以内退位减法"),
    ("G2U04KP01", "表内乘法"),
    ("G2U07KP01", "有余数的除法"),
    ("G3U08KP01", "分数的初步认识"),
    ("G4U03KP01", "小数的意义和性质"),
    ("G3U05KP01", "长方形和正方形"),
    ("G6U04KP01", "比"),
    ("G2U03KP01", "100以内进位加法"),
    ("G5U02KP01", "小数乘法"),
]


def test_pattern_library():
    print("== 1. 易错模式库完整性 ==")
    assert len(PATTERNS) >= 15, f"模式数应>=15，实际{len(PATTERNS)}"
    # 每个模式字段齐全
    for pid, p in PATTERNS.items():
        for field in ["id", "name", "level", "theme", "category", "wrong_rule",
                      "correct_rule", "applicable_types", "templates", "hint_prefix"]:
            assert field in p, f"{pid} 缺少字段 {field}"
        assert p["level"] in ("computation_error", "misconception"), f"{pid} level非法"
        assert p["category"] in CATEGORY_LABELS, f"{pid} category非法"
        assert p["templates"], f"{pid} 无模板"
        for t in p["templates"]:
            assert t in TEMPLATES, f"{pid} 模板 {t} 未注册"
    # 层级分布：应同时含计算性错误与概念性误解
    levels = {p["level"] for p in PATTERNS.values()}
    assert levels == {"computation_error", "misconception"}, f"需同时含两层，实际{levels}"
    print(f"  通过：{len(PATTERNS)} 个易错模式，覆盖层级 {levels}")
    print(f"  错误类别覆盖：{sorted(set(p['category'] for p in PATTERNS.values()))}")


def test_hierarchy():
    print("== 2. 层级关系图 ==")
    tree = get_pattern_hierarchy()
    assert tree, "层级图为空"
    for theme, info in tree.items():
        assert "label" in info and info["patterns"]
    print(f"  通过：{len(tree)} 个主题，模式层级图可生成")


def test_generation():
    print("== 3. 题目生成（结构化输出）==")
    for kp_id, kp_name in KP_CASES:
        for _ in range(5):
            q = generate_question_with_errors(kp_id, kp_name, difficulty=2)
            # 基础字段
            for field in ["knowledge_point_id", "question_type", "stem", "answer",
                          "solution", "common_error", "difficulty", "review_status"]:
                assert field in q, f"{kp_name} 缺字段 {field}"
            assert q["stem"] and q["answer"], f"{kp_name} 题干/答案为空"
            # 结构化字段
            for field in ["error_category", "error_category_label", "pattern_id",
                          "pattern_name", "pattern_level", "theme", "theme_label",
                          "wrong_rule", "correct_rule", "wrong_value", "error_step",
                          "steps", "wrong_path", "socratic_hints", "distractor_mapping",
                          "solution_status", "enhanced_explanation"]:
                assert field in q, f"{kp_name} 缺结构化字段 {field}"
            # steps 必须是合法 JSON 且非空
            steps = json.loads(q["steps"])
            assert isinstance(steps, list) and len(steps) >= 1, f"{kp_name} steps非法"
            # socratic_hints 合法 JSON
            hints = json.loads(q["socratic_hints"])
            assert isinstance(hints, list) and len(hints) >= 1, f"{kp_name} hints非法"
            # distractor_mapping 合法
            dm = json.loads(q["distractor_mapping"])
            assert isinstance(dm, list) and dm, f"{kp_name} distractor非法"
            # 错误答案与正确答案不同
            assert q["wrong_value"] and str(q["wrong_value"]) != str(q["answer"]), \
                f"{kp_name} 错误答案与正确答案相同: {q['wrong_value']} vs {q['answer']}"
    print(f"  通过：{len(KP_CASES)} 个知识点 ×5 次生成，全部结构化字段完整且合法")


def test_example_output():
    print("== 4. 示例输出 ==")
    q = generate_question_with_errors("G3U08KP01", "分数的初步认识", difficulty=2)
    print(f"  题干: {q['stem']}")
    print(f"  答案: {q['answer']}")
    print(f"  易错类别: {q['error_category_label']}（{q['pattern_name']}）")
    print(f"  错误步骤: {q['error_step']}")
    print(f"  错误规则: {q['wrong_rule']}")
    print(f"  苏格拉底提示: {json.loads(q['socratic_hints'])}")
    print(f"  干扰项映射: {json.loads(q['distractor_mapping'])}")


def test_angle_template_no_crash():
    """Issue #1：_tpl_angle_measurement 在大量随机下不应抛空区间异常"""
    print("== 5. 角度模板空区间回归 ==")
    for _ in range(500):
        t = _tpl_angle_measurement()
        assert t["stem"] and t["answer"], "角度模板出生空结果"
    print("  500 次随机抽样均未崩溃 ✅")


def test_dec_sub_div_templates():
    """Issue #2：dec_sub/dec_div 应产出减法/除法表达式，而非加法/乘法"""
    print("== 6. 小数减/除模板语义 ==")
    for _ in range(50):
        sub = _tpl_dec_sub()
        assert "-" in sub["stem"], f"dec_sub 应为减法: {sub['stem']}"
        assert "÷" in sub["stem"] or "+" not in sub["stem"], f"dec_sub 出现加法: {sub['stem']}"
        div = _tpl_dec_div()
        assert "÷" in div["stem"], f"dec_div 应为除法: {div['stem']}"
        assert "×" not in div["stem"], f"dec_div 出现乘法: {div['stem']}"
    # 分发表映射正确
    assert TEMPLATES["dec_sub"] is _tpl_dec_sub, "dec_sub 未映射到正确函数"
    assert TEMPLATES["dec_div"] is _tpl_dec_div, "dec_div 未映射到正确函数"
    print("  小数减/除模板语义与分发表映射正确 ✅")


def test_word_problem_grade_whitelist():
    """Issue #3：倍数关系模板不应出现在低年级 word_problem 题中"""
    print("== 7. 解决问题模板年级白名单 ==")
    # 倍数关系题限定三年级及以上
    assert TEMPLATE_GRADE["word_problem_relation"] == \
        ["三年级", "四年级", "五年级", "六年级"], "word_problem_relation 白名单错误"
    assert "一年级" not in TEMPLATE_GRADE["word_problem_relation"]
    assert "二年级" not in TEMPLATE_GRADE["word_problem_relation"]
    # 低年级 word_problem 不应生成倍数题
    for g in ("一年级", "二年级"):
        for _ in range(30):
            q = generate_question_with_errors(
                "G1U01KP01", "比多少", 2,
                kp={"types": ["word_problem"], "grade": g, "semester": "上册"},
            )
            assert "倍" not in q["stem"], f"{g} 出现倍数内容: {q['stem']}"
    print("  低年级解决题不再出现倍数内容 ✅")


if __name__ == "__main__":
    test_pattern_library()
    test_hierarchy()
    test_generation()
    test_example_output()
    test_angle_template_no_crash()
    test_dec_sub_div_templates()
    test_word_problem_grade_whitelist()
    print("\n全部自测通过 ✅")