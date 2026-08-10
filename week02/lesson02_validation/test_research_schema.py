import pytest
from research_schema import validate_summary_core


def test_sample_size_with_positive() -> None:
    data = {
        "research_question": "研究问题",
        "data_source": "GitHub",
        "sample_size": 123,
    }
    text = validate_summary_core(data)
    assert text["sample_size"] is not None
    assert text["sample_size"] > 0


def test_sample_size_with_None() -> None:
    data = {
        "research_question": "研究问题",
        "data_source": "GitHub",
        "sample_size": None,
    }
    text = validate_summary_core(data)
    assert text["sample_size"] is None


def test_list() -> None:
    data = ["research_question", "data_source", "sample_size"]
    with pytest.raises(TypeError, match="传入的必须是字典"):
        validate_summary_core(data)


@pytest.mark.parametrize(
    ("data"),
    [
        {"data_source": "GitHub", "sample_size": None},
        {"research_question": "研究问题", "sample_size": None},
        {"research_question": "研究问题", "data_source": "GitHub"},
    ],
)
def test_missing_field(data: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        validate_summary_core(data)


@pytest.mark.parametrize(
    ("data", "exception", "match"),
    [
        (
            {"research_question": 123, "data_source": "GitHub", "sample_size": None},
            TypeError,
            "research_question: 必须为字符串",
        ),
        (
            {"research_question": "研究问题", "data_source": 123, "sample_size": None},
            TypeError,
            "data_source: 必须为字符串",
        ),
        (
            {"research_question": "研究问题", "data_source": "", "sample_size": None},
            ValueError,
            "data_source: 字符串为空",
        ),
        (
            {"research_question": "   ", "data_source": "GitHub", "sample_size": None},
            ValueError,
            "research_question: 字符串为空",
        ),
    ],
    ids=(
        "str_research_question",
        "str_data_source",
        "empty_data_source",
        "empty_research_question",
    ),
)
def test_str(data: dict[str, object], exception: type[Exception], match: str) -> None:
    with pytest.raises(exception, match=match):
        validate_summary_core(data)


@pytest.mark.parametrize(
    ("data", "exception", "match"),
    [
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": "123",
            },
            TypeError,
            "sample_size: 必须为 int 类型",
        ),
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": -123,
            },
            ValueError,
            "sample_size: 必须是正数",
        ),
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": 0,
            },
            ValueError,
            "sample_size: 必须是正数",
        ),
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": True,
            },
            TypeError,
            "sample_size: 不能为 bool 类型",
        ),
    ],
    ids=("str", "negative", "zero", "bool"),
)
def test_sample_size_with_exception(
    data: dict[str, object], exception: type[Exception], match: str
) -> None:
    with pytest.raises(exception, match=match):
        validate_summary_core(data)


if __name__ == "__main__":
    pytest.main(["week02/lesson02_validation/test_research_schema.py", "-qs"])
