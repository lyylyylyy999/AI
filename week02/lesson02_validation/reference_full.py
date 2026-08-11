"""W2-02B 完整研究摘要契约参考实现。"""

from reference_core import ResearchSummaryCore, validate_summary_core


class ResearchSummary(ResearchSummaryCore):
    statistical_methods: list[str]
    key_findings: list[str]
    limitations: list[str]


LIST_FIELDS = ("statistical_methods", "key_findings", "limitations")


def _validate_string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list):
        raise TypeError(f"{field}: 必须是列表")

    validated_items: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise TypeError(f"{field}[{index}]: 必须是字符串")
        if not item.strip():
            raise ValueError(f"{field}[{index}]: 不能为空")
        validated_items.append(item)

    return validated_items


def validate_research_summary(data: object) -> ResearchSummary:
    """校验未知数据，并返回与输入可变列表隔离的研究摘要。"""
    if not isinstance(data, dict):
        raise TypeError("data: 必须是 JSON object")

    missing_fields = [field for field in LIST_FIELDS if field not in data]
    if missing_fields:
        raise ValueError(f"缺少字段: {', '.join(missing_fields)}")

    core = validate_summary_core(data)
    statistical_methods = _validate_string_list(
        data["statistical_methods"], "statistical_methods"
    )
    key_findings = _validate_string_list(data["key_findings"], "key_findings")
    limitations = _validate_string_list(data["limitations"], "limitations")

    return ResearchSummary(
        **core,
        statistical_methods=statistical_methods,
        key_findings=key_findings,
        limitations=limitations,
    )
