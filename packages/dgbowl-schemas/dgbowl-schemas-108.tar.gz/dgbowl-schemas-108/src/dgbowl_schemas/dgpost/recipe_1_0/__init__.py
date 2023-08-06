from pydantic import BaseModel, Extra
from typing import Optional, Literal, Sequence
from .load import Load
from .extract import Extract
from .transform import Transform
from .plot import Plot
from .save import Save


class Recipe(BaseModel, extra=Extra.forbid):
    version: Literal["v1.0"]
    load: Optional[Sequence[Load]]
    extract: Optional[Sequence[Extract]]
    transform: Optional[Sequence[Transform]]
    plot: Optional[Sequence[Plot]]
    save: Optional[Sequence[Save]]
