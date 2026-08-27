"""W3-02 DeepSeek HTTP 响应结构解析参考实现。"""


def extract_message_content(response_data: object) -> str:
    """从未知的 Chat Completions 响应对象中提取原始模型文本。"""
    if not isinstance(response_data, dict):
        raise TypeError("response: 必须是 object")

    if "choices" not in response_data:
        raise ValueError("response.choices: 缺少字段")
    choices: object = response_data["choices"]
    if not isinstance(choices, list):
        raise TypeError("response.choices: 必须是 list")
    if not choices:
        raise ValueError("response.choices: 不能为空")

    first_choice: object = choices[0]
    if not isinstance(first_choice, dict):
        raise TypeError("response.choices[0]: 必须是 object")

    if "message" not in first_choice:
        raise ValueError("response.choices[0].message: 缺少字段")
    message: object = first_choice["message"]
    if not isinstance(message, dict):
        raise TypeError("response.choices[0].message: 必须是 object")

    if "content" not in message:
        raise ValueError("response.choices[0].message.content: 缺少字段")
    content: object = message["content"]
    if content is None:
        raise ValueError("response.choices[0].message.content: 不能为 null")
    if not isinstance(content, str):
        raise TypeError("response.choices[0].message.content: 必须是 str")
    if not content.strip():
        raise ValueError("response.choices[0].message.content: 不能为空")

    return content
