"""PDF 渲染器 - 仿照示例卷子排版"""

import os
import re
import math
import logging
from datetime import datetime
from fpdf import FPDF

# 抑制 fontTools 子集化对 TTC 字体的无害警告（不影响渲染结果）
logging.getLogger("fontTools.subset").setLevel(logging.ERROR)


class PDFRenderer:
    """PDF 渲染器 - 仿照标准每日一练卷子排版"""

    def __init__(self):
        self.font_path = self._find_chinese_font()

    def _find_chinese_font(self) -> str:
        # 常见系统字体路径（Windows + Linux），优先取可用的
        font_dirs = ["C:/Windows/Fonts", "C:/WINNT/Fonts",
                     "/usr/share/fonts/truetype/noto",
                     "/usr/share/fonts/opentype/noto",
                     "/usr/share/fonts/truetype/wqy",
                     "/System/Library/Fonts"]
        chinese_fonts = ["simsun.ttc", "msyh.ttc", "simhei.ttf", "simkai.ttf",
                         "NotoSansCJK-Regular.ttc", "NotoSansCJK-Regular.ttf",
                         "wqy-zenhei.ttc", "wqy-microhei.ttc",
                         "PingFang.ttc", "STHeiti Light.ttc"]
        for font_dir in font_dirs:
            for font_name in chinese_fonts:
                font_path = os.path.join(font_dir, font_name)
                if os.path.exists(font_path):
                    return font_path
        return ""

    @staticmethod
    def _clean_text(s: str) -> str:
        """渲染前清理文本：展开下划线占位符、去除会被字体子集报缺词形的控制字符。

        综合算式等题干内嵌字面换行符（\\n），SimSun 子集不含 \\n 字形，直接传给
        fpdf2 会触发 "missing the following glyphs: ' ' (\\n)" 警告。统一替换为空格。
        """
        return str(s).replace("&#95;&#95;", "______").replace("\n", " ")

    def render_paper(self, title: str, sections: list, grade: str = None,
                     knowledge_points: str = "", with_answer: bool = True,
                     with_error_tip: bool = False, output_path: str = "output.pdf") -> str:
        """渲染练习卷PDF"""

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)

        if self.font_path:
            pdf.add_font("Chinese", "", self.font_path, uni=True)
            pdf.add_font("Chinese", "B", self.font_path, uni=True)
            font_name = "Chinese"
        else:
            font_name = "Helvetica"

        # ===== 试卷页 =====
        pdf.add_page()

        # 标题
        pdf.set_font(font_name, "B", 14)
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(2)

        # 信息栏
        pdf.set_font(font_name, "", 9)
        info_y = pdf.get_y()
        pdf.cell(38, 7, "学校：_________________", ln=False)
        pdf.cell(38, 7, "班级：_________________", ln=False)
        pdf.cell(38, 7, "姓名：_________________", ln=False)
        pdf.cell(38, 7, "日期：_________________", ln=False)
        pdf.cell(38, 7, "用时：_________________", ln=True)
        pdf.ln(2)

        # 分隔线
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.4)
        pdf.line(12, pdf.get_y(), 198, pdf.get_y())
        pdf.ln(4)

        # 题目内容
        for section in sections:
            if pdf.get_y() > 255:
                pdf.add_page()

            # 题型标题
            pdf.set_font(font_name, "B", 11)
            pdf.cell(0, 8, section["title"], ln=True)
            pdf.ln(1)

            q_type = section["type"]
            questions = section["questions"]

            if q_type == "mental_arithmetic":
                self._render_mental_arithmetic(pdf, font_name, questions)
            elif q_type == "vertical_calculation":
                self._render_vertical_calculation(pdf, font_name, questions)
            elif q_type == "step_calculation":
                self._render_step_calculation(pdf, font_name, questions)
            elif q_type == "fill_unknown":
                self._render_fill_unknown(pdf, font_name, questions)
            elif q_type == "compare_size":
                self._render_compare_size(pdf, font_name, questions)
            elif q_type == "word_problem":
                self._render_word_problem(pdf, font_name, questions)
            else:
                self._render_default(pdf, font_name, questions)

            pdf.ln(3)

        # ===== 答案页 =====
        if with_answer:
            self._render_answer_page(pdf, font_name, sections, title, with_error_tip)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        return output_path

    def _render_mental_arithmetic(self, pdf, font_name, questions):
        """口算题：每行3题，紧凑排列"""
        pdf.set_font(font_name, "", 10)
        for i, q in enumerate(questions):
            stem = self._clean_text(q.stem)
            text = f"  {q.number}. {stem}"
            pdf.cell(60, 6, text, ln=False)
            if (i + 1) % 3 == 0:
                pdf.ln(6)
        if len(questions) % 3 != 0:
            pdf.ln(6)

    def _render_vertical_calculation(self, pdf, font_name, questions):
        """竖式计算：每行2题，留空位"""
        pdf.set_font(font_name, "", 10)
        for i, q in enumerate(questions):
            stem = self._clean_text(q.stem)
            text = f"  {q.number}. {stem}"
            pdf.cell(80, 6, text, ln=False)
            pdf.ln(4)
            pdf.ln(10)
            if (i + 1) % 2 == 0:
                pdf.ln(2)
        if len(questions) % 2 != 0:
            pdf.ln(2)

    def _render_step_calculation(self, pdf, font_name, questions):
        """脱式计算：每行2题，留空位"""
        pdf.set_font(font_name, "", 10)
        for i, q in enumerate(questions):
            stem = self._clean_text(q.stem)
            text = f"  {q.number}. {stem}"
            pdf.cell(80, 6, text, ln=False)
            pdf.ln(4)
            pdf.ln(8)
            if (i + 1) % 2 == 0:
                pdf.ln(2)
        if len(questions) % 2 != 0:
            pdf.ln(2)

    def _render_fill_unknown(self, pdf, font_name, questions):
        """填未知数：每行3题"""
        pdf.set_font(font_name, "", 10)
        for i, q in enumerate(questions):
            stem = self._clean_text(q.stem)
            text = f"  {q.number}. {stem}"
            pdf.cell(60, 6, text, ln=False)
            if (i + 1) % 3 == 0:
                pdf.ln(6)
        if len(questions) % 3 != 0:
            pdf.ln(6)

    def _render_compare_size(self, pdf, font_name, questions):
        """比大小：每行3题"""
        pdf.set_font(font_name, "", 10)
        if questions:
            # 提取题干里统一印出的指令（如“在○里填上…），题区开头只打印一次，
            # 避免每题重复拼接指令、且 3 题之间无分隔。
            m = re.match(r"^(在○里填上.*?[：:])", questions[0].stem)
            if m:
                pdf.cell(0, 6, self._clean_text(m.group(1)), ln=True)
                pdf.ln(1)
        for i, q in enumerate(questions):
            stem = re.sub(r"^在○里填上.*?[：:]", "", self._clean_text(q.stem))
            text = f"  {q.number}. {stem}"
            pdf.cell(60, 6, text, ln=False)
            if (i + 1) % 3 == 0:
                pdf.ln(6)
        if len(questions) % 3 != 0:
            pdf.ln(6)

    def _render_word_problem(self, pdf, font_name, questions):
        """解决问题：每行1题，留大空位"""
        pdf.set_font(font_name, "", 10)
        for q in questions:
            stem = self._clean_text(q.stem)
            pdf.multi_cell(0, 6, f"  {q.number}. {stem}")
            pdf.ln(2)
            pdf.ln(18)

    def _render_default(self, pdf, font_name, questions):
        """默认排版：每行2题"""
        pdf.set_font(font_name, "", 10)
        for i, q in enumerate(questions):
            stem = self._clean_text(q.stem)
            text = f"  {q.number}. {stem}"
            pdf.cell(80, 6, text, ln=False)
            pdf.ln(4)
            pdf.ln(8)
            if (i + 1) % 2 == 0:
                pdf.ln(2)
        if len(questions) % 2 != 0:
            pdf.ln(2)

    def _render_answer_page(self, pdf, font_name, sections, title, with_error_tip):
        """答案页"""
        pdf.add_page()
        pdf.set_font(font_name, "B", 14)
        pdf.cell(0, 10, f"{title} - 答案", ln=True, align="C")
        pdf.ln(2)
        pdf.line(12, pdf.get_y(), 198, pdf.get_y())
        pdf.ln(4)

        for section in sections:
            if pdf.get_y() > 260:
                pdf.add_page()

            pdf.set_font(font_name, "B", 10)
            pdf.cell(0, 8, section["title"], ln=True)
            pdf.ln(1)

            pdf.set_font(font_name, "", 9)
            for q in section["questions"]:
                if pdf.get_y() > 270:
                    pdf.add_page()
                    pdf.set_font(font_name, "", 9)
                answer = self._clean_text(q.answer) if q.answer else "略"
                pdf.cell(0, 5, f"  {q.number}. {answer}")
                pdf.ln(5)

                if with_error_tip and q.common_error and q.common_error.strip():
                    pdf.set_font(font_name, "", 8)
                    pdf.set_text_color(180, 0, 0)
                    pdf.cell(0, 4, f"      易错点：{self._clean_text(q.common_error)}")
                    pdf.ln(4)
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font(font_name, "", 9)
            pdf.ln(2)
