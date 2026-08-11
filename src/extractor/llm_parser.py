"""LLM 结构化解析器"""

import json
import requests
from typing import List, Dict, Optional


def parse_questions(text: str, config, batch_size: int = 20) -> List[Dict]:
    """调用 LLM 解析文本为结构化题目"""
    if not config.llm_api_key:
        return []

    # 分批处理
    lines = text.split('\n')
    batches = []
    current_batch = []
    for line in lines:
        current_batch.append(line)
        if len(current_batch) >= 50:
            batches.append('\n'.join(current_batch))
            current_batch = []
    if current_batch:
        batches.append('\n'.join(current_batch))

    all_questions = []
    for batch in batches:
        questions = _call_llm(batch, config)
        all_questions.extend(questions)

    return all_questions


def _call_llm(text: str, config) -> List[Dict]:
    """调用 LLM API"""
    headers = {
        "Authorization": f"Bearer {config.llm_api_key}",
        "Content-Type": "application/json",
    }

    prompt = _build_prompt(text)

    payload = {
        "model": config.llm_model,
        "messages": [
            {"role": "system", "content": "你是一个数学题目解析助手。请从给定的数学试卷文本中提取题目，并以JSON格式返回。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": config.llm_temperature,
        "response_format": {"type": "json_object"},
    }

    try:
        response = requests.post(
            f"{config.llm_base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=config.llm_timeout,
        )
        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"]
        data = json.loads(content)

        if isinstance(data, dict) and "questions" in data:
            return data["questions"]
        elif isinstance(data, list):
            return data
        return []
    except Exception as e:
        print(f"LLM 调用失败: {e}")
        return []


def _build_prompt(text: str) -> str:
    """构建 LLM prompt"""
    return f"""请从以下数学试卷文本中提取题目，并以JSON格式返回。

要求：
1. 每道题包含以下字段：
   - stem: 题目文本
   - answer: 答案（无法确定则为null）
   - solution: 解题步骤
   - common_error: 易错点
   - difficulty: 难度(1-5)
   - question_type: 题型（口算题/竖式计算/脱式计算/填未知数/数的组成/数的读写/比大小/规律填数/验算题/估算题/简便计算/列综合算式/解方程/百分数/图形计数/周长面积/单位换算/角的度量/统计图表/解决问题/数学广角）
   - knowledge_point: 关联知识点名称
   - image_required: 是否需要图片辅助(true/false)

2. 仅从原题提取信息，不修改数字或添加新内容
3. 若无法确定答案，标记为 null
4. 识别并标记需要图片辅助的题目

文本：
{text}

请返回JSON格式：
{{"questions": [{{
  "stem": "...",
  "answer": "...",
  "solution": "...",
  "common_error": "...",
  "difficulty": 2,
  "question_type": "...",
  "knowledge_point": "...",
  "image_required": false
}}]}}"""
