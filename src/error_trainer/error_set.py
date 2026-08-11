"""错题重练模块"""

import os
from datetime import datetime
from ..database.repository import ErrorSetRepository, QuestionRepository, PaperRepository


def import_error_image(image_path: str, repos: dict, kp: str = None) -> str:
    """导入错题图片"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片不存在: {image_path}")

    # 复制图片到数据目录
    target_dir = "data/images"
    os.makedirs(target_dir, exist_ok=True)
    filename = os.path.basename(image_path)
    target_path = os.path.join(target_dir, f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")

    import shutil
    shutil.copy2(image_path, target_path)

    # 创建错题记录（需要手动关联题目，或OCR识别后创建）
    error_repo: ErrorSetRepository = repos["error"]

    # 如果有关联知识点，尝试查找对应题目
    if kp:
        q_repo: QuestionRepository = repos["question"]
        kps = repos["kp"].search_by_name(kp)
        if kps:
            questions = q_repo.query(knowledge_point_id=kps[0].id, limit=1)
            if questions:
                error_repo.create(
                    question_id=questions[0].id,
                    source_image=target_path
                )
                return f"已导入错题图片并关联题目(ID: {questions[0].id})"

    # 仅导入图片，不关联题目
    error_repo.create(question_id=0, source_image=target_path)
    return f"已导入错题图片: {target_path}（未关联题目）"


def generate_error_practice(repos: dict, count: int = 20,
                           output_path: str = None, with_answer: bool = True) -> str:
    """生成错题专项练习"""
    error_repo: ErrorSetRepository = repos["error"]
    q_repo: QuestionRepository = repos["question"]

    # 获取错题集
    error_ids = error_repo.get_question_ids()
    if not error_ids:
        raise ValueError("错题集为空，请先导入错题")

    # 获取错题对应的题目
    questions = []
    for qid in error_ids[:count]:
        q = q_repo.get_by_id(qid)
        if q:
            questions.append(q)

    if not questions:
        raise ValueError("错题集中没有有效题目")

    # 使用 PaperGenerator 生成PDF
    from .paper.generator import PaperGenerator
    gen = PaperGenerator(repos)

    # 这里简化处理，直接调用generate
    from .paper.pdf_renderer import PDFRenderer
    renderer = PDFRenderer()

    # 准备数据
    question_number = 1
    for q in questions:
        q.number = question_number
        question_number += 1

    sections = [{
        "type": "error_review",
        "title": "错题重练",
        "questions": questions
    }]

    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/output/错题专项练习_{timestamp}.pdf"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 渲染
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader("templates"))

    template = env.get_template("paper.html")
    html = template.render(
        title="错题专项练习",
        grade="",
        knowledge_points="错题重练",
        questions=len(questions),
        sections=sections,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    if with_answer:
        answer_template = env.get_template("answer.html")
        answer_html = answer_template.render(
            title="错题专项练习",
            sections=sections,
        )
        html += '<div style="page-break-before: always;"></div>' + answer_html

    from weasyprint import HTML
    HTML(string=html).write_pdf(output_path)

    return output_path
