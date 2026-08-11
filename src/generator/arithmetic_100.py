"""算术类题目生成器 - 覆盖1-6年级核心计算"""

import random
from typing import List, Dict, Any
from .base import BaseGenerator


class ArithmeticGenerator(BaseGenerator):
    """算术类题目生成器"""

    def generate(self, count: int, knowledge_point: dict, **kwargs) -> List[Dict[str, Any]]:
        """根据知识点类型生成对应题目"""
        kp_id = knowledge_point["id"]
        kp_name = knowledge_point["name"]
        types = knowledge_point.get("types", [])
        difficulty_range = knowledge_point.get("difficulty_range", [1, 3])

        questions = []
        for _ in range(count):
            # 选择一个题型
            q_type = random.choice(types) if types else "mental_arithmetic"
            difficulty = random.randint(difficulty_range[0], difficulty_range[1])

            q = self._generate_by_type(q_type, kp_id, kp_name, difficulty)
            if q:
                questions.append(q)

        return questions

    def _generate_by_type(self, q_type: str, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """根据题型生成题目"""
        generators = {
            # 数与代数
            "mental_arithmetic": self._gen_mental_arithmetic,
            "vertical_calculation": self._gen_vertical_calculation,
            "step_calculation": self._gen_step_calculation,
            "fill_unknown": self._gen_fill_unknown,
            "number_composition": self._gen_number_composition,
            "number_read_write": self._gen_number_read_write,
            "compare_size": self._gen_compare_size,
            "pattern_sequence": self._gen_pattern_sequence,
            "verification": self._gen_verification,
            "estimation": self._gen_estimation,
            "simplified_calculation": self._gen_simplified_calculation,
            "composite_expression": self._gen_composite_expression,
            "solve_equation": self._gen_solve_equation,
            "percentage": self._gen_percentage,
            # 几何与量
            "shape_counting": self._gen_shape_counting,
            "perimeter_area": self._gen_perimeter_area,
            "unit_conversion": self._gen_unit_conversion,
            "angle_measurement": self._gen_angle_measurement,
            # 统计与解决问题
            "chart_analysis": self._gen_chart_analysis,
            "word_problem": self._gen_word_problem,
            "math_puzzle": self._gen_math_puzzle,
            # 其他
            "oral_counting": self._gen_oral_counting,
        }

        gen_func = generators.get(q_type)
        if gen_func:
            return gen_func(kp_id, kp_name, difficulty)
        return None

    def _gen_mental_arithmetic(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """口算题"""
        if "100以内" in kp_name or "20以内" in kp_name:
            if "加法" in kp_name or "进位" in kp_name:
                a = random.randint(10, 89)
                b = random.randint(10, 99 - a)
                answer = a + b
                stem = f"{a} + {b} = ?"
                solution = f"先算个位{ a % 10} + {b % 10} = {(a % 10 + b % 10)}，再算十位{a // 10} + {b // 10} + {(a % 10 + b % 10) // 10} = {answer // 10 if answer >= 10 else 0}，所以答案是{answer}"
                common_error = f"忘记进位，可能算成{answer - 10}" if answer >= 10 else None
            elif "减法" in kp_name or "退位" in kp_name:
                a = random.randint(20, 99)
                b = random.randint(10, a - 10)
                answer = a - b
                stem = f"{a} - {b} = ?"
                solution = f"个位{a % 10}减{b % 10}不够减，从十位借1，变成{a % 10 + 10} - {b % 10} = {(a % 10 + 10) - b % 10}，十位{a // 10 - 1} - {b // 10} = {(a // 10 - 1) - b // 10}，所以答案是{answer}"
                common_error = f"忘记退位，可能算成{a - b + 10}" if a % 10 < b % 10 else None
            elif "连加" in kp_name or "连减" in kp_name or "混合" in kp_name:
                a = random.randint(10, 50)
                b = random.randint(5, 30)
                c = random.randint(5, 20)
                if random.choice([True, False]):
                    answer = a + b - c
                    stem = f"{a} + {b} - {c} = ?"
                else:
                    answer = a - b + c
                    stem = f"{a} - {b} + {c} = ?"
                solution = f"从左到右依次计算"
                common_error = f"运算顺序错误"
            else:
                a = random.randint(1, 99)
                b = random.randint(1, 99 - a)
                answer = a + b
                stem = f"{a} + {b} = ?"
                solution = f"{a} + {b} = {answer}"
                common_error = None
        elif "表内" in kp_name or "乘法" in kp_name or "除法" in kp_name:
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            if "除法" in kp_name:
                answer = a
                stem = f"{a * b} ÷ {b} = ?"
                solution = f"想乘法口诀：{b} × {a} = {a * b}，所以{a * b} ÷ {b} = {a}"
            else:
                answer = a * b
                stem = f"{a} × {b} = ?"
                solution = f"乘法口诀：{a} × {b} = {answer}"
            common_error = f"记错口诀，可能算成{a * b + random.choice([-1, 1, b - a])}"
        elif "小数" in kp_name:
            a = round(random.uniform(0.1, 9.9), 1)
            b = round(random.uniform(0.1, 9.9), 1)
            if "乘法" in kp_name:
                answer = round(a * b, 2)
                stem = f"{a} × {b} = ?"
            elif "除法" in kp_name:
                a = round(random.uniform(1.0, 9.9), 1)
                b = random.choice([10, 100, 1000])
                answer = round(a / b, 3)
                stem = f"{a} ÷ {b} = ?"
            else:
                answer = round(a + b, 1)
                stem = f"{a} + {b} = ?"
            solution = f"按小数运算法则计算"
            common_error = "小数点位置错误"
        elif "分数" in kp_name:
            a_num = random.randint(1, 5)
            a_den = random.randint(a_num + 1, 9)
            b_num = random.randint(1, 5)
            b_den = random.randint(b_num + 1, 9)
            if "加法" in kp_name:
                common_den = a_den * b_den
                answer_num = a_num * b_den + b_num * a_den
                stem = f"{a_num}/{a_den} + {b_num}/{b_den} = ?"
                answer = f"{answer_num}/{common_den}"
                # 约分
                from math import gcd
                g = gcd(answer_num, common_den)
                if g > 1:
                    answer = f"{answer_num // g}/{common_den // g}"
            else:
                common_den = a_den * b_den
                answer_num = abs(a_num * b_den - b_num * a_den)
                stem = f"{a_num}/{a_den} - {b_num}/{b_den} = ?"
                answer = f"{answer_num}/{common_den}"
            solution = f"通分后计算"
            common_error = "忘记通分"
        else:
            a = random.randint(1, 100)
            b = random.randint(1, 100)
            answer = a + b
            stem = f"{a} + {b} = ?"
            solution = f"{a} + {b} = {answer}"
            common_error = None

        return self._create_question(kp_id, "mental_arithmetic", stem, answer, solution, common_error, difficulty)

    def _gen_vertical_calculation(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """竖式计算"""
        if "100以内" in kp_name or "20以内" in kp_name:
            a = random.randint(10, 89)
            b = random.randint(10, 99)
            if "减法" in kp_name:
                if a < b:
                    a, b = b, a
                answer = a - b
                stem = f"用竖式计算：{a} - {b} = ?"
            else:
                answer = a + b
                stem = f"用竖式计算：{a} + {b} = ?"
        elif "小数" in kp_name:
            a = round(random.uniform(1.0, 99.9), random.choice([1, 2]))
            b = round(random.uniform(1.0, 99.9), random.choice([1, 2]))
            answer = round(a + b, 2)
            stem = f"用竖式计算：{a} + {b} = ?"
        elif "除法" in kp_name:
            b = random.randint(2, 9)
            answer = random.randint(10, 99)
            a = b * answer + random.randint(0, b - 1)
            stem = f"用竖式计算：{a} ÷ {b} = ?..."
            answer = f"{answer}...{a % b}"
        else:
            a = random.randint(100, 999)
            b = random.randint(100, 999)
            answer = a + b
            stem = f"用竖式计算：{a} + {b} = ?"

        return self._create_question(kp_id, "vertical_calculation", stem, answer, difficulty=difficulty)

    def _gen_step_calculation(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """脱式计算"""
        if "混合" in kp_name or "连加" in kp_name or "连减" in kp_name:
            a = random.randint(10, 50)
            b = random.randint(5, 30)
            c = random.randint(5, 20)
            op1 = random.choice(['+', '-'])
            op2 = random.choice(['+', '-'])
            stem = f"{a} {op1} {b} {op2} {c}"
            # 手动计算，不用eval
            if op1 == '+':
                temp = a + b
            else:
                temp = a - b
            if op2 == '+':
                answer = temp + c
            else:
                answer = temp - c
            stem += " = ?"
        elif "小数" in kp_name:
            a = round(random.uniform(1.0, 10.0), 1)
            b = round(random.uniform(1.0, 10.0), 1)
            c = round(random.uniform(1.0, 10.0), 1)
            stem = f"{a} + {b} × {c}"
            answer = round(a + b * c, 2)
            stem += " = ?"
        elif "分数" in kp_name:
            a = random.randint(1, 5)
            b = random.randint(2, 5)
            c = random.randint(1, 5)
            d = random.randint(2, 5)
            stem = f"{a}/{b} + {c}/{d} × 2"
            answer = "需通分计算"
        else:
            a = random.randint(10, 100)
            b = random.randint(2, 9)
            c = random.randint(1, 20)
            stem = f"{a} + {b} × {c}"
            answer = a + b * c
            stem += " = ?"

        return self._create_question(kp_id, "step_calculation", stem, answer, difficulty=difficulty)

    def _gen_fill_unknown(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """填未知数"""
        if "100以内" in kp_name or "20以内" in kp_name:
            answer = random.randint(1, 50)
            if "加法" in kp_name:
                a = random.randint(10, 50)
                stem = f"{a} + (&#95;&#95;) = {a + answer}"
            elif "减法" in kp_name:
                a = random.randint(30, 99)
                stem = f"{a} - (&#95;&#95;) = {a - answer}"
            else:
                stem = f"(&#95;&#95;) + {answer} = {answer + random.randint(1, 50)}"
                answer = eval(stem.split("=")[1].strip()) - answer
        elif "乘法" in kp_name or "除法" in kp_name:
            answer = random.randint(2, 9)
            stem = f"(&#95;&#95;) × {random.randint(2, 9)} = {answer * random.randint(2, 9)}"
        elif "方程" in kp_name:
            answer = random.randint(1, 20)
            stem = f"x + {random.randint(1, 10)} = {answer + random.randint(1, 10)}，x = (&#95;&#95;)"
        else:
            answer = random.randint(1, 100)
            stem = f"(&#95;&#95;) + 25 = {answer + 25}"

        return self._create_question(kp_id, "fill_unknown", stem, answer, difficulty=difficulty)

    def _gen_number_composition(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """数的组成"""
        if "100以内" in kp_name:
            tens = random.randint(1, 9)
            ones = random.randint(0, 9)
            num = tens * 10 + ones
            stem = f"{tens}个十和{ones}个一组成（&#95;&#95;）"
            answer = num
        elif "11-20" in kp_name:
            num = random.randint(11, 20)
            tens = num // 10
            ones = num % 10
            stem = f"{num}是由（&#95;&#95;）个十和（&#95;&#95;）个一组成的"
            answer = f"{tens}个十和{ones}个一"
        elif "万以内" in kp_name:
            num = random.randint(1000, 9999)
            thousands = num // 1000
            hundreds = (num % 1000) // 100
            tens = (num % 100) // 10
            ones = num % 10
            stem = f"{num}是由（&#95;&#95;）个千、（&#95;&#95;）个百、（&#95;&#95;）个十和（&#95;&#95;）个一组成的"
            answer = f"{thousands}个千、{hundreds}个百、{tens}个十、{ones}个一"
        elif "大数" in kp_name:
            num = random.randint(1000000, 99999999)
            stem = f"请说出{num}的组成"
            answer = f"{num // 1000000}个百万..."
        else:
            num = random.randint(10, 99)
            stem = f"{num} = （&#95;&#95;）个十 + （&#95;&#95;）个一"
            answer = f"{num // 10}个十 + {num % 10}个一"

        return self._create_question(kp_id, "number_composition", stem, answer, difficulty=difficulty)

    def _gen_number_read_write(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """数的读写"""
        if "100以内" in kp_name:
            num = random.randint(10, 99)
            stem = f"写出下列数：{num} 读作（&#95;&#95;）"
            if num < 20:
                answer = ["十", "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九"][num - 10]
            else:
                tens_word = ["", "", "二十", "三十", "四十", "五十", "六十", "七十", "八十", "九十"][num // 10]
                ones_word = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九"][num % 10]
                answer = tens_word + ones_word
        elif "万以内" in kp_name:
            num = random.randint(1000, 9999)
            stem = f"写出{num}并读出来"
            answer = f"写作：{num}，读作：{num // 1000}千{(num % 1000) // 100}百..."
        elif "大数" in kp_name:
            num = random.randint(100000, 99999999)
            stem = f"读出下列数：{num}"
            answer = f"{num // 10000}万..."
        else:
            num = random.randint(100, 999)
            stem = f"写出：{['百', '十', '一']}"
            answer = str(num)

        return self._create_question(kp_id, "number_read_write", stem, answer, difficulty=difficulty)

    def _gen_compare_size(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """比大小"""
        a = random.randint(1, 100)
        b = random.randint(1, 100)
        while a == b:
            b = random.randint(1, 100)

        if a > b:
            answer = ">"
        else:
            answer = "<"

        stem = f"在○里填上>、<或=：{a} ○ {b}"
        solution = f"{a} {'大于' if a > b else '小于'} {b}"
        common_error = "记反了大于号和小于号"

        return self._create_question(kp_id, "compare_size", stem, answer, solution, common_error, difficulty)

    def _gen_pattern_sequence(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """规律填数"""
        patterns = [
            ([2, 4, 6, 8, "___"], "10", "每次加2"),
            ([1, 3, 5, 7, "___"], "9", "每次加2（奇数）"),
            ([10, 20, 30, 40, "___"], "50", "每次加10"),
            ([9, 8, 7, 6, "___"], "5", "每次减1"),
            ([1, 2, 4, 7, 11, "___"], "16", "依次加1,2,3,4,5"),
            ([2, 3, 5, 8, 13, "___"], "21", "前两项之和"),
            ([5, 10, 20, 40, "___"], "80", "每次乘2"),
            ([100, 90, 80, 70, "___"], "60", "每次减10"),
        ]

        seq, answer, solution = random.choice(patterns)
        stem = f"找规律填数：{', '.join(str(x) for x in seq)}"

        return self._create_question(kp_id, "pattern_sequence", stem, answer, solution, difficulty=difficulty)

    def _gen_verification(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """验算题"""
        a = random.randint(10, 99)
        b = random.randint(10, 99)
        correct = a + b
        wrong = correct + random.choice([-10, 10, -1, 1])

        stem = f"判断对错并改正：{a} + {b} = {wrong}（&#95;&#95;）"
        answer = f"错误，正确答案是{correct}"
        solution = f"验算：{correct} - {a} = {b}，所以{a} + {b} = {correct}"
        common_error = "没有发现计算错误"

        return self._create_question(kp_id, "verification", stem, answer, solution, common_error, difficulty)

    def _gen_estimation(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """估算题"""
        a = random.randint(100, 999)
        b = random.randint(100, 999)

        stem = f"估算：{a} + {b} ≈ ?"
        a_round = round(a, -2)
        b_round = round(b, -2)
        answer = f"{a} ≈ {a_round}，{b} ≈ {b_round}，所以{a} + {b} ≈ {a_round + b_round}"
        solution = f"把{a}看作{a_round}，把{b}看作{b_round}"

        return self._create_question(kp_id, "estimation", stem, answer, solution, difficulty=difficulty)

    def _gen_simplified_calculation(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """简便计算"""
        patterns = [
            (f"{a} + {b} + {c} = ({a}+{b})+{c} = ?", str(a+b+c), "加法结合律")
            for a, b, c in [(25, 75, 36), (47, 53, 28), (64, 36, 57)]
        ] + [
            (f"{a} × {b} × {c} = ({a}×{b})×{c} = ?", str(a*b*c), "乘法结合律")
            for a, b, c in [(4, 25, 7), (8, 125, 3)]
        ] + [
            (f"{a} × {b} + {a} × {c} = {a}×({b}+{c}) = ?", str(a*(b+c)), "乘法分配律")
            for a, b, c in [(25, 4, 6), (12, 5, 5)]
        ]

        stem, answer, solution = random.choice(patterns)
        return self._create_question(kp_id, "simplified_calculation", stem, answer, solution, difficulty=difficulty)

    def _gen_composite_expression(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """列综合算式"""
        a = random.randint(10, 50)
        b = random.randint(2, 9)
        c = random.randint(5, 20)

        stem = f"把下面的分步算式列成综合算式：{a} + {b} = {a+b}，{a+b} × {c} = ?"
        answer = f"(a + b) × c"
        solution = f"先算加法，再算乘法，注意加括号"

        return self._create_question(kp_id, "composite_expression", stem, answer, solution, difficulty=difficulty)

    def _gen_solve_equation(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """解方程"""
        if "简易" in kp_name:
            answer = random.randint(1, 20)
            a = random.randint(2, 10)
            b = a * answer + random.randint(1, 10)
            stem = f"解方程：{a}x + {a*answer} = {b}，x = ?"
            solution = f"x = {answer}"
        else:
            answer = random.randint(1, 10)
            stem = f"解方程：2x + 3 = {2*answer + 3}，x = ?"
            solution = f"x = {answer}"

        return self._create_question(kp_id, "solve_equation", stem, answer, solution, difficulty=difficulty)

    def _gen_percentage(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """百分数"""
        patterns = [
            ("一本书原价80元，现价64元，打几折？", "八折", "64÷80=0.8=80%=八折"),
            ("一件衣服打8折后160元，原价多少？", "200元", "160÷0.8=200"),
            ("某班50人，今天到校48人，出勤率是多少？", "96%", "48÷50×100%=96%"),
        ]
        stem, answer, solution = random.choice(patterns)
        return self._create_question(kp_id, "percentage", stem, answer, solution, difficulty=difficulty)

    def _gen_shape_counting(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """图形计数"""
        stem = "下图中有几个三角形？(假设为3层三角形图)"
        answer = "7"
        solution = "上层1个+中层3个+下层3个=7个"
        common_error = "漏数了组合三角形"
        return self._create_question(kp_id, "shape_counting", stem, answer, solution, common_error, difficulty)

    def _gen_perimeter_area(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """周长面积计算"""
        if "长方形" in kp_name or "正方形" in kp_name or "多边形" in kp_name:
            length = random.randint(5, 20)
            width = random.randint(3, 15)
            if "正方形" in kp_name:
                width = length
                stem = f"一个正方形边长是{length}厘米，周长和面积分别是多少？"
                answer = f"周长={length*4}厘米，面积={length*length}平方厘米"
            else:
                stem = f"一个长方形长{length}厘米，宽{width}厘米，周长和面积分别是多少？"
                answer = f"周长={(length+width)*2}厘米，面积={length*width}平方厘米"
            solution = f"周长=(长+宽)×2，面积=长×宽"
            common_error = "周长和面积公式混淆"
        elif "圆" in kp_name:
            r = random.randint(3, 10)
            stem = f"一个圆的半径是{r}厘米，求周长和面积（π取3.14）"
            answer = f"周长={2*3.14*r:.2f}厘米，面积={3.14*r*r:.2f}平方厘米"
            solution = f"C=2πr，S=πr²"
            common_error = "忘记半径平方"
        elif "三角形" in kp_name:
            base = random.randint(5, 15)
            height = random.randint(3, 10)
            stem = f"三角形底{base}厘米，高{height}厘米，面积是多少？"
            answer = f"{base*height//2}平方厘米"
            solution = "S=底×高÷2"
            common_error = "忘记除以2"
        else:
            stem = "求下图的面积（单位：厘米）"
            answer = "需要具体图形"
            solution = "分割法或填补法"
            common_error = None

        return self._create_question(kp_id, "perimeter_area", stem, answer, solution, common_error, difficulty)

    def _gen_unit_conversion(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """单位换算"""
        conversions = [
            ("米", "厘米", 100, "3米 = （&#95;&#95;）厘米", "300"),
            ("千米", "米", 1000, "5千米 = （&#95;&#95;）米", "5000"),
            ("元", "角", 10, "6元 = （&#95;&#95;）角", "60"),
            ("小时", "分钟", 60, "2小时 = （&#95;&#95;）分钟", "120"),
            ("年", "月", 12, "3年 = （&#95;&#95;）月", "36"),
            ("吨", "千克", 1000, "2吨 = （&#95;&#95;）千克", "2000"),
            ("平方米", "平方分米", 100, "4平方米 = （&#95;&#95;）平方分米", "400"),
            ("克", "千克", 1000, "5000克 = （&#95;&#95;）千克", "5"),
        ]
        _, _, _, stem, answer = random.choice(conversions)
        return self._create_question(kp_id, "unit_conversion", stem, answer, difficulty=difficulty)

    def _gen_angle_measurement(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """角的度量"""
        angle = random.randint(20, 160)
        stem = f"量出这个角的度数（假设图为{angle}°角）"
        answer = f"{angle}°"
        solution = f"量角器中心点对准顶点，0刻度线对齐一边，读出度数"
        common_error = "读错内外圈刻度"
        return self._create_question(kp_id, "angle_measurement", stem, answer, solution, common_error, difficulty)

    def _gen_chart_analysis(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """统计图表分析"""
        stem = "小明家一周用水量统计：周一120升，周二110升，周三130升，周四100升，周五140升。平均每天用水多少升？"
        answer = "120升"
        solution = "(120+110+130+100+140)÷5=600÷5=120"
        return self._create_question(kp_id, "chart_analysis", stem, answer, solution, difficulty=difficulty)

    def _gen_word_problem(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """解决问题"""
        problems = [
            ("小明有35个苹果，小红比他多18个，小红有多少个苹果？", "53个", "35+18=53", "35+18=53（个）"),
            ("一本书有96页，小红看了48页，还剩多少页？", "48页", "96-48=48", "96-48=48（页）"),
            ("小明有24颗糖，平均分给4个小朋友，每人分几颗？", "6颗", "24÷4=6", "24÷4=6（颗）"),
            ("果园有苹果树36棵，梨树比苹果树少12棵，梨树有多少棵？", "24棵", "36-12=24", "36-12=24（棵）"),
            ("妈妈买了3袋苹果，每袋8个，一共买了多少个？", "24个", "3×8=24", "3×8=24（个）"),
            ("一根绳子长48米，剪成6段同样长的，每段多少米？", "8米", "48÷6=8", "48÷6=8（米）"),
        ]
        stem, answer, solution, formula = random.choice(problems)
        return self._create_question(kp_id, "word_problem", stem, answer, solution, difficulty=difficulty)

    def _gen_math_puzzle(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """数学广角"""
        puzzles = [
            ("用2、5、8可以组成多少个没有重复数字的两位数？", "6个", "25,28,52,58,82,85", "排列问题"),
            ("有4个小朋友，每两人握一次手，一共握几次？", "6次", "3+2+1=6", "组合问题"),
            ("把一根木料锯成5段，需要锯几次？", "4次", "5-1=4", "植树问题"),
            ("袋子里有红、黄、蓝三种球各1个，随机取2个，有几种可能？", "3种", "红黄、红蓝、黄蓝", "搭配问题"),
        ]
        stem, answer, solution, _ = random.choice(puzzles)
        return self._create_question(kp_id, "math_puzzle", stem, answer, solution, difficulty=difficulty)

    def _gen_oral_counting(self, kp_id: str, kp_name: str, difficulty: int) -> Dict[str, Any]:
        """数一数"""
        stem = "数一数下图中有几只小动物？(假设有5只)"
        answer = "5只"
        solution = "按顺序数，不重复不遗漏"
        common_error = "数重复或漏数"
        return self._create_question(kp_id, "oral_counting", stem, answer, solution, common_error, difficulty)
