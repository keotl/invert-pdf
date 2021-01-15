import abc
import threading
from typing import Callable, Dict, List

from jivago.lang.annotations import Override


class JobState(str):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    _TYPES = [PENDING, RUNNING, COMPLETED, FAILED, UNKNOWN]

    def __new__(cls, x):
        if x not in cls._TYPES:
            return str.__new__(cls, cls.UNKNOWN)
        else:
            return str.__new__(cls, x)


class CompletionToken(abc.ABC):

    @property
    def state(self) -> JobState:
        raise NotImplementedError

    @property
    def job_id(self) -> str:
        raise NotImplementedError

    def subscribe(self, expected_state: JobState, action: Callable[[], None]):
        raise NotImplementedError


class CompletionTokenSource(CompletionToken):
    def __init__(self, job_id: str, state: JobState):
        self._job_id = job_id
        self._state = state
        self._subscribers: Dict[JobState, List[Callable[[], None]]] = {}
        self._lock = threading.Lock()

    def set_state(self, state: JobState):
        with self._lock:
            if self._state == state:
                return
            self._state = state
        for subscriber in self._subscribers.get(state) or []:
            subscriber()

    @Override
    @property
    def state(self) -> JobState:
        return self._state

    @Override
    @property
    def job_id(self) -> str:
        return self._job_id

    @Override
    def subscribe(self, expected_state: JobState, action: Callable[[], None]):
        with self._lock:
            if self._subscribers.get(expected_state) is None:
                self._subscribers[expected_state] = []
            self._subscribers[expected_state].append(action)
            if self._state == expected_state:
                for subscriber in self._subscribers.get(expected_state) or []:
                    subscriber()
