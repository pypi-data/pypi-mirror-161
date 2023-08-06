from dataclasses import dataclass, field

from .typing import ComponentIncludes


@dataclass()
class Theme:
    name: str
    includes: ComponentIncludes = field(default_factory=ComponentIncludes)
