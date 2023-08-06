"""Task database model"""
import json
import uuid

from pathlib import Path
from typing import Optional
from sqlalchemy import (
    CheckConstraint,
    Column,
    Integer,
    JSON,
    Unicode,
    UnicodeText,
    String,
)
from sqlalchemy.ext.declarative import as_declarative, declared_attr

UUID_LENGTH = 6

BOLD = "\033[1m"
UNDERLINE = "\033[4m"
END = "\033[0m"


@as_declarative()
class Base:
    """Declarative base class for SQLAlchemy models"""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(
        String(length=UUID_LENGTH),
        primary_key=True,
        default=lambda: str(uuid.uuid4())[:UUID_LENGTH],
    )


class Task(Base):
    """
    Task Model

    SQLAlchemy declarative model for the tasks3 database containing tasks.

    :param id: Unique ID for the task.
    :param title: Title of the task.
    :param urgency: Urgency level[0-4] of the task.
    :param importance: Importance level[0-4] of the task.
    :param tags: Set of tags to apply to the task.
    :param folder: Anchor this task to a particular directory or file.
    :param description: Description of the task.
    """

    title = Column(Unicode, nullable=False)
    urgency = Column(Integer, nullable=False)
    importance = Column(Integer, nullable=False)
    tags = Column(JSON, nullable=False)
    folder = Column(Unicode, nullable=True)
    description = Column(UnicodeText, nullable=True)

    __table_args__ = (
        CheckConstraint(0 <= urgency, "Urgency interval check"),
        CheckConstraint(urgency <= 4, "Urgency interval check"),
        CheckConstraint(0 <= importance, "Importance interval check"),
        CheckConstraint(importance <= 4, "Importance interval check"),
    )

    def to_dict(self) -> dict:
        return dict(
            id=self.id,
            title=self.title,
            urgency=self.urgency,
            importance=self.importance,
            tags=self.tags,
            folder=self.folder,
            description=self.description,
        )

    @property
    def relative_folder(self) -> Optional[str]:
        """Relative path to the folder this task is anchored to"""
        if self.folder is None or len(self.folder) == 0:
            return None
        try:
            folder = Path(self.folder).relative_to(Path.cwd())
            return str(folder)
        except ValueError:
            return self.folder

    def one_line(self) -> str:
        """One line Human-friendly representation of the task"""
        rep = "[      ] "
        if self.id is not None and len(self.id) == UUID_LENGTH:
            rep = f"[{self.id}] "
        rep += f"{BOLD}{self.title}{END}"
        if self.relative_folder is not None and self.relative_folder != ".":
            rep += f" [path: {UNDERLINE}{self.relative_folder}{END}]"
        return rep

    def short(self) -> str:
        """Short Human-friendly representation of the task"""
        rep = "[      ] "
        if self.id is not None and len(self.id) == UUID_LENGTH:
            rep = f"[{self.id}] "
        urgent = ("⏰" * self.urgency) + ("  " * (4 - self.urgency))
        important = ("🚨" * self.importance) + (" " * (4 - self.importance))
        rep += f"{BOLD}{self.title}{END} ({urgent}) ({important})"
        if self.relative_folder is not None and self.relative_folder != ".":
            rep += "\n  " + f"[path: {UNDERLINE}{self.relative_folder}{END}]"
        if len(self.tags) > 0:
            tags = [f"({tag})" for tag in self.tags]
            rep += "\n  " + " ".join(tags)
        if self.description is not None and len(self.description) > 0:
            rep += "\n    " + self.description.replace("\n", "\n    ")
        return rep

    def yaml(self) -> str:
        """YAML representation of the task"""
        top = (
            f"title: {self.title}\n"
            f"urgency: {self.urgency}\n"
            f"importance: {self.importance}"
        )
        tags = "tags: null"
        if len(self.tags) > 0:
            tags = "tags:\n  - " + "\n  - ".join(self.tags)
        folder = f"folder: {'null' if self.folder is None else self.folder}"
        yaml = f"{top}\n{tags}\n{folder}\n"
        if self.description is not None and len(self.description) > 0:
            description = self.description.replace("\n", "\n  ")
            yaml += f"description: >-\n  {description}\n"
        return yaml

    def json(self) -> str:
        """JSON representation of the task"""
        return json.dumps(self.to_dict(), indent=2)

    def __repr__(self) -> str:
        return f"<Task{self.to_dict().__repr__()}>"
