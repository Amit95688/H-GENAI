from sqlalchemy import create_engine, String, Integer, Text, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# SQLite database for local storage
engine = create_engine(
    "sqlite:///hn_stories.db",
    echo=False,
    connect_args={"timeout": 30},
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, _connection_record) -> None:
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
    finally:
        cursor.close()

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
    


class SummariesTopStories(Base):
    __tablename__ = "summaries_top"

    # Use the Hacker News story `id` as the primary key for top-story summaries
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str] = mapped_column(Text())


class SummariesBestStories(Base):
    __tablename__ = "summaries_best"

    # Use the Hacker News story `id` as the primary key for best-story summaries
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str] = mapped_column(Text())


# Create tables if they don't exist
Base.metadata.create_all(engine)
