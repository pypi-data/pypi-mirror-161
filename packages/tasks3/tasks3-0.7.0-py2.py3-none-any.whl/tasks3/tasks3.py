"""Main module."""

from functools import singledispatch
from typing import List, Optional

from tasks3.db import Task, session_scope

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Query


def search(
    db_engine: Engine,
    id: Optional[str] = None,
    title: Optional[str] = None,
    urgency: Optional[int] = None,
    importance: Optional[int] = None,
    tags: Optional[List[str]] = None,
    folder: Optional[str] = None,
    description: Optional[str] = None,
) -> List[Task]:
    """Search for tasks

    :param id: Search for tasks that start with ``id``.
    :param title: Search for tasks with this substring in title.
    :param urgency: Search for tasks with this urgency level.
    :param importance: Search for tasks with this importance level.
    :param tags: Search for tasks with all these tags.
    :param folder: Search for tasks under this folder.
    :param db_engine: Engine for the tasks database.
    """
    with session_scope(db_engine) as session:
        query: Query = Query(Task, session)
        if urgency:
            query = query.filter(Task.urgency == urgency)
        if importance:
            query = query.filter(Task.importance == importance)
        if id:
            query = query.filter(Task.id.contains(id))
        if title:
            query = query.filter(Task.title.contains(title))
        if folder:
            query = query.filter(Task.folder.like(f"{folder}%"))
        if description:
            query = query.filter(Task.description.contains(description))
        results = query.order_by(Task.urgency, Task.importance).all()
        results.reverse()
        if tags:
            results = [task for task in results if set(tags) <= set(task.tags)]
        return results


@singledispatch
def add(
    title: str,
    urgency: int,
    importance: int,
    tags: List[str],
    folder: str,
    description: str,
    db_engine: Engine,
) -> str:
    """Add a task

    :param title: Title for the new task.
    :param urgency: Urgency level[0-4] for the new task.
    :param importance: Importance level[0-4] for the new task.
    :param tags: Set of tags to apply to the new task.
    :param folder: Delegate this task to a particular directory or file.
    :param description: Description of the task.
    :param db_engine: Engine for the tasks database.
    """
    task = Task(
        title=title,
        urgency=urgency,
        importance=importance,
        tags=tags,
        folder=folder,
        description=description,
    )
    return add(task, db_engine)


@add.register(Task)
def _(
    task: Task,
    db_engine: Engine,
) -> str:
    """Add a task

    :param task: Task to add.
    :param db_engine: Engine for the tasks database.
    """
    with session_scope(db_engine) as session:
        session.add(task)
        session.flush()
        return task.id


def edit(
    id: str,
    db_engine: Engine,
    title: str = None,
    urgency: int = None,
    importance: int = None,
    tags: List[str] = None,
    folder: str = None,
    description: str = None,
    dry_run: bool = False,
) -> Task:
    """Edit a task

    :param id: ID of the task to edit.
    :param db_engine: Engine for the tasks database.
    :param title: Update title of the task.
    :param urgency: Update urgency level[0-4] of the task.
    :param importance: Update importance level[0-4] of the task.
    :param tags: Set of tags to apply to the new task.
    :param folder: Delegate this task to a particular directory or file.
    :param description: Description of the task.
    """
    with session_scope(db_engine) as session:
        task: Task = Query(Task, session).filter_by(id=id).one()
        if title:
            task.title = title
        if urgency:
            task.urgency = urgency
        if importance:
            task.importance = importance
        if tags:
            task.tags = tags
        if folder:
            task.folder = folder
        if description:
            task.description = description
        if dry_run:
            task = Task(**task.to_dict())
            session.rollback()
            return task
        session.add(task)
        return task


def remove(id: str, db_engine: Engine) -> Task:
    """Remove a Task

    :param id: ID of the task to remove.
    :param db_engine: Engine for the tasks database.
    """
    with session_scope(db_engine) as session:
        task: Task = Query(Task, session).filter_by(id=id).one()
        session.delete(task)
    return task
