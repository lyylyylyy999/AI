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
    with pytest.raises(TypeError):
        validate_summary_core(data)


@pytest.mark.parametrize(
    ("data"),
    [
        {"data_source": "GitHub", "sample_size": None},
        {"research_question": "研究问题", "sample_size": None},
        {
            "research_question": "研究问题",
            "data_source": "GitHub",
        },
    ],
)
def test_missing_field(data: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        validate_summary_core(data)


@pytest.mark.parametrize(
    ("data"),
    [
        {"research_question": "研究问题", "data_source": "", "sample_size": None},
        {"research_question": "", "data_source": "GitHub", "sample_size": None},
        {"research_question": "研究问题", "data_source": "     ", "sample_size": None},
    ],
)
def test_empty(data: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        validate_summary_core(data)


@pytest.mark.parametrize(
    ("data"),
    [
        {
            "research_question": "研究问题",
            "data_source": "GitHub",
            "sample_size": "123",
        },
        {"research_question": "研究问题", "data_source": "GitHub", "sample_size": -123},
        {"research_question": "研究问题", "data_source": "GitHub", "sample_size": 0},
        {"research_question": "研究问题", "data_source": "GitHub", "sample_size": True},
    ],
    ids=("str", "negative", "zero", "bool"),
)
def test_sample_size_with_exception(data: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        validate_summary_core(data)


if __name__ == "__main__":
    pytest.main(["week02/lesson02_validation/test_research_schema.py", "-qs"])
