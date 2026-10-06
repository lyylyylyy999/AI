from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel


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

    return application
