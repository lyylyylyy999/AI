# W3-02：DeepSeek HTTP 响应结构解析

预计用时：60–90 分钟。本任务只处理已经解析为 Python `object` 的 HTTP response JSON，不访问网络，不读取 API Key，也不解析模型文本中的 JSON。

## 本课目标

完成后你应当能够：

1. 把不可信的嵌套 `object` 逐层收窄为 `str`。
2. 区分字段缺失、容器类型错误和空模型内容。
3. 从 DeepSeek Chat Completions 响应中提取 `choices[0].message.content`。
4. 保持 HTTP response JSON、模型文本和业务数据三层边界分离。
5. 使用反例证明每一次嵌套访问前都完成了运行时检查。

## 数据边界

```text
HTTP response JSON 对应的 object
  → choices
  → choices[0]
  → message
  → content
  → 模型生成文本 str
```

本任务到 `str` 为止。即使字符串看起来像 JSON，也不能调用 `json.loads()`；模型 JSON 解析与业务校验属于 W3-03。

## 独立任务

在本目录创建：

- `response_parser.py`
- `test_response_parser.py`

实现：

```python
def extract_message_content(response_data: object) -> str: ...
```

正常输入示例：

```python
{
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": '{"research_question": "问题"}',
            }
        }
    ]
}
```

返回值仍然是原始字符串：

```python
'{"research_question": "问题"}'
```

## 运行时检查要求

| 输入问题 | 异常类型 | 错误消息至少指出 |
|---|---|---|
| 顶层不是 `dict` | `TypeError` | `response` |
| `choices` 缺失 | `ValueError` | `choices` |
| `choices` 不是 `list` | `TypeError` | `choices` |
| `choices` 为空 | `ValueError` | `choices` |
| `choices[0]` 不是 `dict` | `TypeError` | `choices[0]` |
| `message` 缺失 | `ValueError` | `choices[0].message` |
| `message` 不是 `dict` | `TypeError` | `choices[0].message` |
| `content` 缺失 | `ValueError` | `choices[0].message.content` |
| `content is None` | `ValueError` | `choices[0].message.content` |
| `content` 不是 `str` | `TypeError` | `choices[0].message.content` |
| `content` 为空或纯空白 | `ValueError` | `choices[0].message.content` |

允许用 `content.strip()` 判断内容是否为空，但成功时必须返回原始 `content`，不能擅自删除模型文本两端空白。

## 红—绿—重构

### 红：正常路径

先写测试证明：

- 能提取第一条 choice 的 message content；
- 看起来像 JSON 的 content 仍返回 `str`；
- 非空内容两端的空白不会被修改。

### 绿：逐层收窄

按以下顺序逐层检查存在性与类型：

```text
response_data → choices → choices[0] → message → content
```

不要用一条长表达式直接访问所有层，也不要使用 `Any`、`cast()`、`# type: ignore` 或异常捕获来掩盖类型问题。

### 补齐反例

覆盖表格中的结构问题。参数化应服务于可读性，不要把不同数据层级全部塞进难以理解的单个参数表。

## 测试真实性要求

- 测试输入直接表达外部响应结构，不复制生产函数的判断逻辑。
- 正常测试应断言返回的是原始字符串，而不是字典。
- 缺失字段与错误类型要用不同反例证明。
- 不以测试数量或 100% 覆盖率为目标。
- 不导入 W3-01 客户端，不使用 MockTransport，因为本层不发送 HTTP 请求。

## 验收标准

- 公开接口是 `extract_message_content(response_data: object) -> str`。
- 正常模型文本原样返回。
- 所有嵌套访问前都有运行时检查。
- 错误消息能定位到具体响应路径。
- 不调用 `json.loads()`，不处理 Markdown code fence。
- 不导入 `validate_research_summary`，不进行业务校验。
- 不访问网络，不读取环境变量或 API Key。
- Ruff、mypy strict 和 pytest 全部通过。

## 运行命令

```powershell
.\.venv\Scripts\ruff.exe check week03\lesson02_response
.\.venv\Scripts\ruff.exe format --check week03\lesson02_response
.\.venv\Scripts\mypy.exe --strict week03\lesson02_response\response_parser.py week03\lesson02_response\test_response_parser.py
.\.venv\Scripts\python.exe -m pytest week03\lesson02_response\test_response_parser.py -q
```

## 完成后回复

```text
W3-02 完成
用时：
测试数：
Ruff：
mypy：
pytest：

为什么输入类型仍然是 object：
为什么不能直接连续索引到 content：
为什么本层不能调用 json.loads：
空白检查后为什么仍返回原始 content：
```
