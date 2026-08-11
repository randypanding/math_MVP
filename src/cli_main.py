"""CLI 命令处理主逻辑"""

import sys
import json
from datetime import datetime

from .config import config
from .database.models import Base
from .database.repository import (
    Database, KnowledgePointRepository, QuestionRepository,
    PaperRepository, ErrorSetRepository, ProcessingLogRepository
)

# 全局数据库实例
_db = None


def get_db() -> Database:
    """获取数据库实例（懒加载）"""
    global _db
    if _db is None:
        _db = Database(config.db_path)
    return _db


def get_repos():
    """获取所有仓库实例"""
    db = get_db()
    return {
        "kp": KnowledgePointRepository(db),
        "question": QuestionRepository(db),
        "paper": PaperRepository(db),
        "error": ErrorSetRepository(db),
        "log": ProcessingLogRepository(db),
    }


def handle_command(args):
    """命令分发"""
    command_map = {
        "generate-questions": cmd_generate_questions,
        "generate": cmd_generate,
        "extract": cmd_extract,
        "batch": cmd_batch,
        "review": cmd_review,
        "query": cmd_query,
        "stats": cmd_stats,
        "import-error": cmd_import_error,
        "error-practice": cmd_error_practice,
        "config": cmd_config,
    }

    handler = command_map.get(args.command)
    if handler:
        try:
            handler(args)
        except KeyboardInterrupt:
            print("\n操作已取消")
            sys.exit(130)
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"未知命令: {args.command}", file=sys.stderr)
        sys.exit(1)


def cmd_generate_questions(args):
    """处理 generate-questions 命令"""
    from .generator.knowledge_points import load_knowledge_points
    from .generator.base import generate_for_knowledge_point

    repos = get_repos()

    if args.all:
        # 生成所有知识点
        kps = load_knowledge_points()
        total = 0
        for kp in kps:
            count = generate_for_knowledge_point(kp, args.count, repos["question"])
            total += count
            print(f"  {kp['name']}: {count} 题")
        print(f"\n共生成 {total} 道题目")
    elif args.grade:
        # 按年级生成
        kps = load_knowledge_points(grade=args.grade)
        total = 0
        for kp in kps:
            count = generate_for_knowledge_point(kp, args.count, repos["question"])
            total += count
            print(f"  {kp['name']}: {count} 题")
        print(f"\n共生成 {total} 道题目")
    elif args.kp:
        # 按知识点名称生成
        kps = load_knowledge_points(name=args.kp)
        if not kps:
            print(f"未找到知识点: {args.kp}")
            sys.exit(1)
        total = 0
        for kp in kps:
            count = generate_for_knowledge_point(kp, args.count, repos["question"])
            total += count
            print(f"  {kp['name']}: {count} 题")
        print(f"\n共生成 {total} 道题目")
    else:
        print("请指定 --all、--grade 或 --kp")
        sys.exit(1)


def cmd_generate(args):
    """处理 generate 命令"""
    from .paper.generator import PaperGenerator

    repos = get_repos()
    gen = PaperGenerator(repos)

    params = {
        "knowledge_points": args.kp.split(",") if args.kp else None,
        "grade": args.grade,
        "count": args.count,
        "types": args.types.split(",") if args.types else None,
        "with_answer": args.with_answer,
        "with_error_tip": args.with_error_tip,
        "title": args.title,
    }

    pdf_path = gen.generate(
        output_path=args.output,
        **params
    )
    print(f"已生成: {pdf_path}")


def cmd_extract(args):
    """处理 extract 命令"""
    from .extractor.doc_reader import extract_from_doc

    if not args.file.endswith('.doc'):
        print("错误: 只支持 .doc 格式文件", file=sys.stderr)
        sys.exit(1)

    result = extract_from_doc(args.file)
    print(f"提取完成: {result.get('question_count', 0)} 道题目")
    print(f"输出: {result.get('output_path', 'N/A')}")


def cmd_batch(args):
    """处理 batch 命令"""
    import os
    from .extractor.doc_reader import extract_from_doc

    if not os.path.isdir(args.folder):
        print(f"错误: 目录不存在 {args.folder}", file=sys.stderr)
        sys.exit(1)

    files = []
    if args.recursive:
        for root, _, filenames in os.walk(args.folder):
            for f in filenames:
                if f.endswith('.doc'):
                    files.append(os.path.join(root, f))
    else:
        for f in os.listdir(args.folder):
            if f.endswith('.doc'):
                files.append(os.path.join(args.folder, f))

    print(f"找到 {len(files)} 个 .doc 文件")
    success = 0
    failed = 0
    for filepath in files:
        try:
            result = extract_from_doc(filepath)
            print(f"  ✓ {os.path.basename(filepath)}: {result.get('question_count', 0)} 题")
            success += 1
        except Exception as e:
            print(f"  ✗ {os.path.basename(filepath)}: {e}")
            failed += 1

    print(f"\n处理完成: 成功 {success}, 失败 {failed}")


