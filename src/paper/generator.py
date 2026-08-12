"""练习卷生成器（扩展版）"""

import os
import random
from datetime import datetime
from typing import List, Dict, Optional

from ..database.repository import QuestionRepository, PaperRepository


class PaperGenerator:
    """练习卷生成器"""

    def __init__(self, repos: dict):
        self.question_repo = repos["question"]
        self.paper_repo = repos["paper"]

    def generate(self, knowledge_points: List[str] = None, grade: str = None,
                 count: int = 50, types: List[str] = None,
                 sections: Dict[str, int] = None,
                 type_order: List[str] = None,
                 difficulty: int = None,
                 with_answer: bool = True, with_error_tip: bool = False,
                 title: str = None, output_path: str = None,
                 random_order: bool = True) -> str:
        """
        生成练习卷

        参数:
            knowledge_points: 知识点列表（如 ["100以内进位加法"]）
            grade: 年级（如 "一年级"）
            count: 总题量（与 sections 互斥）
            types: 题型筛选（如 ["mental_arithmetic", "vertical_calculation"]）
            sections: 按题型指定数量（如 {"mental_arithmetic": 10, "word_problem": 3}）
            type_order: 题型顺序（如 ["mental_arithmetic", "vertical_calculation"]）
            difficulty: 难度筛选（1-5）
            with_answer: 包含答案页
            with_error_tip: 包含易错提示
            title: 试卷标题
            output_path: 输出路径
            random_order: 题目随机排序
        """

        # 1. 从题库选题
        if sections:
            # 按题型指定数量选题
            questions = self._select_questions_by_sections(
                sections, knowledge_points, grade, difficulty
            )
        else:
            # 统一选题
            questions = self._select_questions(
                knowledge_points, grade, count, types, difficulty
            )

        if not questions:
            raise ValueError("题库中没有符合条件的题目")

        # 2. 排序
        if random_order:
            random.shuffle(questions)

        # 3. 生成标题
        if not title:
            if knowledge_points:
                title = f"{'、'.join(knowledge_points[:2])}专项练习"
            elif grade:
                title = f"{grade}数学练习"
            else:
                title = "数学综合练习"

        # 4. 按题型分组
        grouped_sections = self._group_by_type(questions, type_order)

        # 5. 渲染PDF
        from .pdf_renderer import PDFRenderer
        renderer = PDFRenderer()

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            kp_part = "_".join(knowledge_points[:1]) if knowledge_points else "综合"
            output_path = f"data/output/{kp_part}_{len(questions)}题_{timestamp}.pdf"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        pdf_path = renderer.render_paper(
            title=title,
            sections=grouped_sections,
            grade=grade,
            knowledge_points="、".join(knowledge_points) if knowledge_points else "",
            with_answer=with_answer,
            with_error_tip=with_error_tip,
            output_path=output_path
        )

        # 6. 保存到数据库
        self.paper_repo.create(
            title=title,
            parameters={
                "knowledge_points": knowledge_points,
                "grade": grade,
                "count": count,
                "types": types,
                "sections": sections,
                "type_order": type_order,
                "difficulty": difficulty,
                "with_answer": with_answer,
                "with_error_tip": with_error_tip,
            },
            question_ids=[q.id for q in questions],
            pdf_path=pdf_path,
        )

        return pdf_path

    def _select_questions(self, knowledge_points: List[str], grade: str,
                          count: int, types: List[str],
                          difficulty: int = None) -> list:
        """从题库选题（统一数量）"""
        all_questions = []

        if knowledge_points:
            for kp_name in knowledge_points:
                from ..database.repository import KnowledgePointRepository
                kp_repo = KnowledgePointRepository(self.question_repo.db)
                kps = kp_repo.search_by_name(kp_name)
                if kps:
                    kp_id = kps[0].id
                    qs = self.question_repo.query(
                        knowledge_point_id=kp_id,
                        review_status="approved",
                        limit=count * 2  # 多取一些用于筛选
                    )
                    all_questions.extend(qs)
        elif grade:
            all_questions = self.question_repo.query(
                grade=grade,
                review_status="approved",
                limit=count * 2
            )
        else:
            all_questions = self.question_repo.query(
                review_status="approved",
                limit=count * 2
            )

        # 按题型筛选
        if types:
            all_questions = [q for q in all_questions if q.question_type in types]

        # 按难度筛选
        if difficulty:
            all_questions = [q for q in all_questions if q.difficulty == difficulty]

        return all_questions[:count]

    def _select_questions_by_sections(self, sections: Dict[str, int],
                                       knowledge_points: List[str], grade: str,
                                       difficulty: int = None) -> list:
        """按题型指定数量选题"""
        all_questions = []

        for q_type, type_count in sections.items():
            type_questions = []

            if knowledge_points:
                for kp_name in knowledge_points:
                    from ..database.repository import KnowledgePointRepository
                    kp_repo = KnowledgePointRepository(self.question_repo.db)
                    kps = kp_repo.search_by_name(kp_name)
                    if kps:
                        kp_id = kps[0].id
                        qs = self.question_repo.query(
                            knowledge_point_id=kp_id,
                            question_type=q_type,
                            review_status="approved",
                            limit=type_count * 2
                        )
                        type_questions.extend(qs)
            elif grade:
                type_questions = self.question_repo.query(
                    grade=grade,
                    question_type=q_type,
                    review_status="approved",
                    limit=type_count * 2
                )
            else:
                type_questions = self.question_repo.query(
                    question_type=q_type,
                    review_status="approved",
                    limit=type_count * 2
                )

            # 按难度筛选
            if difficulty:
                type_questions = [q for q in type_questions if q.difficulty == difficulty]

            # 取指定数量
            type_questions = type_questions[:type_count]
            all_questions.extend(type_questions)

            if len(type_questions) < type_count:
                print(f"  警告: 题型 '{q_type}' 只有 {len(type_questions)} 道题，少于请求的 {type_count} 道")

        return all_questions

    def _group_by_type(self, questions: list, type_order: List[str] = None) -> List[Dict]:
        """按题型分组，并统一编号"""
        # 默认题型顺序
        default_type_order = [
            "oral_counting", "number_read_write", "number_composition",
            "compare_size", "pattern_sequence", "mental_arithmetic",
            "vertical_calculation", "step_calculation", "fill_unknown",
            "verification", "estimation", "simplified_calculation",
            "composite_expression", "solve_equation", "percentage",
            "unit_conversion", "angle_measurement", "shape_counting",
            "perimeter_area", "chart_analysis", "word_problem", "math_puzzle",
        ]

        order = type_order if type_order else default_type_order

        # 题区中文名（不带编号，编号在下方按实际出现顺序生成）
        type_names = {
            "mental_arithmetic": "口算题",
            "vertical_calculation": "竖式计算",
            "step_calculation": "脱式计算",
            "fill_unknown": "填未知数",
            "number_composition": "数的组成",
            "number_read_write": "数的读写",
            "compare_size": "比大小",
            "pattern_sequence": "规律填数",
            "verification": "验算题",
            "estimation": "估算题",
            "simplified_calculation": "简便计算",
            "composite_expression": "列综合算式",
            "solve_equation": "解方程",
            "percentage": "百分数",
            "shape_counting": "图形计数",
            "perimeter_area": "周长面积",
            "unit_conversion": "单位换算",
            "angle_measurement": "角的度量",
            "chart_analysis": "统计图表",
            "word_problem": "解决问题",
            "math_puzzle": "数学广角",
            "oral_counting": "数一数",
        }

        groups = {}
        for q in questions:
            if q.question_type not in groups:
                groups[q.question_type] = []
            groups[q.question_type].append(q)

        # 中文序号（一、二、三……）
        cn_nums = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
                   "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八",
                   "十九", "二十", "二十一", "二十二"]

        ordered_types = []
        for t in order:
            if t in groups:
                ordered_types.append(t)
        # 添加未在顺序表中的题型
        ordered_types.extend(t for t in groups if t not in order)

        sections = []
        question_number = 1

        for idx, t in enumerate(ordered_types):
            qs = groups[t]
            for q in qs:
                q.number = question_number
                question_number += 1
            sections.append({
                "type": t,
                "title": f"{cn_nums[idx] if idx < len(cn_nums) else idx + 1}、{type_names.get(t, t)}",
                "questions": qs
            })

        return sections
