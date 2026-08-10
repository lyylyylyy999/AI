# W2-02A 参考实现阅读指南

对应文件：`reference_core.py` 和 `reference_core_tests.py`。

## 先回答三个问题

1. `ResearchSummaryCore` 在程序运行时会自动拒绝错误数据吗？
2. 为什么参考实现先校验局部变量，最后才构造 `ResearchSummaryCore`？
3. 为什么 `sample_size=True` 是 `TypeError`，而 `sample_size=0` 是 `ValueError`？

## TypedDict 的职责

`TypedDict` 是给静态类型检查器看的字典形状说明。它让 mypy 知道固定键对应什么类型，但运行时构造 `ResearchSummaryCore(...)` 仍然只会得到普通 `dict`，不会自动校验外部数据。

运行时安全来自 `validate_summary_core()` 中真实执行的 `isinstance`、空值和范围检查。

## 参考实现的验证顺序

```text
未知 object
  → 顶层类型
  → 必需字段
  → 字段类型
  → 字段取值
  → 构造新的 ResearchSummaryCore
```

先验证类型再调用 `.strip()` 或进行数值比较，可以避免向调用者泄漏 `AttributeError` 等内部实现异常。

## TypeError 与 ValueError

- `TypeError`：值的类型不符合接口，例如用字符串表示样本量。
- `ValueError`：类型正确，但内容不合法，例如空问题或样本量为零。
- 本项目暂用 `ValueError` 表示缺少业务必需字段，并确保消息包含字段名。

## 为什么构造新字典

返回新字典可以丢弃模型可能附带的额外字段，并建立清晰的信任边界：函数外拿到的是经过当前契约校验的数据，而不是原始外部字典的别名。
