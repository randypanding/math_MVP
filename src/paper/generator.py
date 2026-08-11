"""练习卷生成器"""

import os
import random
from datetime import datetime
from typing import List, Dict, Optional


class PaperGenerator:
    """练习卷生成器"""

    def __init__(self, repos: dict):
        self.question_repo: QuestionRepository = repos["question"]
        self.paper_repo: PaperRepository = repos["paper"]

    def generate(self, knowledge_points: List[str] = None, grade: str = None,
                 count: int = 50, types: List[str] = None,
                 with_answer: bool = True, with_error_tip: bool = False,
                 title: str = None, output_path: str = None) -> str:
        """生成练习卷"""

        # 1. 从题库选题
        questions = self._select_questions(knowledge_points, grade, count, types)

        if not questions:
            raise ValueError("题库中没有符合条件的题目")

        if len(questions) < count:
            print(f"警告: 题库中只有 {len(questions)} 道符合条件的题目，少于请求的 {count} 道")

        # 2. 随机排序
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
        sections = self._group_by_type(questions)

        # 5. 渲染PDF
        from .pdf_renderer import PDFRenderer
        renderer = PDFRenderer()

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            kp_part = "_".join(knowledge_points[:1]) if knowledge_points else "综合"
            output_path = f"data/output/{kp_part}_{count}题_{timestamp}.pdf"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        pdf_path = renderer.render_paper(
            title=title,
            sections=sections,
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
                "with_answer": with_answer,
                "with_error_tip": with_error_tip,
            },
            question_ids=[q.id for q in questions],
            pdf_path=pdf_path,
        )

        return pdf_path

    def _select_questions(self, knowledge_points: List[str], grade: str,
                          count: int, types: List[str]) -> list:
        """从题库选题"""
        all_questions = []

        if knowledge_points:
            for kp_name in knowledge_points:
                # 先搜索知识点ID
                from ..database.repository import KnowledgePointRepository
                kp_repo = KnowledgePointRepository(self.question_repo.db)
                kps = kp_repo.search_by_name(kp_name)
                if kps:
                    kp_id = kps[0].id
                    qs = self.question_repo.query(
                        knowledge_point_id=kp_id,
                        review_status="approved",
                        limit=count
                    )
                    all_questions.extend(qs)
        elif grade:
            all_questions = self.question_repo.query(
                grade=grade,
                review_status="approved",
                limit=count
            )
        else:
            all_questions = self.question_repo.query(
                review_status="approved",
                limit=count
            )

        # 按题型筛选
        if types:
            all_questions = [q for q in all_questions if q.question_type in types]

        return all_questions[:count]

    def _group_by_type(self, questions: list) -> List[Dict]:
        """按题型分组，并统一编号"""
        type_order = [
            "oral_counting", "number_read_write", "number_composition",
            "compare_size", "pattern_sequence", "mental_arithmetic",
            "vertical_calculation", "step_calculation", "fill_unknown",
            "verification", "estimation", "simplified_calculation",
            "composite_expression", "solve_equation", "percentage",
            "unit_conversion", "angle_measurement", "shape_counting",
            "perimeter_area", "chart_analysis", "word_problem", "math_puzzle",
        ]

        type_names = {
            "mental_arithmetic": "一、口算题",
            "vertical_calculation": "二、竖式计算",
            "step_calculation": "三、脱式计算",
            "fill_unknown": "四、填未知数",
            "number_composition": "五、数的组成",
            "number_read_write": "六、数的读写",
            "compare_size": "七、比大小",
            "pattern_sequence": "八、规律填数",
            "verification": "九、验算题",
            "estimation": "十、估算题",
            "simplified_calculation": "十一、简便计算",
            "composite_expression": "十二、列综合算式",
            "solve_equation": "十三、解方程",
            "percentage": "十四、百分数",
            "shape_counting": "十五、图形计数",
            "perimeter_area": "十六、周长面积",
            "unit_conversion": "十七、单位换算",
            "angle_measurement": "十八、角的度量",
            "chart_analysis": "十九、统计图表",
            "word_problem": "二十、解决问题",
            "math_puzzle": "二十一、数学广角",
            "oral_counting": "数一数",
        }

        groups = {}
        for q in questions:
            if q.question_type not in groups:
                groups[q.question_type] = []
            groups[q.question_type].append(q)

        sections = []
        question_number = 1
        for t in type_order:
            if t in groups:
                qs = groups[t]
                for q in qs:
                    q.number = question_number
                    question_number += 1
                sections.append({
                    "type": t,
                    "title": type_names.get(t, t),
                    "questions": qs
                })

        # 添加未在顺序表中的题型
        for t, qs in groups.items():
            if t not in type_order:
                for q in qs:
                    q.number = question_number
                    question_number += 1
                sections.append({
                    "type": t,
                    "title": type_names.get(t, t),
                    "questions": qs
                })

        return sections
