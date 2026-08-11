"""W2-02B 完整研究摘要契约参考测试。"""

import pytest
from reference_full import validate_research_summary


def make_valid_data() -> dict[str, object]:
    return {
        "research_question": "睡眠是否影响压力？",
        "data_source": "研究生问卷",
        "sample_size": 240,
        "statistical_methods": ["线性回归"],
        "key_findings": ["睡眠时长与压力负相关"],
        "limitations": ["横断面设计不能证明因果关系"],
    }


def test_valid_summary_returns_exact_contract() -> None:
    data = make_valid_data()
    data["unexpected"] = "discard me"

    result = validate_research_summary(data)

    assert set(result) == {
        "research_question",
        "data_source",
        "sample_size",
        "statistical_methods",
        "key_findings",
        "limitations",
    }


def test_empty_lists_are_allowed() -> None:
    data = make_valid_data()
    data["statistical_methods"] = []
    data["key_findings"] = []
    data["limitations"] = []

    result = validate_research_summary(data)

    assert result["statistical_methods"] == []
    assert result["key_findings"] == []
    assert result["limitations"] == []


@pytest.mark.parametrize(
    "missing_field", ["statistical_methods", "key_findings", "limitations"]
)
def test_missing_list_field_names_the_field(missing_field: str) -> None:
    data = make_valid_data()
    del data[missing_field]

    with pytest.raises(ValueError, match=missing_field):
        validate_research_summary(data)


@pytest.mark.parametrize("invalid_value", ["回归", ("回归",), None])
def test_list_field_rejects_non_list(invalid_value: object) -> None:
    data = make_valid_data()
    data["statistical_methods"] = invalid_value

    with pytest.raises(TypeError, match="statistical_methods"):
        validate_research_summary(data)


def test_list_item_type_error_includes_index() -> None:
    data = make_valid_data()
    data["key_findings"] = ["有效发现", 42]

    with pytest.raises(TypeError, match=r"key_findings\[1\]"):
        validate_research_summary(data)


@pytest.mark.parametrize("invalid_value", ["", "   "])
def test_blank_list_item_error_includes_index(invalid_value: str) -> None:
    data = make_valid_data()
    data["limitations"] = ["有效局限", invalid_value]

    with pytest.raises(ValueError, match=r"limitations\[1\]"):
        validate_research_summary(data)


def test_result_lists_do_not_share_input_references() -> None:
    data = make_valid_data()

    result = validate_research_summary(data)
    original_methods = data["statistical_methods"]
    assert isinstance(original_methods, list)
    original_methods.append("外部新增方法")

    assert result["statistical_methods"] == ["线性回归"]
    assert result["statistical_methods"] is not original_methods
