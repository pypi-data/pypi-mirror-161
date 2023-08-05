from enum import Enum


class WorkStatus(Enum):
    Wait = 0,
    Run = 1,
    Stop = 2,
    Break = 3,
    Done = 4,
    Fail = 5


class EventType(Enum):
    Instance = 0,
    Keeping = 1