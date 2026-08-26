import re

import pytest
from response_parser import extract_message_content


def test_valid_response_parser() -> None:
    data = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": ' {"research_question": "问题"} ',
                }
            }
        ]
    }
    result = extract_message_content(data)
    assert result == ' {"research_question": "问题"} '
    assert type(result) == str


@pytest.mark.parametrize(
    ("data", "exception", "match"),
    [
        ([], TypeError, "响应返回的不是字典"),
        ({}, ValueError, "choices 缺失"),
        ({"choices": 123}, TypeError, "choices 必须是列表"),
        ({"choices": []}, ValueError, "choices 不能为空"),
        ({"choices": [123]}, TypeError, "choices[0] 必须为字典"),
        ({"choices": [{}]}, ValueError, "choices[0].message 缺失"),
        ({"choices": [{"message": 123}]}, TypeError, "choices[0].message 必须为字典"),
        (
            {"choices": [{"message": {"role": "assistant"}}]},
            ValueError,
            "choices[0].message.content 缺失",
        ),
        (
            {"choices": [{"message": {"role": "assistant", "content": None}}]},
            ValueError,
            "choices[0].message.content 不能为空",
        ),
        (
            {"choices": [{"message": {"role": "assistant", "content": 123}}]},
            TypeError,
            "choices[0].message.content 必须为字符串类型",
        ),
        (
            {"choices": [{"message": {"role": "assistant", "content": "  "}}]},
            ValueError,
            "choices[0].message.content 不能为空或者纯空白",
        ),
        (
            {"choices": [{"message": {"role": "assistant", "content": "\t\n"}}]},
            ValueError,
            "choices[0].message.content 不能为空或者纯空白",
        ),
        (
            {"choices": [{"message": {"role": "assistant", "content": ""}}]},
            ValueError,
            "choices[0].message.content 不能为空或者纯空白",
        ),
    ],
    ids=(
        "response",
        "choices_missing",
        "choices_type",
        "choices_null",
        "choices[0]_type",
        "choices[0].message_missing",
        "choices[0].message_type",
        "choices[0].message.content_missing",
        "choices[0].message.content_none",
        "choices[0].message.content_type",
        "choices[0].message.content_blank_01",
        "choices[0].message.content_blank_02",
        "choices[0].message.content_empty",
    ),
)
def test_exception_response_parser(
    data: object, exception: type[Exception], match: str
) -> None:
    with pytest.raises(exception, match=re.escape(match)):
        extract_message_content(data)


if __name__ == "__main__":
    pytest.main(["week03/lesson02_response/test_response_parser.py", "-qs"])
