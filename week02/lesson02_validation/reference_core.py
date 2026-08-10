"""W2-02A 研究摘要核心字段校验参考实现。"""

from typing import TypedDict


class ResearchSummaryCore(TypedDict):
    research_question: str
    data_source: str
    sample_size: int | None


REQUIRED_FIELDS = ("research_question", "data_source", "sample_size")


def _validate_non_empty_string(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field}: 必须是字符串")
    if not value.strip():
        raise ValueError(f"{field}: 不能为空")
    return value


def _validate_sample_size(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("sample_size: 必须是整数或 None")
    if value <= 0:
        raise ValueError("sample_size: 必须是正整数")
    return value


def validate_summary_core(data: object) -> ResearchSummaryCore:
    """校验未知数据，并只返回核心契约中的字段。"""
    if not isinstance(data, dict):
        raise TypeError("data: 必须是 JSON object")

    missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
    if missing_fields:
        raise ValueError(f"缺少字段: {', '.join(missing_fields)}")

    research_question = _validate_non_empty_string(
        data["research_question"], "research_question"
    )
    data_source = _validate_non_empty_string(data["data_source"], "data_source")
    sample_size = _validate_sample_size(data["sample_size"])

    return ResearchSummaryCore(
        research_question=research_question,
        data_source=data_source,
        sample_size=sample_size,
    )
