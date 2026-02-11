from sqlalchemy import create_engine, String, Integer, Column
from sqlalchemy.ext.declarative import declarative_base

# Simple local SQLite DB instead of PostgreSQL (no server needed)
engine = create_engine("sqlite:///hn_stories.db", echo=False)

# Classic SQLAlchemy Base (works with older SQLAlchemy versions)
Base = declarative_base()


class TopStories(Base):
    __tablename__ = "top_stories"

    id = Column(Integer, primary_key=True)
    title = Column(String(300))
    author = Column(String(100))
    score = Column(Integer)
    url = Column(String(500))


class BestStories(Base):
    __tablename__ = "best_stories"

    id = Column(Integer, primary_key=True)
    title = Column(String(300))
    author = Column(String(100))
    score = Column(Integer)
    url = Column(String(500))


# Create all tables if they don't exist
Base.metadata.create_all(engine)
