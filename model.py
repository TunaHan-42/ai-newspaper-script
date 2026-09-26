from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class NewsModel:
    title: str
    text: str
    link: str
    source: str

    date: Optional[str] = None

    def to_dict(self):
        return asdict(self)