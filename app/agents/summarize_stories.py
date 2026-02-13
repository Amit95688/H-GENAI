from __future__ import annotations

import os
import concurrent.futures
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.llms import Ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from app.database.database import (
    engine,
    TopStories,
    BestStories,
    SummariesTopStories,
    SummariesBestStories,
)
from app.scrap.scrap import get_top_stories, get_best_stories


# ==============================
# CONFIG
# ==============================

load_dotenv()

OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "llama3.2:3b")
MAX_WORKERS = int(os.getenv("SUMMARY_WORKERS", 4))


# ==============================
# GLOBAL LLM (reuse instance)
# ==============================

llm = Ollama(
    base_url=OLLAMA_BASE,
    model=SUMMARY_MODEL,
    temperature=0.2,
)

prompt = PromptTemplate.from_template(
    "You are a concise technical summarizer.\n\n"
    "Context:\n{context}\n\n"
    "Provide:\n"
    "- 2-3 sentence summary\n"
    "- 3 bullet points\n"
)

chain = prompt | llm | StrOutputParser()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
)


# ==============================
# SUMMARIZATION
# ==============================

def summarize_url(url: Optional[str]) -> str:
    if not url:
        return "Summary unavailable"

    try:
        loader = WebBaseLoader(url)
        docs = loader.load()

        splits = splitter.split_documents(docs)

        # Limit context size (avoid huge prompts)
        context = "\n\n".join(d.page_content for d in splits[:4])

        return chain.invoke({"context": context})

    except Exception:
        return f"Summary unavailable for {url}"


# ==============================
# PARALLEL PROCESSING
# ==============================

def process_story(story: dict) -> tuple[int, str, str]:
    sid = story["id"]
    url = story.get("url")
    summary = summarize_url(url) if url else (story.get("title") or "Summary unavailable")
    return sid, url or "", summary


# ==============================
# DB REFRESH
# ==============================

def refresh_db_with_top_and_best():

    top = get_top_stories(limit=5)
    best = get_best_stories(limit=5)

    with Session(engine) as session:

        # Clear old data
        session.query(TopStories).delete()
        session.query(BestStories).delete()
        session.query(SummariesTopStories).delete()
        session.query(SummariesBestStories).delete()
        session.commit()

        # Insert stories first (fast)
        for s in top:
            session.add(
                TopStories(
                    id=s["id"],
                    title=s.get("title"),
                    author=s.get("author"),
                    score=s.get("score"),
                    url=s.get("url"),
                )
            )

        for s in best:
            session.add(
                BestStories(
                    id=s["id"],
                    title=s.get("title"),
                    author=s.get("author"),
                    score=s.get("score"),
                    url=s.get("url"),
                )
            )

        session.commit()

        # Parallel summarization
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

            # Top stories summaries
            futures_top = [executor.submit(process_story, s) for s in top]
            for future in concurrent.futures.as_completed(futures_top):
                sid, url, summary = future.result()
                session.merge(
                    SummariesTopStories(
                        id=sid,
                        url=url,
                        summary=summary,
                    )
                )

            # Best stories summaries
            futures_best = [executor.submit(process_story, s) for s in best]
            for future in concurrent.futures.as_completed(futures_best):
                sid, url, summary = future.result()
                session.merge(
                    SummariesBestStories(
                        id=sid,
                        url=url,
                        summary=summary,
                    )
                )

        session.commit()


# ==============================
# ENTRYPOINT
# ==============================

if __name__ == "__main__":
    refresh_db_with_top_and_best()
    print("✅ DB refreshed with parallel LLM summaries.")
