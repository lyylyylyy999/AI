from io import StringIO
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from app.domain import InvalidMessageError, Message, Statistics, summarize
from app.jsonl import parse_lines


class HealthResponse(BaseModel):
    status: Literal["ok"]


class APIError(BaseModel):
    code: str
    message: str
    request_id: str
    line_number: int | None = None


def error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    line_number: int | None = None,
) -> JSONResponse:
    """只序列化安全字段，不包含异常原文或框架校验输入。"""
    error = APIError(
        code=code,
        message=message,
        request_id=request.state.request_id,
        line_number=line_number,
    )
    return JSONResponse(
        status_code=status_code,
        content=error.model_dump(exclude_none=True),
        headers={"X-Request-ID": error.request_id},
    )


def create_app() -> FastAPI:
    application = FastAPI(
        title="对话日志管理与统计服务",
        version="0.1.0",
        description="支持上传 UTF-8 JSONL 并返回统计；尚未实现持久化、数据库或模型分析。",
    )

    @application.middleware("http")
    async def add_request_id(request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @application.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(request, 422, "invalid_request", "请求字段缺失或类型不正确。")

    @application.exception_handler(InvalidMessageError)
    async def invalid_log(request: Request, exc: InvalidMessageError) -> JSONResponse:
        status_code = 413 if exc.code == "file_too_large" else 422
        return error_response(request, status_code, exc.code, "上传日志校验失败。", exc.line_number)

    @application.exception_handler(Exception)
    async def internal_error(request: Request, exc: Exception) -> JSONResponse:
        return error_response(request, 500, "internal_error", "服务器内部错误。")

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        """仅检查服务进程是否存活，不检查数据库或大模型是否就绪。"""
        return HealthResponse(status="ok")

    @application.post("/api/v1/logs/statistics", response_model=Statistics)
    def statistics(file: UploadFile) -> Statistics:
        data = file.file.read(2 * 1024 * 1024 + 1)
        if len(data) > 2 * 1024 * 1024:
            raise InvalidMessageError("file_too_large")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            raise InvalidMessageError("invalid_encoding") from None
        messages: list[Message] = []
        with StringIO(text, newline=None) as lines:
            for message in parse_lines(lines):
                if len(messages) == 10000:
                    raise InvalidMessageError("too_many_messages")
                messages.append(message)
        if not messages:
            raise InvalidMessageError("empty_log")
        return summarize(messages)

    return application
