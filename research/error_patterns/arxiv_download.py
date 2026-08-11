#!/usr/bin/env python3
"""arXiv 论文检索+相关性打分+限量全文下载
1) 拉取全部候选的标题/作者/摘要（快）
2) 按相关性打分并保存 manifest（含全部候选）
3) 只为得分最高的 TOP_N 篇下载全文 PDF
"""
import os
import json
import time
import urllib.parse
import urllib.request
import feedparser
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.join(BASE_DIR, "papers")
MANIFEST_PATH = os.path.join(BASE_DIR, "manifest.json")
ARXIV_API = "https://export.arxiv.org/api/query"
TOP_N = 120  # 下载全文的论文数上限

# 标题/摘要关键词 → 权重（标题命中权重更高）
KEYWORDS = {
    "misconception": 3, "misconceptions": 3, "error analysis": 3, "common error": 3,
    "error pattern": 3, "mistake": 3, "mistakes": 3, "incorrect": 2, "wrong answer": 3,
    "errors": 2, "learning difficulty": 3, "difficulty": 1, "number sense": 3,
    "arithmetic": 2, "fraction": 3, "decimal": 3, "proportion": 2, "ratio": 2,
    "word problem": 3, "story problem": 3, "computation": 2, "place value": 3,
    "multiplication": 2, "division": 2, "addition": 2, "subtraction": 2,
    "geometry": 1, "algebra": 1, "mathematics education": 3, "math education": 3,
    "elementary math": 3, "primary school math": 3, "math achievement": 2,
    "math performance": 2, "distractor": 3, "intelligent tutoring": 2,
    "conceptual knowledge": 3, "procedural knowledge": 3, "diagnostic": 2,
    "self-explanation": 3, "worked example": 3, "feedback": 2, "math anxiety": 2,
    "math fact": 2, "transfer": 1, "mathematical thinking": 2, "students": 1,
    "children": 1, "elementary": 2, "primary": 2, "learning": 1, "teaching": 1,
    "assessment": 1, "test": 1, "exam": 1, "achievement": 1, "cognitive": 1,
}

QUERIES = [
    ("mathematics misconception elementary students", "ms_math_misconception"),
    ("mathematical error analysis students", "ms_error_analysis"),
    ("arithmetic error children number understanding", "ms_arithmetic_error"),
    ("fraction misconception students", "ms_fraction"),
    ("word problem solving errors mathematics", "ms_word_problem"),
    ("decimal misconception number sense", "ms_decimal"),
    ("geometry misconception students", "ms_geometry"),
    ("algebra misconception students", "ms_algebra"),
    ("mathematics learning difficulty error analysis", "ms_ld"),
    ("intelligent tutoring system mathematics error feedback", "ms_its"),
    ("math word problem comprehension errors", "ms_wps"),
    ("procedural conceptual knowledge mathematics learning", "ms_proc_conc"),
    ("multiplication division misconception children", "ms_muldiv"),
    ("place value understanding error children", "ms_placevalue"),
    ("proportion ratio misconception students", "ms_ratio"),
    ("math anxiety achievement elementary", "ms_anxiety"),
    ("worked example self-explanation mathematics learning", "ms_worked"),
    ("automatic error detection math problem solving", "ms_auto"),
    ("number fact retrieval arithmetic learning", "ms_fact"),
    ("math learning difficulty assessment item response", "ms_irt"),
]

def fetch_arxiv(query, max_results=100):
    params = {"search_query": f"all:{query}", "start": 0, "max_results": max_results,
              "sortBy": "relevance"}
    url = ARXIV_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return feedparser.parse(resp.read().decode("utf-8")).entries

def score(title, abstract):
    t = (title + " " + abstract).lower()
    s = 0
    for kw, w in KEYWORDS.items():
        if kw in title.lower():
            s += w * 3
        elif kw in t:
            s += w
    return s

def safe_name(title, arxiv_id):
    s = re.sub(r"[^\w\s\u4e00-\u9fff-]", "", title)
    s = re.sub(r"\s+", "_", s).strip("_")
    return f"{arxiv_id.replace('/', '_')}_{s[:70]}"

def main():
    os.makedirs(PAPER_DIR, exist_ok=True)
    seen = {}
    for query, tag in QUERIES:
        print(f"=== {query} ===", flush=True)
        try:
            entries = fetch_arxiv(query)
        except Exception as e:
            print(f"  fail {e}", flush=True)
            time.sleep(3)
            continue
        for ent in entries:
            arxiv_id = ent.id.split("/abs/")[-1].split("v")[0].replace("/", "_")
            if arxiv_id in seen:
                continue
            title = ent.title.replace("\n", " ").strip()
            abstract = ent.summary.replace("\n", " ").strip()
            if score(title, abstract) < 3:  # 相关性门槛
                continue
            pdf_url = next((l.get("href") for l in ent.get("links", [])
                            if l.get("type") == "application/pdf"), ent.get("link"))
            seen[arxiv_id] = {
                "arxiv_id": arxiv_id, "title": title,
                "authors": [a.get("name", "") for a in ent.get("authors", [])],
                "published": ent.get("published", ""), "abstract": abstract,
                "query_tag": tag, "pdf_url": pdf_url,
                "pdf_path": os.path.join(PAPER_DIR, safe_name(title, arxiv_id) + ".pdf"),
                "score": score(title, abstract),
            }
        time.sleep(3)

    all_records = sorted(seen.values(), key=lambda r: -r["score"])
    print(f"候选总数: {len(all_records)}", flush=True)

    # 保存全部候选元数据
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    # 下载 TOP_N 全文
    to_download = all_records[:TOP_N]
    print(f"本轮下载全文 {len(to_download)} 篇", flush=True)
    ok = 0
    for i, rec in enumerate(to_download):
        if os.path.exists(rec["pdf_path"]) and os.path.getsize(rec["pdf_path"]) > 1000:
            ok += 1
            continue
        try:
            req = urllib.request.Request(rec["pdf_url"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as resp, open(rec["pdf_path"], "wb") as f:
                f.write(resp.read())
            if os.path.getsize(rec["pdf_path"]) > 1000:
                ok += 1
                print(f"[{i+1}/{len(to_download)}] OK {rec['arxiv_id']} score={rec['score']}", flush=True)
            else:
                os.remove(rec["pdf_path"])
                print(f"[{i+1}/{len(to_download)}] 空文件 {rec['arxiv_id']}", flush=True)
        except Exception as e:
            print(f"[{i+1}/{len(to_download)}] FAIL {rec['arxiv_id']} {e}", flush=True)
        time.sleep(1.0)

    print(f"下载完成 {ok}/{len(to_download)}", flush=True)

if __name__ == "__main__":
    main()