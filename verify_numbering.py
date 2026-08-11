"""验证编号是否正确"""
import sys
sys.path.insert(0, '.')
from src.database.repository import Database, QuestionRepository
from src.paper.generator import PaperGenerator

db = Database('data/mathgen.db')
q_repo = QuestionRepository(db)

# 获取一些题目
questions = q_repo.query(review_status='approved', limit=30)

# 测试编号
gen = PaperGenerator({'question': q_repo, 'paper': None, 'kp': None})
sections = gen._group_by_type(questions)

print('编号验证:')
for section in sections:
    nums = [q.number for q in section['questions']]
    title = section['title']
    print(f'  {title}: {nums}')

# 检查编号是否连续
all_nums = []
for section in sections:
    all_nums.extend([q.number for q in section['questions']])

print(f'\n总编号范围: {min(all_nums)} - {max(all_nums)}')
print(f'题目总数: {len(all_nums)}')
print(f'是否连续: {sorted(all_nums) == list(range(1, len(all_nums)+1))}')
