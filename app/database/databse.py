# app/database/database.py
from sqlalchemy import create_engine, String, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# SQLite database for local storage
engine = create_engine("sqlite:///hn_stories.db", echo=False)

# Modern SQLAlchemy Base
class Base(DeclarativeBase):
    pass


class TopStories(Base):
    __tablename__ = "top_stories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    author: Mapped[str] = mapped_column(String(100))
    score: Mapped[int] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(String(500))


class BestStories(Base):
    __tablename__ = "best_stories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    author: Mapped[str] = mapped_column(String(100))
    score: Mapped[int] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(String(500))


# Create tables if they don't exist
Base.metadata.create_all(engine)