def cmd_review(args):
    """处理 review 命令"""
    from .review.cli_review import start_review

    repos = get_repos()
    start_review(repos, kp_filter=args.kp, limit=args.limit)


def cmd_query(args):
    """处理 query 命令"""
    repos = get_repos()

    # 如果按知识点名称搜索，先找到对应ID
    kp_id = None
    if args.kp:
        kps = repos["kp"].search_by_name(args.kp)
        if kps:
            kp_id = kps[0].id

    questions = repos["question"].query(
        knowledge_point_id=kp_id,
        grade=args.grade,
        question_type=args.type,
        difficulty=args.difficulty,
        review_status=args.status,
        limit=args.limit
    )

    if args.json_output:
        data = [{
            "id": q.id,
            "type": q.question_type,
            "stem": q.stem,
            "answer": q.answer,
            "difficulty": q.difficulty,
            "status": q.review_status,
        } for q in questions]
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"{'ID':<5} {'题型':<15} {'题目':<30} {'答案':<10} {'难度':<5} {'状态':<10}")
        print("-" * 80)
        for q in questions:
            stem = q.stem[:27] + "..." if len(q.stem) > 30 else q.stem
            print(f"{q.id:<5} {q.question_type:<15} {stem:<30} {str(q.answer):<10} {q.difficulty:<5} {q.review_status:<10}")
        print(f"\n共 {len(questions)} 道题目")


def cmd_stats(args):
    """处理 stats 命令"""
    repos = get_db()

    # 题目统计
    q_repo = QuestionRepository(repos)
    kp_repo = KnowledgePointRepository(repos)
    log_repo = ProcessingLogRepository(repos)

    total_questions = q_repo.count()
    approved = q_repo.count(review_status="approved")
    pending = q_repo.count(review_status="pending")
    total_kps = kp_repo.count()
    log_stats = log_stats = log_repo.get_stats()

    if hasattr(args, 'json_output') and args.json_output:
        data = {
            "questions": {
                "total": total_questions,
                "approved": approved,
                "pending": pending,
            },
            "knowledge_points": total_kps,
            "processing": log_stats,
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("题库统计")
        print("========")
        print(f"总题数: {total_questions}")
        print(f"  已审核: {approved}")
        print(f"  待审核: {pending}")
        print(f"知识点数: {total_kps}")
        print(f"\n处理统计")
        print(f"  已处理文件: {log_stats['total_files']}")
        print(f"  成功: {log_stats['success']}")
        print(f"  失败: {log_stats['failed']}")
        print(f"  部分成功: {log_stats['partial']}")
        print(f"  提取题目总数: {log_stats['total_questions_extracted']}")


def cmd_import_error(args):
    """处理 import-error 命令"""
    from .error_trainer.error_set import import_error_image

    repos = get_repos()
    result = import_error_image(args.image, repos, kp=args.kp)
    print(f"已导入错题: {result}")


def cmd_error_practice(args):
    """处理 error-practice 命令"""
    from .error_trainer.error_set import generate_error_practice

    repos = get_repos()
    pdf_path = generate_error_practice(repos, count=args.count,
                                        output_path=args.output,
                                        with_answer=args.with_answer)
    print(f"已生成错题练习: {pdf_path}")


def cmd_config(args):
    """处理 config 命令"""
    if not hasattr(args, 'cfg_command') or not args.cfg_command:
        # 显示当前配置
        print("当前配置")
        print("========")
        print(f"LLM 提供商: {config.llm_provider}")
        print(f"LLM 模型: {config.llm_model}")
        print(f"API Base URL: {config.llm_base_url}")
        print(f"API Key: {'已设置' if config.llm_api_key else '未设置'}")
        print(f"数据库路径: {config.db_path}")
    elif args.cfg_command == "show":
        print("当前配置")
        print("========")
        print(f"LLM 提供商: {config.llm_provider}")
        print(f"LLM 模型: {config.llm_model}")
        print(f"API Base URL: {config.llm_base_url}")
        print(f"API Key: {'已设置' if config.llm_api_key else '未设置'}")
        print(f"数据库路径: {config.db_path}")
    elif args.cfg_command == "set-model":
        print(f"模型已设置为: {args.model}")
        print("提示: 请手动修改 config.yaml 中的 llm.model 值")
    elif args.cfg_command == "set-api-key":
        print("API Key 已设置")
        print("提示: 请将 Key 填入 .env 文件: LLM_API_KEY=your-key")
