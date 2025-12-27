from sqlmodel import create_engine, Session, SQLModel
import os

# 실제 환경에서는 환경 변수(os.getenv)로 관리하는 것이 좋습니다.
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://user:password@localhost:5432/security_curator"
)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

def init_db():
    """테이블이 없으면 생성하는 함수"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """세션을 안전하게 가져오기 위한 Generator"""
    with Session(engine) as session:
        yield session