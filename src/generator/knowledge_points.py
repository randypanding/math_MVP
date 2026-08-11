"""知识点注册表 - 覆盖小学1-6年级"""

# 完整知识点列表（100+）
KNOWLEDGE_POINTS = [
    # === 一年级上册 ===
    {"id": "G1U01KP01", "name": "数一数", "grade": "一年级", "semester": "上册", "unit": "准备课", "types": ["oral_counting"], "difficulty": [1, 2]},
    {"id": "G1U01KP02", "name": "比多少", "grade": "一年级", "semester": "上册", "unit": "准备课", "types": ["compare_size", "shape_counting"], "difficulty": [1, 2]},
    {"id": "G1U02KP01", "name": "1-5的认识", "grade": "一年级", "semester": "上册", "unit": "1-5的认识和加减法", "types": ["number_read_write", "compare_size", "number_composition"], "difficulty": [1, 2]},
    {"id": "G1U02KP02", "name": "5以内加法", "grade": "一年级", "semester": "上册", "unit": "1-5的认识和加减法", "types": ["mental_arithmetic", "word_problem"], "difficulty": [1, 2]},
    {"id": "G1U02KP03", "name": "5以内减法", "grade": "一年级", "semester": "上册", "unit": "1-5的认识和加减法", "types": ["mental_arithmetic", "word_problem"], "difficulty": [1, 2]},
    {"id": "G1U02KP04", "name": "0的认识", "grade": "一年级", "semester": "上册", "unit": "1-5的认识和加减法", "types": ["mental_arithmetic", "number_read_write"], "difficulty": [1, 2]},
    {"id": "G1U03KP01", "name": "认识图形(一)", "grade": "一年级", "semester": "上册", "unit": "认识图形(一)", "types": ["shape_counting"], "difficulty": [1, 2]},
    {"id": "G1U04KP01", "name": "6-10的认识", "grade": "一年级", "semester": "上册", "unit": "6-10的认识和加减法", "types": ["number_read_write", "compare_size", "number_composition"], "difficulty": [1, 2]},
    {"id": "G1U04KP02", "name": "6-10的加法", "grade": "一年级", "semester": "上册", "unit": "6-10的认识和加减法", "types": ["mental_arithmetic", "fill_unknown", "word_problem"], "difficulty": [1, 2]},
    {"id": "G1U04KP03", "name": "6-10的减法", "grade": "一年级", "semester": "上册", "unit": "6-10的认识和加减法", "types": ["mental_arithmetic", "fill_unknown", "word_problem"], "difficulty": [1, 2]},
    {"id": "G1U04KP04", "name": "连加连减", "grade": "一年级", "semester": "上册", "unit": "6-10的认识和加减法", "types": ["step_calculation"], "difficulty": [2, 3]},
    {"id": "G1U04KP05", "name": "加减混合", "grade": "一年级", "semester": "上册", "unit": "6-10的认识和加减法", "types": ["step_calculation"], "difficulty": [2, 3]},
    {"id": "G1U05KP01", "name": "11-20各数的认识", "grade": "一年级", "semester": "上册", "unit": "11-20各数的认识", "types": ["number_read_write", "number_composition", "compare_size"], "difficulty": [1, 2]},
    {"id": "G1U06KP01", "name": "认识钟表", "grade": "一年级", "semester": "上册", "unit": "认识钟表", "types": ["chart_analysis"], "difficulty": [1, 2]},
    {"id": "G1U07KP01", "name": "20以内进位加法", "grade": "一年级", "semester": "上册", "unit": "20以内进位加法", "types": ["mental_arithmetic", "fill_unknown", "word_problem"], "difficulty": [2, 3]},

    # === 一年级下册 ===
    {"id": "G1U08KP01", "name": "20以内退位减法", "grade": "一年级", "semester": "下册", "unit": "20以内退位减法", "types": ["mental_arithmetic", "fill_unknown", "word_problem"], "difficulty": [2, 3]},
    {"id": "G1U09KP01", "name": "认识图形(二)", "grade": "一年级", "semester": "下册", "unit": "认识图形(二)", "types": ["shape_counting"], "difficulty": [1, 2]},
    {"id": "G1U10KP01", "name": "分类与整理", "grade": "一年级", "semester": "下册", "unit": "分类与整理", "types": ["chart_analysis"], "difficulty": [1, 2]},
    {"id": "G1U11KP01", "name": "100以内数的认识", "grade": "一年级", "semester": "下册", "unit": "100以内数的认识", "types": ["number_read_write", "number_composition", "compare_size", "pattern_sequence"], "difficulty": [1, 2]},
    {"id": "G1U12KP01", "name": "认识人民币", "grade": "一年级", "semester": "下册", "unit": "认识人民币", "types": ["unit_conversion", "word_problem"], "difficulty": [2, 3]},
    {"id": "G1U13KP01", "name": "100以内加法(一)", "grade": "一年级", "semester": "下册", "unit": "100以内的加法和减法(一)", "types": ["mental_arithmetic", "vertical_calculation", "word_problem"], "difficulty": [2, 3]},
    {"id": "G1U13KP02", "name": "100以内减法(一)", "grade": "一年级", "semester": "下册", "unit": "100以内的加法和减法(一)", "types": ["mental_arithmetic", "vertical_calculation", "word_problem"], "difficulty": [2, 3]},

    # === 二年级上册 ===
    {"id": "G2U01KP01", "name": "长度单位", "grade": "二年级", "semester": "上册", "unit": "长度单位", "types": ["unit_conversion", "compare_size"], "difficulty": [1, 2]},
    {"id": "G2U02KP01", "name": "100以内加法(二)", "grade": "二年级", "semester": "上册", "unit": "100以内的加法和减法(二)", "types": ["vertical_calculation", "step_calculation", "word_problem"], "difficulty": [2, 3]},
    {"id": "G2U02KP02", "name": "100以内减法(二)", "grade": "二年级", "semester": "上册", "unit": "100以内的加法和减法(二)", "types": ["vertical_calculation", "step_calculation", "word_problem"], "difficulty": [2, 3]},
    {"id": "G2U02KP03", "name": "连加连减加减混合", "grade": "二年级", "semester": "上册", "unit": "100以内的加法和减法(二)", "types": ["step_calculation"], "difficulty": [2, 3]},
    {"id": "G2U03KP01", "name": "角的初步认识", "grade": "二年级", "semester": "上册", "unit": "角的初步认识", "types": ["shape_counting", "angle_measurement"], "difficulty": [1, 2]},
    {"id": "G2U04KP01", "name": "表内乘法(一)", "grade": "二年级", "semester": "上册", "unit": "表内乘法(一)", "types": ["mental_arithmetic", "fill_unknown", "composite_expression"], "difficulty": [1, 2]},
    {"id": "G2U05KP01", "name": "观察物体(一)", "grade": "二年级", "semester": "上册", "unit": "观察物体(一)", "types": ["shape_counting"], "difficulty": [1, 2]},
    {"id": "G2U06KP01", "name": "表内乘法(二)", "grade": "二年级", "semester": "上册", "unit": "表内乘法(二)", "types": ["mental_arithmetic", "fill_unknown", "word_problem"], "difficulty": [2, 3]},
    {"id": "G2U07KP01", "name": "认识时间", "grade": "二年级", "semester": "上册", "unit": "认识时间", "types": ["unit_conversion", "chart_analysis"], "difficulty": [2, 3]},

    # === 二年级下册 ===
    {"id": "G2U08KP01", "name": "数据收集整理", "grade": "二年级", "semester": "下册", "unit": "数据收集整理", "types": ["chart_analysis"], "difficulty": [1, 2]},
    {"id": "G2U09KP01", "name": "表内除法(一)", "grade": "二年级", "semester": "下册", "unit": "表内除法(一)", "types": ["mental_arithmetic", "fill_unknown", "word_problem"], "difficulty": [1, 2]},
    {"id": "G2U10KP01", "name": "图形的运动(一)", "grade": "二年级", "semester": "下册", "unit": "图形的运动(一)", "types": ["shape_counting"], "difficulty": [1, 2]},
    {"id": "G2U11KP01", "name": "表内除法(二)", "grade": "二年级", "semester": "下册", "unit": "表内除法(二)", "types": ["mental_arithmetic", "word_problem"], "difficulty": [2, 3]},
    {"id": "G2U12KP01", "name": "混合运算", "grade": "二年级", "semester": "下册", "unit": "混合运算", "types": ["step_calculation", "composite_expression"], "difficulty": [2, 3]},
    {"id": "G2U13KP01", "name": "有余数的除法", "grade": "二年级", "semester": "下册", "unit": "有余数的除法", "types": ["vertical_calculation", "fill_unknown", "word_problem"], "difficulty": [2, 3]},
    {"id": "G2U14KP01", "name": "万以内数的认识", "grade": "二年级", "semester": "下册", "unit": "万以内数的认识", "types": ["number_read_write", "number_composition", "compare_size", "estimation"], "difficulty": [2, 3]},
    {"id": "G2U15KP01", "name": "克和千克", "grade": "二年级", "semester": "下册", "unit": "克和千克", "types": ["unit_conversion", "compare_size"], "difficulty": [1, 2]},

    # === 三年级上册 ===
    {"id": "G3U01KP01", "name": "时分秒", "grade": "三年级", "semester": "上册", "unit": "时、分、秒", "types": ["unit_conversion", "word_problem"], "difficulty": [1, 2]},
    {"id": "G3U02KP01", "name": "万以内加减法(一)", "grade": "三年级", "semester": "上册", "unit": "万以内的加法和减法(一)", "types": ["vertical_calculation", "verification"], "difficulty": [2, 3]},
    {"id": "G3U03KP01", "name": "测量", "grade": "三年级", "semester": "上册", "unit": "测量", "types": ["unit_conversion", "word_problem"], "difficulty": [2, 3]},
    {"id": "G3U04KP01", "name": "倍的认识", "grade": "三年级", "semester": "上册", "unit": "倍的认识", "types": ["mental_arithmetic", "word_problem"], "difficulty": [2, 3]},
    {"id": "G3U05KP01", "name": "多位数乘一位数", "grade": "三年级", "semester": "上册", "unit": "多位数乘一位数", "types": ["vertical_calculation", "step_calculation", "word_problem"], "difficulty": [2, 3]},
    {"id": "G3U06KP01", "name": "长方形和正方形", "grade": "三年级", "semester": "上册", "unit": "长方形和正方形", "types": ["perimeter_area", "shape_counting"], "difficulty": [2, 3]},
    {"id": "G3U07KP01", "name": "分数的初步认识", "grade": "三年级", "semester": "上册", "unit": "分数的初步认识", "types": ["mental_arithmetic", "compare_size", "number_read_write"], "difficulty": [2, 3]},

    # === 三年级下册 ===
    {"id": "G3U08KP01", "name": "位置与方向(一)", "grade": "三年级", "semester": "下册", "unit": "位置与方向(一)", "types": ["chart_analysis"], "difficulty": [1, 2]},
    {"id": "G3U09KP01", "name": "除数是一位数的除法", "grade": "三年级", "semester": "下册", "unit": "除数是一位数的除法", "types": ["vertical_calculation", "verification", "fill_unknown"], "difficulty": [2, 3]},
    {"id": "G3U10KP01", "name": "复式统计表", "grade": "三年级", "semester": "下册", "unit": "复式统计表", "types": ["chart_analysis"], "difficulty": [2, 3]},
    {"id": "G3U11KP01", "name": "两位数乘两位数", "grade": "三年级", "semester": "下册", "unit": "两位数乘两位数", "types": ["vertical_calculation", "step_calculation", "word_problem"], "difficulty": [2, 3]},
    {"id": "G3U12KP01", "name": "面积", "grade": "三年级", "semester": "下册", "unit": "面积", "types": ["perimeter_area", "unit_conversion", "word_problem"], "difficulty": [2, 3]},
    {"id": "G3U13KP01", "name": "年月日", "grade": "三年级", "semester": "下册", "unit": "年、月、日", "types": ["unit_conversion", "word_problem"], "difficulty": [2, 3]},
    {"id": "G3U14KP01", "name": "小数的初步认识", "grade": "三年级", "semester": "下册", "unit": "小数的初步认识", "types": ["number_read_write", "compare_size", "mental_arithmetic"], "difficulty": [2, 3]},

    # === 四年级上册 ===
    {"id": "G4U01KP01", "name": "大数的认识", "grade": "四年级", "semester": "上册", "unit": "大数的认识", "types": ["number_read_write", "number_composition", "estimation", "unit_conversion"], "difficulty": [2, 3]},
    {"id": "G4U02KP01", "name": "公顷和平方千米", "grade": "四年级", "semester": "上册", "unit": "公顷和平方千米", "types": ["unit_conversion", "word_problem"], "difficulty": [2, 3]},
    {"id": "G4U03KP01", "name": "角的度量", "grade": "四年级", "semester": "上册", "unit": "角的度量", "types": ["angle_measurement", "shape_counting"], "difficulty": [2, 3]},
    {"id": "G4U04KP01", "name": "三位数乘两位数", "grade": "四年级", "semester": "上册", "unit": "三位数乘两位数", "types": ["vertical_calculation", "word_problem", "estimation"], "difficulty": [2, 3]},
    {"id": "G4U05KP01", "name": "平行四边形和梯形", "grade": "四年级", "semester": "上册", "unit": "平行四边形和梯形", "types": ["shape_counting", "perimeter_area"], "difficulty": [2, 3]},
    {"id": "G4U06KP01", "name": "除数是两位数的除法", "grade": "四年级", "semester": "上册", "unit": "除数是两位数的除法", "types": ["vertical_calculation", "verification", "fill_unknown"], "difficulty": [3, 4]},
    {"id": "G4U07KP01", "name": "条形统计图", "grade": "四年级", "semester": "上册", "unit": "条形统计图", "types": ["chart_analysis"], "difficulty": [2, 3]},

    # === 四年级下册 ===
    {"id": "G4U08KP01", "name": "四则运算", "grade": "四年级", "semester": "下册", "unit": "四则运算", "types": ["step_calculation", "composite_expression"], "difficulty": [2, 3]},
    {"id": "G4U09KP01", "name": "运算定律", "grade": "四年级", "semester": "下册", "unit": "运算定律", "types": ["simplified_calculation", "verification"], "difficulty": [2, 3]},
    {"id": "G4U10KP01", "name": "小数的意义和性质", "grade": "四年级", "semester": "下册", "unit": "小数的意义和性质", "types": ["number_read_write", "compare_size", "unit_conversion"], "difficulty": [2, 3]},
    {"id": "G4U11KP01", "name": "三角形", "grade": "四年级", "semester": "下册", "unit": "三角形", "types": ["shape_counting", "angle_measurement", "perimeter_area"], "difficulty": [2, 3]},
    {"id": "G4U12KP01", "name": "小数的加法和减法", "grade": "四年级", "semester": "下册", "unit": "小数的加法和减法", "types": ["vertical_calculation", "step_calculation", "verification"], "difficulty": [2, 3]},
    {"id": "G4U13KP01", "name": "图形的运动(二)", "grade": "四年级", "semester": "下册", "unit": "图形的运动(二)", "types": ["shape_counting"], "difficulty": [2, 3]},
    {"id": "G4U14KP01", "name": "平均数与条形统计图", "grade": "四年级", "semester": "下册", "unit": "平均数与条形统计图", "types": ["chart_analysis", "word_problem"], "difficulty": [2, 3]},

    # === 五年级上册 ===
    {"id": "G5U01KP01", "name": "小数乘法", "grade": "五年级", "semester": "上册", "unit": "小数乘法", "types": ["vertical_calculation", "step_calculation", "simplified_calculation"], "difficulty": [2, 3]},
    {"id": "G5U02KP01", "name": "位置", "grade": "五年级", "semester": "上册", "unit": "位置", "types": ["chart_analysis"], "difficulty": [1, 2]},
    {"id": "G5U03KP01", "name": "小数除法", "grade": "五年级", "semester": "上册", "unit": "小数除法", "types": ["vertical_calculation", "verification", "fill_unknown"], "difficulty": [3, 4]},
    {"id": "G5U04KP01", "name": "可能性", "grade": "五年级", "semester": "上册", "unit": "可能性", "types": ["chart_analysis", "math_puzzle"], "difficulty": [2, 3]},
    {"id": "G5U05KP01", "name": "简易方程", "grade": "五年级", "semester": "上册", "unit": "简易方程", "types": ["solve_equation", "composite_expression", "word_problem"], "difficulty": [3, 4]},
    {"id": "G5U06KP01", "name": "多边形的面积", "grade": "五年级", "semester": "上册", "unit": "多边形的面积", "types": ["perimeter_area", "word_problem"], "difficulty": [3, 4]},

    # === 五年级下册 ===
    {"id": "G5U07KP01", "name": "观察物体(三)", "grade": "五年级", "semester": "下册", "unit": "观察物体(三)", "types": ["shape_counting"], "difficulty": [2, 3]},
    {"id": "G5U08KP01", "name": "因数与倍数", "grade": "五年级", "semester": "下册", "unit": "因数与倍数", "types": ["number_composition", "pattern_sequence", "math_puzzle"], "difficulty": [2, 3]},
    {"id": "G5U09KP01", "name": "长方体和正方体", "grade": "五年级", "semester": "下册", "unit": "长方体和正方体", "types": ["perimeter_area", "unit_conversion", "word_problem"], "difficulty": [3, 4]},
    {"id": "G5U10KP01", "name": "分数的意义和性质", "grade": "五年级", "semester": "下册", "unit": "分数的意义和性质", "types": ["number_read_write", "compare_size", "unit_conversion"], "difficulty": [3, 4]},
    {"id": "G5U11KP01", "name": "分数的加法和减法", "grade": "五年级", "semester": "下册", "unit": "分数的加法和减法", "types": ["step_calculation", "simplified_calculation", "fill_unknown"], "difficulty": [3, 4]},

    # === 六年级上册 ===
    {"id": "G6U01KP01", "name": "分数乘法", "grade": "六年级", "semester": "上册", "unit": "分数乘法", "types": ["step_calculation", "simplified_calculation", "word_problem"], "difficulty": [3, 4]},
    {"id": "G6U02KP01", "name": "位置与方向(二)", "grade": "六年级", "semester": "上册", "unit": "位置与方向(二)", "types": ["chart_analysis"], "difficulty": [2, 3]},
    {"id": "G6U03KP01", "name": "分数除法", "grade": "六年级", "semester": "上册", "unit": "分数除法", "types": ["step_calculation", "word_problem"], "difficulty": [3, 4]},
    {"id": "G6U04KP01", "name": "比", "grade": "六年级", "semester": "上册", "unit": "比", "types": ["compare_size", "unit_conversion", "word_problem"], "difficulty": [3, 4]},
    {"id": "G6U05KP01", "name": "圆", "grade": "六年级", "semester": "上册", "unit": "圆", "types": ["perimeter_area", "word_problem"], "difficulty": [3, 4]},
    {"id": "G6U06KP01", "name": "百分数(一)", "grade": "六年级", "semester": "上册", "unit": "百分数(一)", "types": ["percentage", "unit_conversion", "word_problem"], "difficulty": [3, 4]},

    # === 六年级下册 ===
    {"id": "G6U07KP01", "name": "负数", "grade": "六年级", "semester": "下册", "unit": "负数", "types": ["number_read_write", "compare_size", "word_problem"], "difficulty": [2, 3]},
    {"id": "G6U08KP01", "name": "百分数(二)", "grade": "六年级", "semester": "下册", "unit": "百分数(二)", "types": ["percentage", "word_problem"], "difficulty": [3, 4]},
    {"id": "G6U09KP01", "name": "圆柱与圆锥", "grade": "六年级", "semester": "下册", "unit": "圆柱与圆锥", "types": ["perimeter_area", "unit_conversion", "word_problem"], "difficulty": [3, 4]},
    {"id": "G6U10KP01", "name": "比例", "grade": "六年级", "semester": "下册", "unit": "比例", "types": ["solve_equation", "word_problem", "chart_analysis"], "difficulty": [3, 4]},
]


def load_knowledge_points(grade: str = None, name: str = None) -> list:
    """加载知识点列表，支持按年级或名称筛选"""
    result = KNOWLEDGE_POINTS
    if grade:
        result = [kp for kp in result if kp["grade"] == grade]
    if name:
        result = [kp for kp in result if name in kp["name"]]
    return result


def get_knowledge_point(kp_id: str) -> dict:
    """根据ID获取知识点"""
    for kp in KNOWLEDGE_POINTS:
        if kp["id"] == kp_id:
            return kp
    return None
