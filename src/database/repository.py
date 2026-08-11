"""数据库仓库层 - CRUD 操作"""

import os
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base, KnowledgePoint, Question, Paper, ErrorSet, ProcessingLog


class Database:
    """数据库连接管理"""

    def __init__(self, db_path: str = "data/mathgen.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()


class Repository:
    """通用仓库基类"""

    def __init__(self, db: Database):
        self.db = db

    def get_session(self) -> Session:
        return self.db.get_session()


class KnowledgePointRepository(Repository):
    """知识点仓库"""

    def create(self, **kwargs) -> KnowledgePoint:
        session = self.get_session()
        try:
            kp = KnowledgePoint(**kwargs)
            session.add(kp)
            session.commit()
            session.refresh(kp)
            return kp
        finally:
            session.close()

    def get_by_id(self, kp_id: str) -> Optional[KnowledgePoint]:
        session = self.get_session()
        try:
            return session.query(KnowledgePoint).filter_by(id=kp_id).first()
        finally:
            session.close()

    def get_all(self) -> List[KnowledgePoint]:
        session = self.get_session()
        try:
            return session.query(KnowledgePoint).all()
        finally:
            session.close()

    def get_by_grade(self, grade: str) -> List[KnowledgePoint]:
        session = self.get_session()
        try:
            return session.query(KnowledgePoint).filter_by(grade=grade).all()
        finally:
            session.close()

    def search_by_name(self, name: str) -> List[KnowledgePoint]:
        session = self.get_session()
        try:
            return session.query(KnowledgePoint).filter(KnowledgePoint.name.like(f"%{name}%")).all()
        finally:
            session.close()

    def count(self) -> int:
        session = self.get_session()
        try:
            return session.query(KnowledgePoint).count()
        finally:
            session.close()


class QuestionRepository(Repository):
    """题目仓库"""

    def create(self, **kwargs) -> Question:
        session = self.get_session()
        try:
            q = Question(**kwargs)
            session.add(q)
            session.commit()
            session.refresh(q)
            return q
        finally:
            session.close()

    def create_batch(self, questions: list) -> int:
        session = self.get_session()
        try:
            for q_data in questions:
                q = Question(**q_data)
                session.add(q)
            session.commit()
            return len(questions)
        finally:
            session.close()

    def get_by_id(self, q_id: int) -> Optional[Question]:
        session = self.get_session()
        try:
            return session.query(Question).filter_by(id=q_id).first()
        finally:
            session.close()

    def query(self, knowledge_point_id: str = None, grade: str = None,
              question_type: str = None, difficulty: int = None,
              review_status: str = None, limit: int = 50, offset: int = 0) -> List[Question]:
        session = self.get_session()
        try:
            query = session.query(Question)
            # 如果需要按年级筛选且有知识点数据，则 JOIN
            if grade:
                # 先查找该年级的所有知识点ID
                kp_ids = [kp.id for kp in session.query(KnowledgePoint).filter_by(grade=grade).all()]
                if kp_ids:
                    query = query.filter(Question.knowledge_point_id.in_(kp_ids))
            if knowledge_point_id:
                query = query.filter(Question.knowledge_point_id == knowledge_point_id)
            if question_type:
                query = query.filter(Question.question_type == question_type)
            if difficulty:
                query = query.filter(Question.difficulty == difficulty)
            if review_status:
                query = query.filter(Question.review_status == review_status)
            return query.offset(offset).limit(limit).all()
        finally:
            session.close()

    def count(self, knowledge_point_id: str = None, review_status: str = None) -> int:
        session = self.get_session()
        try:
            query = session.query(Question)
            if knowledge_point_id:
                query = query.filter(Question.knowledge_point_id == knowledge_point_id)
            if review_status:
                query = query.filter(Question.review_status == review_status)
            return query.count()
        finally:
            session.close()

    def update(self, q_id: int, **kwargs) -> Optional[Question]:
        session = self.get_session()
        try:
            q = session.query(Question).filter_by(id=q_id).first()
            if q:
                for key, value in kwargs.items():
                    setattr(q, key, value)
                session.commit()
                session.refresh(q)
            return q
        finally:
            session.close()

    def get_pending_review(self, limit: int = 50) -> List[Question]:
        session = self.get_session()
        try:
            return session.query(Question).filter_by(review_status="pending").limit(limit).all()
        finally:
            session.close()


class PaperRepository(Repository):
    """练习卷仓库"""

    def create(self, **kwargs) -> Paper:
        session = self.get_session()
        try:
            p = Paper(**kwargs)
            session.add(p)
            session.commit()
            session.refresh(p)
            return p
        finally:
            session.close()

    def get_by_id(self, p_id: int) -> Optional[Paper]:
        session = self.get_session()
        try:
            return session.query(Paper).filter_by(id=p_id).first()
        finally:
            session.close()

    def get_all(self) -> List[Paper]:
        session = self.get_session()
        try:
            return session.query(Paper).order_by(Paper.created_at.desc()).all()
        finally:
            session.close()


class ErrorSetRepository(Repository):
    """错题集仓库"""

    def create(self, **kwargs) -> ErrorSet:
        session = self.get_session()
        try:
            e = ErrorSet(**kwargs)
            session.add(e)
            session.commit()
            session.refresh(e)
            return e
        finally:
            session.close()

    def get_all(self) -> List[ErrorSet]:
        session = self.get_session()
        try:
            return session.query(ErrorSet).all()
        finally:
            session.close()

    def get_question_ids(self) -> List[int]:
        session = self.get_session()
        try:
            results = session.query(ErrorSet.question_id).all()
            return [r[0] for r in results]
        finally:
            session.close()

    def increment_review(self, error_id: int):
        session = self.get_session()
        try:
            e = session.query(ErrorSet).filter_by(id=error_id).first()
            if e:
                e.review_count += 1
                e.last_reviewed = datetime.now()
                session.commit()
        finally:
            session.close()


class ProcessingLogRepository(Repository):
    """处理日志仓库"""

    def create(self, **kwargs) -> ProcessingLog:
        session = self.get_session()
        try:
            log = ProcessingLog(**kwargs)
            session.add(log)
            session.commit()
            session.refresh(log)
            return log
        finally:
            session.close()

    def get_all(self) -> List[ProcessingLog]:
        session = self.get_session()
        try:
            return session.query(ProcessingLog).order_by(ProcessingLog.created_at.desc()).all()
        finally:
            session.close()

    def get_stats(self) -> dict:
        session = self.get_session()
        try:
            total = session.query(ProcessingLog).count()
            success = session.query(ProcessingLog).filter_by(status="success").count()
            failed = session.query(ProcessingLog).filter_by(status="failed").count()
            partial = session.query(ProcessingLog).filter_by(status="partial").count()
            total_extracted = session.query(ProcessingLog).with_entities(
                ProcessingLog.questions_extracted).all()
            return {
                "total_files": total,
                "success": success,
                "failed": failed,
                "partial": partial,
                "total_questions_extracted": sum(t[0] for t in total_extracted) if total_extracted else 0
            }
        finally:
            session.close()
