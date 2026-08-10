# W2-01 参考实现阅读指南

请在自己的实现通过验收后再阅读。本文件对应：

- `reference_solution.py`
- `reference_tests.py`

## 阅读顺序

1. 先看 `build_research_record`，逐项判断 Python 值会变成哪种 JSON 值。
2. 对比 `serialize_record` 与 `save_record`：前者返回字符串，后者接收文件路径并写文件。
3. 查看 `load_json` 为什么返回 `object`，而不是直接承诺 `dict[str, object]`。
4. 查看参考测试如何使用 `tmp_path`，以及 fixture 如何基于 `__file__` 定位。

## 四个函数的边界

| 函数 | 输入 | 输出或副作用 |
|---|---|---|
| `json.dumps` | Python 对象 | JSON 字符串 |
| `json.loads` | JSON 字符串 | Python 对象 |
| `json.dump` | Python 对象、文件对象 | 写入 JSON 文件 |
| `json.load` | 文件对象 | Python 对象 |

函数名末尾的 `s` 可以记作 string。`dump` 表示向 JSON 方向转换，`load` 表示从 JSON 方向读回。

## 两个不同的中文问题

- `encoding="utf-8"` 决定文件如何编码和解码。
- `ensure_ascii=False` 决定非 ASCII 字符是否在 JSON 文本中显示为原字符。

两者不能互相替代。UTF-8 文件仍可能包含 `\uXXXX`，而 `ensure_ascii=False` 也不能替代正确的文件编码。

## 当前刻意保留的边界

`json.load` 只验证 JSON 语法，不验证研究记录的字段。合法 JSON `[]`、`42` 或 `{"sample_size": "很多"}` 都可能不符合业务契约。因此参考实现将读入值标为 `object`。W2-02 会负责把未知外部数据校验为明确的研究摘要结构。

## 运行参考质量门

```powershell
.\.venv\Scripts\ruff.exe check week02\lesson01_json\reference_solution.py week02\lesson01_json\reference_tests.py
.\.venv\Scripts\ruff.exe format --check week02\lesson01_json\reference_solution.py week02\lesson01_json\reference_tests.py
.\.venv\Scripts\mypy.exe --strict week02\lesson01_json\reference_solution.py week02\lesson01_json\reference_tests.py
.\.venv\Scripts\python.exe -m pytest week02\lesson01_json\reference_tests.py -q
```
