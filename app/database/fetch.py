# app/database/fetch.py
"""
Fetch top & best stories from Hacker News and save them into Postgres
using the SQLAlchemy models defined in app.database.databse.
"""

from sqlalchemy.orm import Session

from app.database.databse import engine, TopStories, BestStories
from app.scrap.scrap import get_top_stories, get_best_stories


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


def main():
    """Fetch top & best stories from Hacker News and save them."""
    top = get_top_stories()
    best = get_best_stories()

    save_top_stories(top)
    save_best_stories(best)
    print("✅ Top and Best stories saved/updated in DB!")


if __name__ == "__main__":
    main()