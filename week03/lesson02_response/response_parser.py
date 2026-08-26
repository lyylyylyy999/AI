def extract_message_content(response_data: object) -> str:
    if not isinstance(response_data, dict):
        raise TypeError("响应返回的不是字典")
    if "choices" not in response_data:
        raise ValueError("choices 缺失")
    choices = response_data["choices"]
    if not isinstance(choices, list):
        raise TypeError("choices 必须是列表")
    if len(choices) == 0:
        raise ValueError("choices 不能为空")
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise TypeError("choices[0] 必须为字典")
    if "message" not in first_choice:
        raise ValueError("choices[0].message 缺失")
    message = first_choice["message"]
    if not isinstance(message, dict):
        raise TypeError("choices[0].message 必须为字典")
    if "content" not in message:
        raise ValueError("choices[0].message.content 缺失")
    content = message["content"]
    if content is None:
        raise ValueError("choices[0].message.content 不能为空")
    if not isinstance(content, str):
        raise TypeError("choices[0].message.content 必须为字符串类型")
    if content.strip() == "":
        raise ValueError("choices[0].message.content 不能为空或者纯空白")
    return content
