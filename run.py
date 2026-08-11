"""
数学练习卷生成器 - 一键生成脚本
生成全量题目 + 示例PDF + 统计报告
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.repository import (
    Database, QuestionRepository, KnowledgePointRepository,
    PaperRepository, ProcessingLogRepository
)
from src.generator.knowledge_points import load_knowledge_points
from src.generator.base import generate_for_knowledge_point
from src.paper.generator import PaperGenerator
from src.stats.reports import StatsReporter
from collections import Counter

# 初始化
db = Database('data/mathgen.db')
q_repo = QuestionRepository(db)
kp_repo = KnowledgePointRepository(db)
p_repo = PaperRepository(db)
log_repo = ProcessingLogRepository(db)

print("=" * 60)
print("数学专题练习卷生成器 - 全量生成")
print("=" * 60)

# 1. 生成题目
print("\n[1/3] 生成题目...")
kps = load_knowledge_points()
total = 0
for kp in kps:
    count = generate_for_knowledge_point(kp, 10, q_repo)
    total += count

all_questions = q_repo.query(review_status="approved", limit=100000)
print(f"  新增: {total} 题")
print(f"  题库总题数: {len(all_questions)} 题")

# 2. 生成示例PDF
print("\n[2/3] 生成示例PDF...")
repos = {"question": q_repo, "paper": p_repo, "kp": kp_repo, "log": log_repo}
gen = PaperGenerator(repos)
os.makedirs("data/output", exist_ok=True)

sample_configs = [
    {"kp": ["20以内进位加法"], "title": "20以内进位加法专项练习"},
    {"kp": ["100以内加法(二)", "100以内减法(二)"], "title": "100以内加减法专项练习"},
    {"kp": ["表内乘法(一)", "表内乘法(二)"], "title": "表内乘法专项练习"},
    {"kp": ["混合运算"], "title": "混合运算专项练习"},
    {"kp": ["小数乘法"], "title": "小数乘法专项练习"},
    {"kp": ["分数乘法"], "title": "分数乘法专项练习"},
]

for config in sample_configs:
    try:
        pdf_path = gen.generate(
            knowledge_points=config["kp"],
            count=30,
            with_answer=True,
            with_error_tip=True,
            title=config["title"],
            output_path=f"data/output/{config['title']}.pdf"
        )
        size = os.path.getsize(pdf_path)
        print(f"  [OK] {config['title']}.pdf ({size//1024}KB)")
    except Exception as e:
        print(f"  [SKIP] {config['title']}: {e}")

# 3. 统计报告
print("\n[3/3] 统计报告...")
reporter = StatsReporter(repos)
reporter.print_report()

print("\n" + "=" * 60)
print("生成完成！PDF 文件位于 data/output/ 目录")
print("=" * 60)
