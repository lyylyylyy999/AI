# W2-02B 参考实现阅读指南

对应文件：`reference_full.py` 和 `reference_full_tests.py`。阅读前应先理解 W2-02A 的核心字段参考实现。

## 重点一：容器类型不代表元素类型

`isinstance(value, list)` 只能证明值是列表。外部数据仍可能是：

```python
["线性回归", 42, None]
```

因此参考实现使用 `enumerate()` 同时检查元素并保留索引，让错误能够定位为 `key_findings[1]`。

## 重点二：验证过程中创建新列表

参考实现没有在验证结束后直接返回原始 `value`，而是把每个验证通过的字符串加入 `validated_items`。这同时完成：

- 元素级验证。
- 一层浅复制。
- 与外部可变列表切断引用共享。

对于当前的 `list[str]`，浅复制已经足够，因为字符串本身不可变。未来遇到嵌套字典或嵌套列表时，还需要重新讨论复制深度。

## 重点三：组合已经验证的契约

`validate_research_summary()` 复用 `validate_summary_core()`，然后验证三个新增列表字段，最后构造完整 `ResearchSummary`。这样核心字段规则只有一处来源。

## 当前数据流

```text
JSON 文本
  → json.loads / json.load
  → object（只保证 JSON 语法有效）
  → validate_research_summary
  → ResearchSummary（业务契约已验证）
```

下一阶段学习 HTTP 时，API 响应也会沿着同一条边界进入校验函数。
