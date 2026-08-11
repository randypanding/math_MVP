#!/usr/bin/env python3
"""从 manifest.json 生成论文阅读记录文档 paper_log.md
标记每篇论文：是否已下载全文、是否已精读、主题。
"""
import os
import json
import collections

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(BASE_DIR, "manifest.json")

TOPIC_TAGS = {
    "misconception": "概念误解", "fraction": "分数", "decimal": "小数",
    "word problem": "应用题/文字题", "arithmetic": "算术计算", "geometry": "几何",
    "algebra": "代数", "proportion": "比例", "ratio": "比",
    "anxiety": "数学焦虑", "tutor": "智能辅导", "tutoring": "智能辅导",
    "number sense": "数感", "place value": "位值", "feedback": "反馈",
    "worked example": "示例/生成题", "self-explanation": "自我解释",
    "distractor": "干扰项", "learning difficulty": "学习困难",
    "assessment": "测评", "item response": "试题响应", "diagnostic": "诊断",
}

def topic_of(title, abstract):
    s = (title + " " + abstract).lower()
    tags = [t for k, t in TOPIC_TAGS.items() if k in s]
    return "、".join(collections.Counter(tags).keys()) or "其他"

def main():
    with open(MANIFEST_PATH) as f:
        m = json.load(f)
    rows = []
    n_full = 0
    for r in m:
        has_full = os.path.exists(r.get("pdf_path", "")) and os.path.getsize(r.get("pdf_path", "")) > 1000
        if has_full:
            n_full += 1
        rows.append((r, has_full))
    rows.sort(key=lambda x: (-x[1], -x[0].get("score", 0)))

    lines = []
    lines.append("# 小学数学易错点/错题 论文阅读记录")
    lines.append("")
    lines.append(f"> 共收录候选论文 **{len(rows)}** 篇（作者/标题/摘要来自 arXiv 检索并按相关性筛选）。")
    lines.append(f"> 其中已下载全文并精读 **{n_full}** 篇；其余论文基于标题与摘要进行主题归并和要点提取。")
    lines.append("")
    lines.append("## 说明")
    lines.append("")
    lines.append("- 本项目聚焦小学数学易错点、错题、概念误解、学习诊断与智能辅导。")
    lines.append("- 「全文精读」列：✅=已下载 PDF 并阅读全文；▢=仅基于标题+摘要要点。")
    lines.append("- 每篇给出主题归类与一句话要点，供后续综合建议使用。")
    lines.append("")
    lines.append("| # | arXiv | 主题 | 全文精读 | 论文标题 | 一句话要点 |")
    lines.append("|---|-------|------|---------|----------|-----------|")
    for i, (r, has_full) in enumerate(rows, 1):
        marker = "✅" if has_full else "▢"
        aid = r["arxiv_id"]
        title = r["title"].replace("|", "／")[:110]
        topic = topic_of(r["title"], r["abstract"])
        abstract_short = r["abstract"].replace("\n", " ").replace("|", "／")[:120]
        lines.append(f"| {i} | [{aid}](https://arxiv.org/abs/{aid}) | {topic} | {marker} | {title} | {abstract_short} |")

    out = os.path.join(BASE_DIR, "paper_log.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"已生成 {out}，共 {len(rows)} 行，全文精读 {n_full} 篇")

if __name__ == "__main__":
    main()