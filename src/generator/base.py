"""题目生成器基类"""

import random
from typing import List, Dict, Any, Optional
from ..database.repository import QuestionRepository




class BaseGenerator:
    """题目生成器基类"""

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)

    def generate(self, count: int, knowledge_point: dict, **kwargs) -> List[Dict[str, Any]]:
        """生成题目，子类必须实现"""
        raise NotImplementedError

    def _create_question(self, knowledge_point_id: str, question_type: str,
                         stem: str, answer: str, solution: str = None,
                         common_error: str = None, difficulty: int = 1,
                         source: str = "程序生成") -> Dict[str, Any]:
        """创建题目字典"""
        return {
            "knowledge_point_id": knowledge_point_id,
            "question_type": question_type,
            "stem": stem,
            "answer": str(answer),
            "solution": solution,
            "common_error": common_error,
            "difficulty": difficulty,
            "source": source,
            "review_status": "approved",  # 程序化生成自动通过
        }


def generate_for_knowledge_point(kp: dict, count: int, repo: QuestionRepository) -> int:
    """为指定知识点生成题目（含易错模式）"""
    # 延迟导入避免循环
    from .error_patterns import generate_question_with_errors
    from ..database.repository import KnowledgePointRepository

    # 确保知识点在数据库中
    kp_repo = KnowledgePointRepository(repo.db)
    existing = kp_repo.get_by_id(kp['id'])
    if not existing:
        kp_repo.create(
            id=kp['id'],
            name=kp['name'],
            grade=kp['grade'],
            semester=kp['semester'],
            unit=kp.get('unit'),
            question_types=kp.get('types'),
            difficulty_range=kp.get('difficulty_range'),
        )

    # 生成带易错模式的题目
    questions = []
    difficulty_range = kp.get('difficulty', [1, 3])
    for _ in range(count):
        difficulty = random.randint(difficulty_range[0], difficulty_range[1])
        # 传入完整知识点字典（含 types/grade/semester），驱动类型选择与年级感知模板
        q = generate_question_with_errors(kp['id'], kp['name'], difficulty, kp=kp)
        questions.append(q)

    # 去重：同一知识点内按题干哈希去重，避免一份卷子出现重复题
    seen = set()
    unique = []
    for q in questions:
        key = q.get("stem", "").strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(q)
    questions = unique

    if questions:
        repo.create_batch(questions)
    return len(questions)
