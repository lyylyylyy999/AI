"""W3-02 DeepSeek HTTP 响应结构解析参考测试。"""

import pytest
from reference_solution import extract_message_content


def test_extracts_json_shaped_content_as_original_string() -> None:
    content = '  {"research_question": "问题"}\n'
    response_data = {
        "choices": [{"message": {"role": "assistant", "content": content}}]
    }

    result = extract_message_content(response_data)

    assert isinstance(result, str)
    assert result == content


@pytest.mark.parametrize("response_data", [[], None, "response"])
def test_rejects_non_object_response(response_data: object) -> None:
    with pytest.raises(TypeError, match="response"):
        extract_message_content(response_data)


def test_rejects_missing_choices() -> None:
    with pytest.raises(ValueError, match="choices"):
        extract_message_content({})


@pytest.mark.parametrize("choices", [None, {}, "choice"])
def test_rejects_choices_with_wrong_type(choices: object) -> None:
    with pytest.raises(TypeError, match="choices"):
        extract_message_content({"choices": choices})


def test_rejects_empty_choices() -> None:
    with pytest.raises(ValueError, match="choices"):
        extract_message_content({"choices": []})


@pytest.mark.parametrize("first_choice", [None, [], "choice"])
def test_rejects_non_object_first_choice(first_choice: object) -> None:
    with pytest.raises(TypeError, match=r"choices\[0\]"):
        extract_message_content({"choices": [first_choice]})


def test_rejects_missing_message() -> None:
    with pytest.raises(ValueError, match="message"):
        extract_message_content({"choices": [{}]})


@pytest.mark.parametrize("message", [None, [], "message"])
def test_rejects_message_with_wrong_type(message: object) -> None:
    with pytest.raises(TypeError, match="message"):
        extract_message_content({"choices": [{"message": message}]})


def test_rejects_missing_content() -> None:
    with pytest.raises(ValueError, match="content"):
        extract_message_content({"choices": [{"message": {}}]})


def test_rejects_null_content() -> None:
    with pytest.raises(ValueError, match="content"):
        extract_message_content({"choices": [{"message": {"content": None}}]})


@pytest.mark.parametrize("content", [123, [], {}])
def test_rejects_content_with_wrong_type(content: object) -> None:
    with pytest.raises(TypeError, match="content"):
        extract_message_content({"choices": [{"message": {"content": content}}]})


@pytest.mark.parametrize("content", ["", "   ", "\t\n"])
def test_rejects_empty_or_blank_content(content: str) -> None:
    with pytest.raises(ValueError, match="content"):
        extract_message_content({"choices": [{"message": {"content": content}}]})
