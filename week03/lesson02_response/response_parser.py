def extract_message_content(response_data: object) -> str:
    if not isinstance(response_data, dict):
        raise TypeError("响应返回的不是字典")
    if "choices" not in response_data:
        raise ValueError("choices 缺失")
    if not isinstance(response_data["choices"], list):
        raise TypeError("choices 必须是列表")
    if len(response_data["choices"]) == 0:
        raise ValueError("choices 不能为空")
    if not isinstance(response_data["choices"][0], dict):
        raise TypeError("choices[0] 必须为字典")
    if "message" not in response_data["choices"][0]:
        raise ValueError("choices[0].message 缺失")
    if not isinstance(response_data["choices"][0]["message"], dict):
        raise TypeError("choices[0].message 必须为字典")
    if "content" not in response_data["choices"][0]["message"]:
        raise ValueError("choices[0].message.content 缺失")
    if response_data["choices"][0]["message"]["content"] is None:
        raise ValueError("choices[0].message.content 不能为空")
    if not isinstance(response_data["choices"][0]["message"]["content"], str):
        raise TypeError("choices[0].message.content 必须为字符串类型")
    if response_data["choices"][0]["message"]["content"].strip() == "":
        raise ValueError("choices[0].message.content 不能为空或者纯空白")
    return response_data["choices"][0]["message"]["content"]
