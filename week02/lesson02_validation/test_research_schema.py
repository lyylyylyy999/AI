import pytest
from research_schema import validate_research_summary, validate_summary_core


def test_sample_size_with_positive() -> None:
    data = {
        "research_question": "研究问题",
        "data_source": "GitHub",
        "sample_size": 123,
        "additional": 234,
    }
    text = validate_summary_core(data)
    assert text["sample_size"] is not None
    assert text["sample_size"] > 0
    assert set(text.keys()) == {"research_question", "data_source", "sample_size"}


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
    ("data", "exception", "match"),
    [
        (
            {"data_source": "GitHub", "sample_size": None},
            ValueError,
            "缺少字段: research_question",
        ),
        (
            {"research_question": "研究问题", "sample_size": None},
            ValueError,
            "缺少字段: data_source",
        ),
        (
            {"research_question": "研究问题", "data_source": "GitHub"},
            ValueError,
            "缺少字段: sample_size",
        ),
    ],
    ids=("research_question", "data_source", "sample_size"),
)
def test_missing_field(
    data: dict[str, object], exception: type[Exception], match: str
) -> None:
    with pytest.raises(exception, match=match):
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


def test_alidate_research_summary_with_normal() -> None:
    data = {
        "research_question": "研究问题",
        "data_source": "GitHub",
        "sample_size": None,
        "statistical_methods": [],
        "key_findings": ["123", "234"],
        "limitations": ["123", "234", "345"],
    }
    assert validate_research_summary(data) == data


def test_value_with_empty() -> None:
    data: dict[str, object] = {
        "research_question": "研究问题",
        "data_source": "GitHub",
        "sample_size": None,
        "statistical_methods": [],
        "key_findings": [],
        "limitations": [],
    }
    assert validate_research_summary(data) == data


@pytest.mark.parametrize(
    ("data", "exception", "match"),
    [
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": None,
                "key_findings": ["123", "234"],
                "limitations": ["123", "234", "345"],
            },
            ValueError,
            "缺少字段: statistical_methods",
        ),
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": None,
                "statistical_methods": [],
                "limitations": ["123", "234", "345"],
            },
            ValueError,
            "缺少字段: key_findings",
        ),
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": None,
                "statistical_methods": [],
                "key_findings": ["123", "234"],
            },
            ValueError,
            "缺少字段: limitations",
        ),
    ],
    ids=("statistical_methods", "key_findings", "limitations"),
)
def test_missing_field_2(
    data: dict[str, object], exception: type[Exception], match: str
) -> None:
    with pytest.raises(exception, match=match):
        validate_research_summary(data)


@pytest.mark.parametrize(
    ("data", "exception", "match"),
    [
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": None,
                "statistical_methods": "123",
                "key_findings": ["123", "234"],
                "limitations": ["123", "234", "345"],
            },
            TypeError,
            "statistical_methods: 必须是列表",
        ),
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": None,
                "statistical_methods": [],
                "key_findings": ("123", "234"),
                "limitations": ["123", "234", "345"],
            },
            TypeError,
            "key_findings: 必须是列表",
        ),
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": None,
                "statistical_methods": [],
                "key_findings": ["123", "234"],
                "limitations": None,
            },
            TypeError,
            "limitations: 必须是列表",
        ),
    ],
    ids=("statistical_methods", "key_findings", "limitations"),
)
def test_value_with_exception(
    data: dict[str, object], exception: type[Exception], match: str
) -> None:
    with pytest.raises(exception, match=match):
        validate_research_summary(data)


@pytest.mark.parametrize(
    ("data", "exception", "match"),
    [
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": None,
                "statistical_methods": [123],
                "key_findings": ["123", "234"],
                "limitations": ["123", "234", "345"],
            },
            TypeError,
            "statistical_methods的第0个值: 必须是字符串",
        ),
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": None,
                "statistical_methods": [],
                "key_findings": [123],
                "limitations": ["123", "234", "345"],
            },
            TypeError,
            "key_findings的第0个值: 必须是字符串",
        ),
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": None,
                "statistical_methods": [],
                "key_findings": ["123", "234"],
                "limitations": [123],
            },
            TypeError,
            "limitations的第0个值: 必须是字符串",
        ),
    ],
    ids=("statistical_methods", "key_findings", "limitations"),
)
def test_element_with_int(
    data: dict[str, object], exception: type[Exception], match: str
) -> None:
    with pytest.raises(exception, match=match):
        validate_research_summary(data)


@pytest.mark.parametrize(
    ("data", "exception", "match"),
    [
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": None,
                "statistical_methods": [""],
                "key_findings": ["123", "234"],
                "limitations": ["123", "234", "345"],
            },
            ValueError,
            "statistical_methods的第0个值: 不能是空字符串",
        ),
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": None,
                "statistical_methods": [],
                "key_findings": ["  "],
                "limitations": ["123", "234", "345"],
            },
            ValueError,
            "key_findings的第0个值: 不能是空字符串",
        ),
        (
            {
                "research_question": "研究问题",
                "data_source": "GitHub",
                "sample_size": None,
                "statistical_methods": [],
                "key_findings": ["123", "234"],
                "limitations": ["   "],
            },
            ValueError,
            "limitations的第0个值: 不能是空字符串",
        ),
    ],
    ids=("statistical_methods", "key_findings", "limitations"),
)
def test_empty_element(
    data: dict[str, object], exception: type[Exception], match: str
) -> None:
    with pytest.raises(exception, match=match):
        validate_research_summary(data)


def test_additional_value() -> None:
    data = {
        "research_question": "研究问题",
        "data_source": "GitHub",
        "sample_size": None,
        "statistical_methods": [],
        "key_findings": ["123", "234"],
        "limitations": ["123", "234", "345"],
        "addition": "abc",
    }
    assert validate_research_summary(data) == {
        "research_question": "研究问题",
        "data_source": "GitHub",
        "sample_size": None,
        "statistical_methods": [],
        "key_findings": ["123", "234"],
        "limitations": ["123", "234", "345"],
    }


def test_new_list() -> None:
    a = ["12"]
    b = ["12", "23"]
    c = ["12", "23", "34"]
    data = {
        "research_question": "研究问题",
        "data_source": "GitHub",
        "sample_size": None,
        "statistical_methods": a,
        "key_findings": b,
        "limitations": c
    }
    result = validate_research_summary(data)
    a.append("123")
    assert result["statistical_methods"] is not a
    assert result == {
        "research_question": "研究问题",
        "data_source": "GitHub",
        "sample_size": None,
        "statistical_methods": ["12"],
        "key_findings": ["12", "23"],
        "limitations": ["12", "23", "34"]
    }



if __name__ == "__main__":
    pytest.main(["week02/lesson02_validation/test_research_schema.py", "-qs"])
