"""W2-02A 核心字段校验参考测试。"""

import pytest
from reference_core import validate_summary_core


def test_valid_data_returns_only_contract_fields() -> None:
    data = {
        "research_question": "睡眠是否影响压力？",
        "data_source": "研究生问卷",
        "sample_size": 240,
        "unexpected": "discard me",
    }

    assert validate_summary_core(data) == {
        "research_question": "睡眠是否影响压力？",
        "data_source": "研究生问卷",
        "sample_size": 240,
    }


def test_none_sample_size_is_allowed() -> None:
    data = {
        "research_question": "睡眠是否影响压力？",
        "data_source": "研究生问卷",
        "sample_size": None,
    }

    assert validate_summary_core(data)["sample_size"] is None


def test_non_object_top_level_is_rejected() -> None:
    with pytest.raises(TypeError, match="data"):
        validate_summary_core([])


@pytest.mark.parametrize(
    "missing_field",
    ["research_question", "data_source", "sample_size"],
)
def test_missing_required_field_names_the_field(missing_field: str) -> None:
    data: dict[str, object] = {
        "research_question": "问题",
        "data_source": "问卷",
        "sample_size": 100,
    }
    del data[missing_field]

    with pytest.raises(ValueError, match=missing_field):
        validate_summary_core(data)


@pytest.mark.parametrize("field", ["research_question", "data_source"])
def test_text_field_rejects_non_string(field: str) -> None:
    data: dict[str, object] = {
        "research_question": "问题",
        "data_source": "问卷",
        "sample_size": 100,
    }
    data[field] = 123

    with pytest.raises(TypeError, match=field):
        validate_summary_core(data)


@pytest.mark.parametrize("invalid_value", ["", "   "])
def test_research_question_rejects_blank_string(invalid_value: str) -> None:
    data = {
        "research_question": invalid_value,
        "data_source": "问卷",
        "sample_size": 100,
    }

    with pytest.raises(ValueError, match="research_question"):
        validate_summary_core(data)


@pytest.mark.parametrize("invalid_value", ["100", True])
def test_sample_size_rejects_invalid_type(invalid_value: object) -> None:
    data = {
        "research_question": "问题",
        "data_source": "问卷",
        "sample_size": invalid_value,
    }

    with pytest.raises(TypeError, match="sample_size"):
        validate_summary_core(data)


@pytest.mark.parametrize("invalid_value", [0, -1])
def test_sample_size_rejects_non_positive_value(invalid_value: int) -> None:
    data = {
        "research_question": "问题",
        "data_source": "问卷",
        "sample_size": invalid_value,
    }

    with pytest.raises(ValueError, match="sample_size"):
        validate_summary_core(data)
