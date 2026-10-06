from collections.abc import Iterable
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic_core import PydanticCustomError


class InvalidMessageError(ValueError):
    """提供稳定的错误类别与行号，不包含原始输入。"""

    def __init__(self, code: str, line_number: int | None = None) -> None:
        self.code = code
        self.line_number = line_number
        location = f"第{line_number}行：" if line_number is not None else ""
        super().__init__(f"{location}消息校验失败 ({code})")


class Message(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True)

    conversation_id: str
    role: Literal["system", "user", "assistant"]
    content: str

    @field_validator("role", mode="before")
    @classmethod
    def validate_role_type(cls, value: object) -> object:
        if not isinstance(value, str):
            raise PydanticCustomError("invalid_type", "角色必须是字符串")
        return value

    @field_validator("conversation_id", "content")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        if not value.strip():
            raise PydanticCustomError("blank_value", "字段不能为空或仅包含空白字符")
        return value


class Statistics(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True)

    total_messages: int
    conversation_count: int
    messages_by_role: dict[str, int]
    total_characters: int


def summarize(messages: Iterable[Message]) -> Statistics:
    """遍历消息一次，按原始正文统计字符数，包括空白字符。"""
    total_messages = 0
    conversation_ids: set[str] = set()
    messages_by_role = {"system": 0, "user": 0, "assistant": 0}
    total_characters = 0
    for message in messages:
        total_messages += 1
        conversation_ids.add(message.conversation_id)
        messages_by_role[message.role] += 1
        total_characters += len(message.content)
    return Statistics(
        total_messages=total_messages,
        conversation_count=len(conversation_ids),
        messages_by_role=messages_by_role,
        total_characters=total_characters,
    )
