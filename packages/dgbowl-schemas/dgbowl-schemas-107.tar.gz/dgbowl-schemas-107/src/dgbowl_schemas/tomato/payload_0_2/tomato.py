from pydantic import BaseModel, Extra, Field
from typing import Literal


class Tomato(BaseModel, extra=Extra.forbid):
    class Output(BaseModel, extra=Extra.forbid):
        path: str = None
        prefix: str = "results"
    
    class Snapshot(BaseModel, extra=Extra.forbid):
        path: str = None
        prefix: str = "snapshot"
        frequency: int = 3600

    unlock_when_done: bool = False
    verbosity: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "WARNING"
    output: Output = Field(default_factory=Output)
    snapshot: Snapshot = None
