"""Data model for an extracted Book."""

from dataclasses import dataclass, field
from typing import List

from xsget.chapter import Chapter


@dataclass
class Book:
    """A book class model."""

    chapters: List[Chapter] = field(default_factory=list, repr=False)
    title: str = field(default="")
    authors: List[str] = field(default_factory=list)
