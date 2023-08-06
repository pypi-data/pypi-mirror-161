#!/usr/bin/env python

"""Tests for tasks3's database"""

import pytest

from typing import Tuple
from pathlib import Path
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, Query

from tasks3 import db
from tasks3.db import Task, session_scope


@pytest.fixture(params=["sqlite"])
def db_backend(request) -> str:
    return request.param


def get_db(tmp_path: Path, backend: str) -> Tuple[Path, Engine]:
    tasks3_path = tmp_path.joinpath("tasks3")
    tasks3_path.mkdir()
    db_path = tasks3_path.joinpath("task.db")
    db_engine = create_engine(f"{backend}:///{db_path}")
    return db_path, db_engine


def test_db_init(tmp_path: Path, db_backend: str):
    db_path, db_engine = get_db(tmp_path, db_backend)
    assert not db_path.exists()
    db.init(db_engine)
    assert db_path.exists()
    table_names = inspect(db_engine).get_table_names()
    assert len(table_names) == 1
    assert "task" in table_names


def test_db_add_task(tmp_path: Path, db_backend: str):
    db_path, db_engine = get_db(tmp_path, db_backend)
    db.init(db_engine)
    table_names = inspect(db_engine).get_table_names()
    assert "task" in table_names
    task = Task(title="Title", urgency=2, importance=2, tags=["pytest"])
    session: Session
    count: int
    with session_scope(db_engine) as session:
        session.add(task)
        count = Query(Task, session).count()
    assert count == 1


def test_db_purge(tmp_path: Path, db_backend: str):
    db_path, db_engine = get_db(tmp_path, db_backend)
    db.init(db_engine)
    table_names = inspect(db_engine).get_table_names()
    assert "task" in table_names
    task = Task(title="Title", urgency=2, importance=2, tags=["pytest"])
    session: Session
    count: int
    with session_scope(db_engine) as session:
        session.add(task)
        count = Query(Task, session).count()
    assert count == 1
    db.purge(db_engine)
    with session_scope(db_engine) as session:
        count = Query(Task, session).count()
    assert count == 0


def test_db_drop(tmp_path: Path, db_backend: str):
    db_path, db_engine = get_db(tmp_path, db_backend)
    db.init(db_engine)
    table_names_before = inspect(db_engine).get_table_names()
    assert "task" in table_names_before
    db.drop(db_engine)
    table_names_after = inspect(db_engine).get_table_names()
    assert len(table_names_after) == 0
    assert "task" not in table_names_after
