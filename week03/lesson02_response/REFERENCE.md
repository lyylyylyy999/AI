# W3-02 参考实现阅读指南

对应文件：`reference_solution.py` 和 `reference_tests.py`。参考答案在 W3-02 学习实现通过后生成，用于复盘和对照，不覆盖 `response_parser.py`。

## 1. 为什么入口仍然是 object

W3-01 的 HTTP 层调用 `response.json()` 后，只能确定得到某个 Python JSON 值。JSON 顶层可以是字典、列表、字符串、数字、布尔值或 `None`，所以 W3-02 不能假定它已经符合 DeepSeek 响应结构。

```text
response.json() → object
```

只有运行时检查全部通过，函数才能诚实地返回 `str`。

## 2. object 与 Any 的区别

从裸 `dict` 直接取值容易得到隐式 `Any`。`Any` 会让类型检查器放弃检查；显式把每层外部值标注为 `object`，则必须通过 `isinstance` 才能继续操作。

```text
choices: object
→ isinstance(choices, list)
→ first_choice: object
→ isinstance(first_choice, dict)
```

相同模式继续应用到 `message` 和 `content`，最终把 `content` 收窄为 `str`。

## 3. 为什么逐层检查

直接连续索引会把多个失败点混在一起。顶层、`choices`、第一条 choice、`message` 和 `content` 任一层错误，都可能产生难以定位的内置异常。

参考实现按路径逐层检查：

```text
response
→ response.choices
→ response.choices[0]
→ response.choices[0].message
→ response.choices[0].message.content
```

异常消息因此可以指出失败发生在哪一层。

## 4. 缺失、类型错误与空值

- 字段不存在：结构不完整，使用 `ValueError`。
- 容器或内容类型错误：实际类型违反预期，使用 `TypeError`。
- `choices` 为空或 content 无可用文本：值存在但不可用，使用 `ValueError`。

这是当前函数的局部契约。完整错误翻译和 CLI 退出码留到第 4 周。

## 5. 为什么 content 原样返回

`.strip()` 只用于判断字符串是否为空。成功时返回原始 content，避免响应解析层悄悄修改模型文本。是否去除 Markdown code fence、是否解析 JSON，属于 W3-03。

## 6. 参考测试如何约束边界

参考测试分别证明：

- JSON 形状的字符串没有被提前解析；
- 非空内容两端空白没有被修改；
- 每一层缺失或类型错误都有定向反例；
- `None`、错误类型、空字符串和纯空白不会冒充有效模型文本。

测试没有访问网络，也没有依赖 W3-01 客户端或真实 DeepSeek 响应。

## 7. 当前刻意不做的事情

- 不解析模型文本中的 JSON。
- 不处理 Markdown code fence。
- 不调用 `validate_research_summary`。
- 不创建自定义异常体系。
- 不组装 CLI 或退出码矩阵。

这些边界分别留给 W3-03 和第 4 周。
