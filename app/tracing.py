import time
from collections.abc import Callable
from types import TracebackType
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict


class TraceRecord(BaseModel):
    model_config = ConfigDict(
        frozen=True, strict=True, extra="forbid", hide_input_in_errors=True,
    )

    request_name: str
    status: Literal["success", "failure"]
    elapsed_seconds: float
    error_type: str | None


class RequestTrace:
    def __init__(
        self,
        request_name: str,
        sink: Callable[[TraceRecord], None],
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self.request_name = request_name
        if not isinstance(self.request_name, str) or not self.request_name.strip():
            raise ValueError("request_name 只能是非空字符串类型")
        self._clock = clock
        self.sink = sink
        self._record: TraceRecord | None = None
        self._entered = False
        self._start: float

    @property
    def record(self) -> TraceRecord | None:
        return self._record

    def __enter__(self) -> Self:
        if self._entered:
            raise RuntimeError("同一个请求追踪实例只能进入一次")

        self._entered = True
        self._start = self._clock()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        end = self._clock()
        spend_time = end - self._start
        self._record = TraceRecord(
            request_name=self.request_name,
            status="success" if exc_type is None else "failure",
            elapsed_seconds=spend_time,
            error_type=None if exc_type is None else exc_type.__name__,
        )
        self.sink(self._record)
        return False
