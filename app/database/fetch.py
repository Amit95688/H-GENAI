from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import engine, SummariesTopStories, SummariesBestStories


def fetch_one_summary(table: str = "top") -> tuple[int, str, str] | None:
	model = SummariesTopStories if table == "top" else SummariesBestStories

	with Session(engine) as session:
		stmt = select(model.id, model.url, model.summary).limit(1)
		return session.execute(stmt).first()


if __name__ == "__main__":
	row = fetch_one_summary("top")
	if row is None:
		print("No summaries found.")
	else:
		print(row)
