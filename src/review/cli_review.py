"""交互式审核模块"""

import sys
from typing import Optional
from .database.repository import QuestionRepository, KnowledgePointRepository


def start_review(repos: dict, kp_filter: str = None, limit: int = 50):
    """启动交互式审核"""
    q_repo: QuestionRepository = repos["question"]
    kp_repo: KnowledgePointRepository = repos["kp"]

    # 获取待审核题目
    pending = q_repo.get_pending_review(limit=limit)

    if not pending:
        print("没有待审核的题目！")
        return

    print(f"共 {len(pending)} 道题目待审核")
    print("=" * 60)
    print("操作说明: [c]确认通过  [e]编辑  [s]跳过  [q]退出")
    print("=" * 60)

    approved = 0
    skipped = 0
    edited = 0

    for i, q in enumerate(pending, 1):
        # 获取知识点名称
        kp = kp_repo.get_by_id(q.knowledge_point_id)
        kp_name = kp.name if kp else "未知"

        print(f"\n[{i}/{len(pending)}] 题目ID: {q.id}")
        print(f"  知识点: {kp_name}")
        print(f"  题型: {q.question_type}")
        print(f"  题目: {q.stem[:80]}")
        print(f"  答案: {q.answer}")
        if q.solution:
            print(f"  解析: {q.solution[:60]}")
        if q.common_error:
            print(f"  易错点: {q.common_error[:60]}")

        while True:
            choice = input("\n  操作 [c/e/s/q]: ").strip().lower()

            if choice == 'c':
                q_repo.update(q.id, review_status="approved")
                print("  ✓ 已通过")
                approved += 1
                break
            elif choice == 'e':
                # 编辑模式
                print("  要修改的字段: [1]答案 [2]解析 [3]易错点 [4]知识点")
                field = input("  选择: ").strip()
                if field == '1':
                    new_val = input("  新答案: ").strip()
                    q_repo.update(q.id, answer=new_val)
                elif field == '2':
                    new_val = input("  新解析: ").strip()
                    q_repo.update(q.id, solution=new_val)
                elif field == '3':
                    new_val = input("  新易错点: ").strip()
                    q_repo.update(q.id, common_error=new_val)
                elif field == '4':
                    print("  暂不支持修改知识点")
                    continue
                q_repo.update(q.id, review_status="approved")
                print("  ✓ 已修改并通过")
                edited += 1
                break
            elif choice == 's':
                print("  → 已跳过")
                skipped += 1
                break
            elif choice == 'q':
                print(f"\n审核结束: 通过 {approved}, 修改 {edited}, 跳过 {skipped}")
                return
            else:
                print("  无效输入，请重新选择")

    print(f"\n审核完成: 通过 {approved}, 修改 {edited}, 跳过 {skipped}")
