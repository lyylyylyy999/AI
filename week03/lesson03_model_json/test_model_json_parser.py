import pytest
from model_json_parser import parse_research_summary_content


def test_valid_model_json_parser() -> None:
    data = """{
        "research_question": "人工智能是否提高学习效率？",
        "data_source": "问卷调查",
        "sample_size": 100,
        "statistical_methods": ["t-test"],
        "key_findings": ["学习效率有所提升"],
        "limitations": ["样本范围有限"]
    }"""
    result = parse_research_summary_content(data)
    assert result == {
        "research_question": "人工智能是否提高学习效率？",
        "data_source": "问卷调查",
        "sample_size": 100,
        "statistical_methods": ["t-test"],
        "key_findings": ["学习效率有所提升"],
        "limitations": ["样本范围有限"],
    }


@pytest.mark.parametrize(
    ("data", "result"),
    [
        (
            """```json
            {
                "research_question": "人工智能是否提高学习效率？",
                "data_source": "问卷调查",
                "sample_size": 100,
                "statistical_methods": ["t-test"],
                "key_findings": ["学习效率有所提升"],
                "limitations": ["样本范围有限"]
            }
                ```""",
            {
                "research_question": "人工智能是否提高学习效率？",
                "data_source": "问卷调查",
                "sample_size": 100,
                "statistical_methods": ["t-test"],
                "key_findings": ["学习效率有所提升"],
                "limitations": ["样本范围有限"],
            },
        ),
        (
            """```
            {
                "research_question": "人工智能是否提高学习效率？",
                "data_source": "问卷调查",
                "sample_size": 100,
                "statistical_methods": ["t-test"],
                "key_findings": ["学习效率有所提升"],
                "limitations": ["样本范围有限"]
            }
                ```""",
            {
                "research_question": "人工智能是否提高学习效率？",
                "data_source": "问卷调查",
                "sample_size": 100,
                "statistical_methods": ["t-test"],
                "key_findings": ["学习效率有所提升"],
                "limitations": ["样本范围有限"],
            },
        ),
    ],
)
def test_markdown_code_fence(data: str, result: object) -> None:
    assert result == parse_research_summary_content(data)


@pytest.mark.parametrize(
    ("data", "exception", "match"),
    [
        ("", ValueError, "content 不能为空"),
        ("  ", ValueError, "content 不能为空"),
        (
            """```json            
                ```""",
            ValueError,
            "content 不能为空",
        ),
    ],
)
def test_content_empty(data: str, exception: type[Exception], match: str) -> None:
    with pytest.raises(exception, match=match):
        parse_research_summary_content(data)


@pytest.mark.parametrize(
    ("data", "exception", "match"),
    [
        ("{", ValueError, "content 不是合法的 JSON"),
        (
            """``json          
                ```""",
            ValueError,
            "content 不是合法的 JSON",
        ),
        (
            """[
                "research_question": "人工智能是否提高学习效率？",
                "data_source": "问卷调查",
                "sample_size": 100,
                "statistical_methods": ["t-test"],
                "key_findings": ["学习效率有所提升"],
            ]""",
            ValueError,
            "content 不是合法的 JSON",
        ),
    ],
)
def test_invalid_json(data: str, exception: type[Exception], match: str) -> None:
    with pytest.raises(exception, match=match):
        parse_research_summary_content(data)


def test_missing_parse() -> None:
    data = """{
        "research_question": "人工智能是否提高学习效率？",
        "data_source": "问卷调查",
        "sample_size": 100,
        "statistical_methods": ["t-test"],
        "key_findings": ["学习效率有所提升"],
    }"""
    with pytest.raises(ValueError, match="content 不是合法的 JSON"):
        parse_research_summary_content(data)


def test_false_type_with_sample_size() -> None:
    data = """{
        "research_question": "人工智能是否提高学习效率？",
        "data_source": "问卷调查",
        "sample_size": "100",
        "statistical_methods": ["t-test"],
        "key_findings": ["学习效率有所提升"],
        "limitations": ["样本范围有限"]
    }"""
    with pytest.raises(TypeError, match="sample_size: 必须为 int 类型"):
        parse_research_summary_content(data)


def test_false_type_with_data_source() -> None:
    data = """{
        "research_question": "人工智能是否提高学习效率？",
        "data_source": 123,
        "sample_size": 100,
        "statistical_methods": ["t-test"],
        "key_findings": ["学习效率有所提升"],
        "limitations": ["样本范围有限"]
    }"""
    with pytest.raises(TypeError, match="data_source: 必须为字符串"):
        parse_research_summary_content(data)


def test_false_type_with_key_findings() -> None:
    data = """{
        "research_question": "人工智能是否提高学习效率？",
        "data_source": "问卷调查",
        "sample_size": 100,
        "statistical_methods": ["t-test"],
        "key_findings": "学习效率有所提升",
        "limitations": ["样本范围有限"]
    }"""
    with pytest.raises(TypeError, match="key_findings: 必须是列表"):
        parse_research_summary_content(data)
