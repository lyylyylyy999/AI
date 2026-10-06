from typing import Literal

from fastapi import FastAPI, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.domain import InvalidMessageError, Statistics, summarize
from app.jsonl import parse_lines


class HealthResponse(BaseModel):
    status: Literal["ok"]


def create_app() -> FastAPI:
    application = FastAPI(
        title="对话日志管理与统计服务",
        version="0.1.0",
        description="当前为训练用最小入口，尚未实现日志导入、数据库或模型分析。",
    )

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        """仅检查服务进程是否存活，不检查数据库或大模型是否就绪。"""
        return HealthResponse(status="ok")

    @application.post("/api/v1/logs/statistics", response_model=Statistics)
    def statistics(file: UploadFile) -> Statistics:
        data = file.file.read()
        if len(data) > 2 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="file_too_large",
            )
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="invalid_encoding"
            )
        try:
            message = list(parse_lines(line for line in text.splitlines()))
        except InvalidMessageError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            )
        if len(message) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="empty_log"
            )
        if len(message) > 10000:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="too_many_messages"
            )
        result = summarize(iter(message))
        return result

    return application
