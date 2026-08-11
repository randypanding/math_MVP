"""统计报告模块"""

from datetime import datetime, timedelta
from ..database.repository import (
    QuestionRepository, KnowledgePointRepository,
    PaperRepository, ProcessingLogRepository
)


class StatsReporter:
    """统计报告生成器"""

    def __init__(self, repos: dict):
        self.q_repo: QuestionRepository = repos["question"]
        self.kp_repo: KnowledgePointRepository = repos["kp"]
        self.p_repo: PaperRepository = repos["paper"]
        self.log_repo: ProcessingLogRepository = repos["log"]

    def get_full_report(self) -> dict:
        """获取完整统计报告"""
        return {
            "overview": self._get_overview(),
            "by_grade": self._get_by_grade(),
            "by_type": self._get_by_type(),
            "by_difficulty": self._get_by_difficulty(),
            "processing": self._get_processing_stats(),
            "recent_papers": self._get_recent_papers(),
        }

    def _get_overview(self) -> dict:
        """题库概况"""
        total = self.q_repo.count()
        approved = self.q_repo.count(review_status="approved")
        pending = self.q_repo.count(review_status="pending")
        rejected = self.q_repo.count(review_status="rejected")
        kps = self.kp_repo.count()

        return {
            "total_questions": total,
            "approved": approved,
            "pending": pending,
            "rejected": rejected,
            "knowledge_points": kps,
        }

    def _get_by_grade(self) -> dict:
        """按年级统计"""
        kps = self.kp_repo.get_all()
        grade_stats = {}
        for kp in kps:
            count = self.q_repo.count(knowledge_point_id=kp.id)
            if kp.grade not in grade_stats:
                grade_stats[kp.grade] = 0
            grade_stats[kp.grade] += count
        return grade_stats

    def _get_by_type(self) -> dict:
        """按题型统计"""
        # 这里简化处理，实际应该用SQL GROUP BY
        questions = self.q_repo.query(limit=10000)
        type_stats = {}
        for q in questions:
            if q.question_type not in type_stats:
                type_stats[q.question_type] = 0
            type_stats[q.question_type] += 1
        return type_stats

    def _get_by_difficulty(self) -> dict:
        """按难度统计"""
        questions = self.q_repo.query(limit=10000)
        diff_stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for q in questions:
            if q.difficulty in diff_stats:
                diff_stats[q.difficulty] += 1
        return diff_stats

    def _get_processing_stats(self) -> dict:
        """处理统计"""
        return self.log_repo.get_stats()

    def _get_recent_papers(self) -> list:
        """最近生成的练习卷"""
        papers = self.p_repo.get_all()[:10]
        return [{"id": p.id, "title": p.title, "created_at": str(p.created_at)} for p in papers]

    def print_report(self):
        """打印报告"""
        report = self.get_full_report()

        print("=" * 50)
        print("数学练习卷生成器 - 统计报告")
        print("=" * 50)

        # 题库概况
        overview = report["overview"]
        print("\n【题库概况】")
        print(f"  总题数: {overview['total_questions']}")
        print(f"  已审核: {overview['approved']}")
        print(f"  待审核: {overview['pending']}")
        print(f"  已驳回: {overview['rejected']}")
        print(f"  知识点数: {overview['knowledge_points']}")

        # 年级分布
        print("\n【年级分布】")
        for grade, count in sorted(report["by_grade"].items()):
            print(f"  {grade}: {count} 题")

        # 题型分布
        print("\n【题型分布】")
        type_names = {
            "mental_arithmetic": "口算题", "vertical_calculation": "竖式计算",
            "step_calculation": "脱式计算", "fill_unknown": "填未知数",
            "number_composition": "数的组成", "number_read_write": "数的读写",
            "compare_size": "比大小", "pattern_sequence": "规律填数",
            "verification": "验算题", "estimation": "估算题",
            "simplified_calculation": "简便计算", "composite_expression": "列综合算式",
            "solve_equation": "解方程", "percentage": "百分数",
            "shape_counting": "图形计数", "perimeter_area": "周长面积",
            "unit_conversion": "单位换算", "angle_measurement": "角的度量",
            "chart_analysis": "统计图表", "word_problem": "解决问题",
            "math_puzzle": "数学广角", "oral_counting": "数一数",
        }
        for qtype, count in sorted(report["by_type"].items(), key=lambda x: -x[1]):
            name = type_names.get(qtype, qtype)
            print(f"  {name}: {count} 题")

        # 难度分布
        print("\n【难度分布】")
        for diff, count in sorted(report["by_difficulty"].items()):
            print(f"  难度{diff}: {count} 题")

        # 处理统计
        proc = report["processing"]
        print("\n【处理统计】")
        print(f"  已处理文件: {proc['total_files']}")
        print(f"  成功: {proc['success']}")
        print(f"  失败: {proc['failed']}")
        print(f"  部分成功: {proc['partial']}")
        print(f"  提取题目总数: {proc['total_questions_extracted']}")

        print("\n" + "=" * 50)
