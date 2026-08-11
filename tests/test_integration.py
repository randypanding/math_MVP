"""集成自测：验证结构化易错模式字段能通过完整管线持久化到数据库"""
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

tmpdir = tempfile.mkdtemp()
db_path = os.path.join(tmpdir, "test_integ.db")

# 使用独立临时数据库
from src.database.repository import Database, QuestionRepository, KnowledgePointRepository
from src.generator.knowledge_points import load_knowledge_points
from src.generator.base import generate_for_knowledge_point

db = Database(db_path)
q_repo = QuestionRepository(db)
kp_repo = KnowledgePointRepository(db)

# 选几个覆盖不同主题的知识点
kps = load_knowledge_points()
targets = [kp for kp in kps if any(k in kp["name"] for k in
             ["分数", "小数", "周长", "比", "进位加法", "除法"])][:5]
print(f"== 集成自测：{len(targets)} 个知识点 ==\n")

for kp in targets:
    n = generate_for_knowledge_point(kp, 8, q_repo)
    print(f"  {kp['name']}: 生成 {n} 题")
    # 抽样验证持久化字段
    qs = q_repo.query(knowledge_point_id=kp["id"], limit=3)
    for q in qs:
        assert q.error_category, f"{kp['name']} 缺 error_category"
        assert q.pattern_name, f"{kp['name']} 缺 pattern_name"
        assert q.wrong_rule and q.correct_rule, f"{kp['name']} 缺规则字段"
        assert q.steps, f"{kp['name']} 缺 steps"
        assert q.socratic_hints, f"{kp['name']} 缺 hints"
        assert q.distractor_mapping, f"{kp['name']} 缺 distractor"
        assert q.solution_status == "targeted", f"{kp['name']} solution_status错"
        # steps/hints/distractor 存的是JSON字符串，可反序列化
        json.loads(q.steps)
        json.loads(q.socratic_hints)
        json.loads(q.distractor_mapping)
    print(f"    抽查 {len(qs)} 题：结构化字段均已持久化 ✅")

total = q_repo.count()
print(f"\n入库题目总数: {total}")
assert total > 0

# 统计错误类别分布
from sqlalchemy import func
from src.database.models import Question
from sqlalchemy.orm import Session
s = db.get_session()
cats = s.query(Question.error_category, func.count()).group_by(Question.error_category).all()
s.close()
print("错误类别分布:", dict(cats))
print("\n集成自测全部通过 ✅")