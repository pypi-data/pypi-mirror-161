from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CodeCellConfig:
    highlights: List[List[int]] = field(default_factory=list)
    title: Optional[str] = None
