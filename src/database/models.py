"""SQLAlchemy ORM 模型定义"""

from datetime import datetime
from sqlalchemy import create_engine, String, Integer, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List


class Base(DeclarativeBase):
    pass


class KnowledgePoint(Base):
    """知识点表"""
    __tablename__ = "knowledge_points"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[str] = mapped_column(String(20), nullable=False)
    semester: Mapped[str] = mapped_column(String(10), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(100))
    parent_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("knowledge_points.id"))
    question_types: Mapped[Optional[list]] = mapped_column(JSON)
    difficulty_range: Mapped[Optional[list]] = mapped_column(JSON)

    questions: Mapped[List["Question"]] = relationship(back_populates="knowledge_point")

    def __repr__(self):
        return f"<KnowledgePoint({self.id}: {self.name})>"


class Question(Base):
    """题目表"""
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    knowledge_point_id: Mapped[str] = mapped_column(String(20), ForeignKey("knowledge_points.id"), nullable=False)
    question_type: Mapped[str] = mapped_column(String(30), nullable=False)
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[Optional[str]] = mapped_column(Text)
    solution: Mapped[Optional[str]] = mapped_column(Text)
    common_error: Mapped[Optional[str]] = mapped_column(Text)
    # ---- 结构化易错模式字段（见 error_patterns.py / error-pattern-and-answer-suggestions.md） ----
    error_category: Mapped[Optional[str]] = mapped_column(String(30))
    error_category_label: Mapped[Optional[str]] = mapped_column(String(50))
    pattern_id: Mapped[Optional[str]] = mapped_column(String(50))
    pattern_name: Mapped[Optional[str]] = mapped_column(String(100))
    pattern_level: Mapped[Optional[str]] = mapped_column(String(30))
    theme: Mapped[Optional[str]] = mapped_column(String(30))
    theme_label: Mapped[Optional[str]] = mapped_column(String(50))
    wrong_rule: Mapped[Optional[str]] = mapped_column(Text)
    correct_rule: Mapped[Optional[str]] = mapped_column(Text)
    wrong_value: Mapped[Optional[str]] = mapped_column(String(100))
    error_step: Mapped[Optional[str]] = mapped_column(Text)
    steps: Mapped[Optional[str]] = mapped_column(Text)
    wrong_path: Mapped[Optional[str]] = mapped_column(Text)
    socratic_hints: Mapped[Optional[str]] = mapped_column(Text)
    distractor_mapping: Mapped[Optional[str]] = mapped_column(Text)
    solution_status: Mapped[Optional[str]] = mapped_column(String(30))
    enhanced_explanation: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    source: Mapped[Optional[str]] = mapped_column(String(200))
    image_path: Mapped[Optional[str]] = mapped_column(String(300))
    image_required: Mapped[bool] = mapped_column(Boolean, default=False)
    review_status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    knowledge_point: Mapped["KnowledgePoint"] = relationship(back_populates="questions")
    error_entries: Mapped[List["ErrorSet"]] = relationship(back_populates="question")

    def __repr__(self):
        return f"<Question({self.id}: {self.question_type})>"


class Paper(Base):
    """练习卷表"""
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    parameters: Mapped[Optional[dict]] = mapped_column(JSON)
    question_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    pdf_path: Mapped[Optional[str]] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Paper({self.id}: {self.title})>"


class ErrorSet(Base):
    """错题集表"""
    __tablename__ = "error_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), nullable=False)
    source_image: Mapped[Optional[str]] = mapped_column(String(300))
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    last_reviewed: Mapped[Optional[datetime]] = mapped_column(DateTime)

    question: Mapped["Question"] = relationship(back_populates="error_entries")

    def __repr__(self):
        return f"<ErrorSet({self.id}: question={self.question_id})>"


class ProcessingLog(Base):
    """处理日志表"""
    __tablename__ = "processing_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    questions_extracted: Mapped[int] = mapped_column(Integer, default=0)
    questions_imported: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<ProcessingLog({self.id}: {self.file_name} - {self.status})>"
