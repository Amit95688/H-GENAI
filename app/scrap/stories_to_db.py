"""
Fetch top & best stories from Hacker News and save them into local SQLite
using the SQLAlchemy models defined in app.database.database.
"""

from sqlalchemy.orm import Session

from app.database.database import (
    engine,
    TopStories,
    BestStories,
    SummariesTopStories,
    SummariesBestStories,
)
from app.scrap.scrap import get_top_stories, get_best_stories
from app.agents.summarize_stories import summarize_text


def save_top_stories(stories: list[dict]):
    """Save or update top stories in the database."""
    with Session(engine) as session:
        for story in stories:
            story_id = story.get("id")
            if not story_id:
                continue

            existing = session.get(TopStories, story_id)
            if existing:
                existing.title = story.get("title")
                existing.author = story.get("author")
                existing.score = story.get("score")
                existing.url = story.get("url")
            else:
                new_story = TopStories(
                    id=story_id,
                    title=story.get("title"),
                    author=story.get("author"),
                    score=story.get("score"),
                    url=story.get("url"),
                )
                session.add(new_story)
        session.commit()


def save_best_stories(stories: list[dict]):
    """Save or update best stories in the database."""
    with Session(engine) as session:
        for story in stories:
            story_id = story.get("id")
            if not story_id:
                continue

            existing = session.get(BestStories, story_id)
            if existing:
                existing.title = story.get("title")
                existing.author = story.get("author")
                existing.score = story.get("score")
                existing.url = story.get("url")
            else:
                new_story = BestStories(
                    id=story_id,
                    title=story.get("title"),
                    author=story.get("author"),
                    score=story.get("score"),
                    url=story.get("url"),
                )
                session.add(new_story)
        session.commit()

def refresh_db_with_top_and_best():
    """Keep only top 5 + best 5 in DB (replace previous rows)."""
    top = get_top_stories(limit=5)
    best = get_best_stories(limit=5)

    with Session(engine) as session:
        # Clear existing rows so we only ever have 5 of each
        session.query(TopStories).delete()
        session.query(BestStories).delete()

        # Insert new top 5 and generate summaries stored in `summaries` table
        for s in top:
            sid = s.get("id")
            url = s.get("url")
            story = TopStories(
                id=sid,
                title=s.get("title"),
                author=s.get("author"),
                score=s.get("score"),
                url=url,
            )
            session.add(story)

            # create summary record keyed by story id (top stories table)
            summary_text = summarize_text(url or "", s.get("title")) if url else (s.get("title") or "[no url]")
            summary_row = SummariesTopStories(id=sid, url=url or "", summary=summary_text)
            session.merge(summary_row)

        # Insert new best 5 and generate summaries stored in `summaries` table
        for s in best:
            sid = s.get("id")
            url = s.get("url")
            story = BestStories(
                id=sid,
                title=s.get("title"),
                author=s.get("author"),
                score=s.get("score"),
                url=url,
            )
            session.add(story)

            summary_text = summarize_text(url or "", s.get("title")) if url else (s.get("title") or "[no url]")
            summary_row = SummariesBestStories(id=sid, url=url or "", summary=summary_text)
            session.merge(summary_row)

        session.commit()


def main():
    """Entry point: refresh DB and summarize."""
    refresh_db_with_top_and_best()
    print("✅ Top 5 + Best 5 stories saved and summarized in DB (hn_stories.db).")


if __name__ == "__main__":
    main()