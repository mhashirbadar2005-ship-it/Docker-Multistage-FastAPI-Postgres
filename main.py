"""
Task 2 Demo App — FastAPI + PostgreSQL

A small, genuinely multi-dependency web app used to practice:
  - Docker multi-stage builds
  - Environment-variable-based configuration (no hardcoded secrets)
  - Container port mapping

Endpoints:
  GET  /health      -> confirms the app + DB connection are alive
  POST /items        -> create an item {"name": "..."}
  GET  /items         -> list all items
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError

# ---- Configuration: read from environment variables, never hardcoded ----
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/task2db",
)
APP_NAME = os.getenv("APP_NAME", "task2-demo-app")

# ---- Database setup ----
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once, when the container starts: creates the "items" table
    # if it doesn't exist yet. We don't retry here on purpose —
    # docker-compose's healthcheck + depends_on already makes sure the
    # DB is ready before this container starts.
    Base.metadata.create_all(bind=engine)
    yield
    # Anything after `yield` would run on shutdown — nothing needed here.


app = FastAPI(title=APP_NAME, lifespan=lifespan)


@app.get("/health")
def health_check():
    """Container + DB liveness check — useful for compose healthchecks
    and for proving in your report that the two containers can talk."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "app": APP_NAME}
    except OperationalError:
        raise HTTPException(status_code=503, detail="database unavailable")


class ItemIn(BaseModel):
    name: str


@app.post("/items")
def create_item(item: ItemIn):
    db = SessionLocal()
    try:
        db_item = Item(name=item.name)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return {"id": db_item.id, "name": db_item.name, "created_at": db_item.created_at}
    finally:
        db.close()


@app.get("/items")
def list_items():
    db = SessionLocal()
    try:
        items = db.query(Item).all()
        return [
            {"id": i.id, "name": i.name, "created_at": i.created_at}
            for i in items
        ]
    finally:
        db.close()