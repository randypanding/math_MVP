"""DOC 文档读取器 - 提取文本和图片"""

import os
import sys
from typing import Optional


def extract_from_doc(doc_path: str) -> dict:
    """从 .doc 文件提取文本和图片"""
    if not os.path.exists(doc_path):
        raise FileNotFoundError(f"文件不存在: {doc_path}")

    if not doc_path.endswith('.doc'):
        raise ValueError("只支持 .doc 格式文件")

    result = {
        "file": doc_path,
        "text": "",
        "images": [],
        "question_count": 0,
        "output_path": "",
    }

    try:
        # 提取文本
        text = _extract_text(doc_path)
        result["text"] = text

        # 提取图片
        images = _extract_images(doc_path)
        result["images"] = images

        # 保存处理结果
        basename = os.path.splitext(os.path.basename(doc_path))[0]
        output_dir = "data/processed"
        os.makedirs(output_dir, exist_ok=True)

        # 保存文本
        text_path = os.path.join(output_dir, f"{basename}.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        result["output_path"] = text_path

        # 调用 LLM 解析（如果配置了 API Key）
        from ..config import config
        if config.llm_api_key:
            from .llm_parser import parse_questions
            questions = parse_questions(text, config)
            result["question_count"] = len(questions)

            # 保存 JSON
            import json
            json_path = os.path.join(output_dir, f"{basename}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
            result["output_path"] = json_path

    except Exception as e:
        result["error"] = str(e)

    return result


def _extract_text(doc_path: str) -> str:
    """提取文本（通过 win32com）"""
    try:
        import win32com.client
    except ImportError:
        return "错误: win32com 不可用（需要 Windows + pywin32）"

    word = None
    doc = None
    try:
        word = win32com.client.Dispatch('Word.Application')
        word.Visible = False

        doc = word.Documents.Open(os.path.abspath(doc_path))
        text = doc.Content.Text

        # 清理文本
        text = text.replace('\r', '\n')
        # 去除多余空行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)

        return text
    finally:
        if doc:
            doc.Close()
        if word:
            word.Quit()


def _extract_images(doc_path: str) -> list:
    """提取图片（通过 doc→docx 转换）"""
    try:
        import win32com.client
        import pythoncom
    except ImportError:
        return []

    images = []
    word = None
    doc = None
    docx_path = None

    try:
        pythoncom.CoInitialize()
        word = win32com.client.Dispatch('Word.Application')
        word.Visible = False

        doc = word.Documents.Open(os.path.abspath(doc_path))

        # 转换为 .docx
        basename = os.path.splitext(os.path.basename(doc_path))[0]
        docx_path = os.path.abspath(f"data/images/{basename}_temp.docx")

        os.makedirs("data/images", exist_ok=True)
        # FileFormat=16 = wdFormatDocumentDefault
        doc.SaveAs2(docx_path, FileFormat=16)

        # 使用 python-docx 提取图片
        from docx import Document
        from docx.opc.constants import RELATIONSHIP_TYPE as RT

        docx_doc = Document(docx_path)
        image_dir = f"data/images/{basename}"
        os.makedirs(image_dir, exist_ok=True)

        image_count = 0
        for rel in docx_doc.part.rels.values():
            if "image" in rel.reltype:
                image_count += 1
                image_data = rel.target_part.blob
                image_ext = rel.target_ref.split('.')[-1]
                image_path = os.path.join(image_dir, f"image_{image_count}.{image_ext}")
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                images.append(image_path)

        # 清理临时文件
        if os.path.exists(docx_path):
            os.remove(docx_path)

        return images
    except Exception as e:
        return [f"图片提取错误: {e}"]
    finally:
        if doc:
            doc.Close()
        if word:
            word.Quit()
        pythoncom.CoUninitialize()
