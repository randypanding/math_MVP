"""生成一份完整的示例卷子并验证"""
import sys
sys.path.insert(0, '.')

from src.database.repository import Database, QuestionRepository, KnowledgePointRepository, PaperRepository
from src.paper.generator import PaperGenerator
from src.paper.pdf_renderer import PDFRenderer
import os

# 初始化数据库
db = Database('data/mathgen.db')
q_repo = QuestionRepository(db)
kp_repo = KnowledgePointRepository(db)
p_repo = PaperRepository(db)

# 获取各种题型的题目
repos = {'question': q_repo, 'paper': p_repo, 'kp': kp_repo}

# 口算题
mental = q_repo.query(knowledge_point_id='G1U07KP01', review_status='approved', limit=12)
if not mental:
    mental = q_repo.query(question_type='mental_arithmetic', review_status='approved', limit=12)

# 列式计算
vertical = q_repo.query(knowledge_point_id='G1U07KP01', review_status='approved', limit=4)
if not vertical:
    vertical = q_repo.query(question_type='mental_arithmetic', review_status='approved', limit=4)

# 单位换算
unit = q_repo.query(question_type='unit_conversion', review_status='approved', limit=6)

# 创建 sections
sections = []

if mental:
    for i, q in enumerate(mental, 1):
        q.number = i
    sections.append({
        'type': 'mental_arithmetic',
        'title': '一、口算题',
        'questions': mental
    })

if vertical:
    for i, q in enumerate(vertical, len(mental)+1 if mental else 1):
        q.number = i
    sections.append({
        'type': 'vertical_calculation',
        'title': '二、列式计算',
        'questions': vertical
    })

if unit:
    start = len(mental) + len(vertical) + 1 if mental and vertical else 1
    for i, q in enumerate(unit, start):
        q.number = i
    sections.append({
        'type': 'unit_conversion',
        'title': '三、单位换算',
        'questions': unit
    })

# 添加应用题
word_problems = [
    {
        'number': len(mental) + len(vertical) + len(unit) + 1 if mental and vertical and unit else 1,
        'stem': '果园里有苹果树30棵，梨树26棵，苹果和梨一共有多少棵？',
        'answer': '56棵',
        'solution': '30 + 26 = 56（棵）',
        'common_error': '易错：可能算成30 - 26 = 4',
        'knowledge_point_id': 'G1U07KP01',
        'question_type': 'word_problem',
        'review_status': 'approved',
        'difficulty': 1,
        'source': '程序生成',
    },
    {
        'number': len(mental) + len(vertical) + len(unit) + 2 if mental and vertical and unit else 2,
        'stem': '小红有75朵花，送给小丽20朵，小红还剩多少朵花？',
        'answer': '55朵',
        'solution': '75 - 20 = 55（朵）',
        'common_error': '易错：可能算成75 + 20 = 95',
        'knowledge_point_id': 'G1U07KP01',
        'question_type': 'word_problem',
        'review_status': 'approved',
        'difficulty': 1,
        'source': '程序生成',
    },
]

# 创建 Question 对象
from src.database.models import Question
word_qs = []
for wp in word_problems:
    num = wp.pop('number')
    q = Question(**wp)
    q.number = num
    word_qs.append(q)

if word_qs:
    sections.append({
        'type': 'word_problem',
        'title': '四、解决问题',
        'questions': word_qs
    })

# 渲染PDF
renderer = PDFRenderer()
os.makedirs('data/output', exist_ok=True)

pdf_path = renderer.render_paper(
    title='一年级数学下册计算每日一练',
    sections=sections,
    grade='一年级',
    knowledge_points='100以内加减法',
    with_answer=True,
    with_error_tip=True,
    output_path='data/output/测试卷_完整版.pdf'
)

print(f'PDF 已生成: {pdf_path}')
print(f'文件大小: {os.path.getsize(pdf_path)} bytes')

# 打印题目编号验证
print('\n题目编号验证:')
for section in sections:
    nums = [q.number for q in section['questions']]
    print(f'  {section["title"]}: {nums}')
