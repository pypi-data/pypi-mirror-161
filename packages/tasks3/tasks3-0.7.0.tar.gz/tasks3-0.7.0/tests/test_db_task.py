#!/usr/bin/env python

"""Tests for tasks3's Task ORM"""

import pytest

from tasks3.db import Task

from typing import Set


@pytest.fixture(params=["Title"])
def title(request) -> str:
    return request.param


@pytest.fixture(params=[0, 4], ids=["Not Urgent", "Very Urgent"])
def urgency(request) -> int:
    return request.param


@pytest.fixture(params=[0, 4], ids=["Not Important", "Very Important"])
def importance(request) -> int:
    return request.param


@pytest.fixture(params=[{"pytest"}])
def tags(request) -> Set[str]:
    return request.param


def test_task_create(title: str, urgency: int, importance: int, tags: Set[str]):
    task = Task(
        title=title,
        urgency=urgency,
        importance=importance,
        tags=tags,
    )
    assert task.title == title
    assert task.urgency == urgency
    assert task.importance == importance
    assert task.tags == tags
