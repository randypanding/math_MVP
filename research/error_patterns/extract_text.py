#!/usr/bin/env python3
"""从已下载的 PDF 抽取纯文本，并做相关性过滤（剔除与数学教育无关的论文）"""
import os
import json
import re
import pymupdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.join(BASE_DIR, "papers")
TEXT_DIR = os.path.join(BASE_DIR, "text")
MANIFEST_PATH = os.path.join(BASE_DIR, "manifest.json")

# 相关性关键词（命中任一即视为相关）
RELEVANCE_KEYWORDS = [
    "misconception", "misconceptions", "error analysis", "common error", "common errors",
    "error pattern", "errors", "mistake", "mistakes", "wrong answer", "incorrect",
    "learning difficulty", "difficulti", "number sense", "arithmetic", "fraction",
    "decimal", "proportion", "ratio", "word problem", "story problem", "computation",
    "place value", "multiplication", "division", "addition", "subtraction", "geometry",
    "algebra", "mathematics education", "math education", "mathematical", "students",
    "children", "elementary", "primary", "pedagog", "teaching", "assessment",
    "distractor", "intelligent tutoring", "cognitive", "conceptual knowledge",
    "procedural knowledge", "math achievement", "item response", "diagnostic",
    "learning", "misunderstand", "achievement", "tutor", "self-explanation",
]

def is_relevant(text):
    t = text.lower()
    return any(k in t for k in RELEVANCE_KEYWORDS)

def extract_text(pdf_path):
    try:
        doc = pymupdf.open(pdf_path)
        parts = []
        for page in doc:
            parts.append(page.get_text())
        doc.close()
        return "\n".join(parts)
    except Exception as e:
        return f"__EXTRACT_ERROR__: {e}"

def main():
    os.makedirs(TEXT_DIR, exist_ok=True)
    if not os.path.exists(MANIFEST_PATH):
        print("manifest 不存在")
        return

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    ok = 0
    kept = 0
    dropped = 0
    for rec in manifest:
        pdf_path = rec.get("pdf_path", "")
        if not os.path.exists(pdf_path):
            continue
        ok += 1
        text = extract_text(pdf_path)
        if text.startswith("__EXTRACT_ERROR__"):
            rec["text_ok"] = False
            rec["relevant"] = False
            continue
        rec["text_ok"] = True
        relevant = is_relevant(text)
        rec["relevant"] = relevant
        if relevant:
            kept += 1
            base = os.path.splitext(os.path.basename(pdf_path))[0]
            txt_path = os.path.join(TEXT_DIR, base + ".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
            rec["text_path"] = txt_path
        else:
            dropped += 1

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"PDF 存在: {ok}, 相关保留: {kept}, 不相关剔除: {dropped}")

if __name__ == "__main__":
    main()