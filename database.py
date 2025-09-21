from sqlalchemy import Column, Integer, String, Float, DateTime, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./resume_logs.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class ResumeLog(Base):
    __tablename__ = "resume_logs"

    id = Column(Integer, primary_key=True, index=True)
    resume_name = Column(String, nullable=False)
    hard_score = Column(Float, nullable=False)
    semantic_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
    verdict = Column(String, nullable=False)
    missing_keywords = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

Base.metadata.create_all(bind=engine)
