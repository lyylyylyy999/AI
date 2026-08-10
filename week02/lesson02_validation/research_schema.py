from typing import TypedDict


class ResearchSummaryCore(TypedDict):
    research_question: str
    data_source: str
    sample_size: int | None


class ResearchSummary(ResearchSummaryCore):
    statistical_methods: list[str]
    key_findings: list[str]
    limitations: list[str]


REQUIRED_FIELDS = (
    "research_question",
    "data_source",
    "sample_size",
    "statistical_methods",
    "key_findings",
    "limitations",
)


def validate_summary_core(data: object) -> ResearchSummaryCore:
    if not isinstance(data, dict):
        raise TypeError("传入的必须是字典")
    required = {"research_question", "data_source", "sample_size"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"缺少字段: {', '.join(missing)}")
    str_fields = []
    if not isinstance(data["research_question"], str):
        str_fields.append("research_question")
    if not isinstance(data["data_source"], str):
        str_fields.append("data_source")
    if str_fields:
        raise TypeError(f"{', '.join(str_fields)}: 必须为字符串")
    empty_fields = []
    if not data["research_question"].strip():
        empty_fields.append("research_question")
    if not data["data_source"].strip():
        empty_fields.append("data_source")
    if empty_fields:
        raise ValueError(f"{', '.join(empty_fields)}: 字符串为空")
    if isinstance(data["sample_size"], bool):
        raise TypeError("sample_size: 不能为 bool 类型")
    if data["sample_size"] is not None and not isinstance(data["sample_size"], int):
        raise TypeError("sample_size: 必须为 int 类型")
    elif data["sample_size"] is not None and data["sample_size"] <= 0:
        raise ValueError("sample_size: 必须是正数")
    return ResearchSummaryCore(
        research_question=data["research_question"],
        data_source=data["data_source"],
        sample_size=data["sample_size"],
    )


def _validate_string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list):
        raise TypeError("字段值必须是列表")
    for i in range(len(value)):
        if not isinstance(value[i], str):
            raise TypeError(f"{field}的第{i}个值: 必须是字符串")
        if not value[i].strip():
            raise ValueError(f"{field}的第{i}个值: 不能是空字符串")
    return value


def validate_research_summary(data: object) -> ResearchSummary:
    if not isinstance(data, dict):
        raise TypeError("data 必须是字典")
    missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
    if missing_fields:
        raise ValueError(f"缺少字段: {', '.join(missing_fields)}")
    core = validate_summary_core(data)
    research_question = core["research_question"]
    data_source = core["data_source"]
    sample_size = core["sample_size"]
    statistical_methods = _validate_string_list(
        data["statistical_methods"], "statistical_methods"
    )
    key_findings = _validate_string_list(data["key_findings"], "key_findings")
    limitations = _validate_string_list(data["limitations"], "limitations")
    return ResearchSummary(
        research_question=research_question,
        data_source=data_source,
        sample_size=sample_size,
        statistical_methods=statistical_methods,
        key_findings=key_findings,
        limitations=limitations,
    )


data = {
    "research_question": "研究问题",
    "data_source": "GitHub",
    "sample_size": None,
    "statistical_methods": [],
    "key_findings": ["123", "234"],
    "limitations": ["123", "234", "345"],
}
print(validate_research_summary(data))
