# 第 1 课：Python 对象与 JSON 的转换

预计用时：30–60 分钟。当前只处理本地数据，不调用 DeepSeek API，也不安装新依赖。

## 本课目标

完成后你应当能够：

1. 解释序列化与反序列化。
2. 区分 `json.dumps` / `json.loads` 和 `json.dump` / `json.load`。
3. 正确读写 UTF-8 JSON，并让中文保持可读。
4. 识别 `JSONDecodeError` 与 Python 对象不可序列化的错误。
5. 理解“JSON 已成功解析”不等于“业务字段已经校验”。

## 核心概念

JSON 是文本格式；Python 的 `dict`、`list` 等是内存中的对象。

| Python | JSON | 注意 |
|---|---|---|
| `dict` | object | JSON 的键必须是字符串 |
| `list` / `tuple` | array | 读回 Python 时都是 `list` |
| `str` | string | JSON 字符串使用双引号 |
| `int` / `float` | number | JSON 不区分整数类型和浮点类型名称 |
| `True` / `False` | `true` / `false` | 大小写不同 |
| `None` | `null` | 名称不同 |

`set`、`Path`、`datetime` 等对象不能由标准库 `json` 直接序列化。遇到它们时，应先明确业务规则并转换，而不是随意使用 `str()` 掩盖类型问题。

### 四个常用函数

- `json.dumps(python_object)`：Python 对象 → JSON 字符串。
- `json.loads(json_text)`：JSON 字符串 → Python 对象。
- `json.dump(python_object, file)`：Python 对象 → JSON 文件。
- `json.load(file)`：JSON 文件 → Python 对象。

记忆方法：名字带 `s` 的版本处理字符串；不带 `s` 的版本处理文件对象。

### 最小示例

下面只演示 API，不是练习答案：

```python
import json

course = {"week": 2, "topic": "JSON", "finished": False}
json_text = json.dumps(course, ensure_ascii=False, indent=2)
restored = json.loads(json_text)

assert restored == course
```

- `ensure_ascii=False` 让中文直接保存在文件中，而不是写成 `\uXXXX`。
- `indent=2` 让结果便于人类阅读。
- 读写文件时仍要显式指定 `encoding="utf-8"`；这与 `ensure_ascii` 是两个不同问题。

### 两类常见失败

非法 JSON 文本会抛出 `json.JSONDecodeError`。它是 `ValueError` 的子类，并提供行号、列号等定位信息。

Python 对象无法转换为 JSON 时，`json.dumps` / `json.dump` 会抛出 `TypeError`。例如集合 `{"回归", "Bootstrap"}` 不是 JSON 支持的数据类型。

解析成功只说明文本语法有效。例如 `[]` 是合法 JSON，但它不一定符合“研究记录必须是 object”的业务契约。运行时字段校验将在 W2-02 单独处理。

## 独立练习：研究记录 JSON 往返

在 `week02/lesson01_json/` 下自行创建：

- `json_practice.py`
- `test_json_practice.py`

不要修改第 1 周代码，也不要查看或创建参考答案。

### 任务 1：建立 Python 对象

实现：

```python
def build_research_record() -> dict[str, object]: ...
```

返回值至少包含以下信息，并为每类 JSON 值选择合适的 Python 类型：

- 中文标题。
- 样本量 `240`。
- 两种统计方法组成的列表。
- 一个浮点数效应量。
- 一个布尔值“是否经过同行评审”。
- 一个尚无内容的备注。
- 一个包含语言和年份的嵌套对象。

字段名由你设计，但要使用清晰的英文 `snake_case`。

### 任务 2：字符串序列化

实现：

```python
def serialize_record(record: dict[str, object]) -> str: ...
```

要求输出 UTF-8 友好的、缩进为 2 个空格的 JSON 文本；中文不能变成 `\uXXXX`。

### 任务 3：文件往返

实现：

```python
from pathlib import Path


def save_record(record: dict[str, object], path: Path) -> None: ...


def load_json(path: Path) -> object: ...
```

- 使用 `json.dump` 和 `json.load`。
- 文件读写显式使用 UTF-8。
- `load_json` 暂时返回 `object`：来自文件的外部数据尚未经过业务校验，不能仅凭类型标注假定它是目标字典。
- 不要在 `load_json` 中吞掉 `JSONDecodeError`。

### 任务 4：先测试，再实现

至少编写 4 条有效测试：

1. 记录包含预期的 JSON 值类型，特别是 `None`、布尔值和列表。
2. `serialize_record` 的输出可被 `json.loads` 还原，且文本中直接包含中文和换行。
3. 保存再读取后，数据与原对象相等。
4. 读取 `data/invalid_research_record.json` 时抛出 `json.JSONDecodeError`。

先写一条失败测试，确认“红”；完成最少代码确认“绿”；最后再整理命名和重复代码。

## 验收标准

- 4 个函数职责清晰，没有在函数内部写死输出路径。
- 使用 `json` 标准库，没有手工拼接 JSON 字符串。
- 中文在生成的 JSON 文件中可直接阅读。
- 非法 JSON 的测试准确断言 `json.JSONDecodeError`，而不是宽泛的 `Exception`。
- 不使用 `default=str` 绕过不支持的数据类型。
- 学习实现通过 Ruff、mypy strict 和 pytest。

## 运行命令

在仓库根目录 PowerShell 中执行：

```powershell
.\.venv\Scripts\python.exe -m pytest week02\lesson01_json\test_json_practice.py -q
```

```powershell
.\.venv\Scripts\ruff.exe check week02\lesson01_json
```

```powershell
.\.venv\Scripts\ruff.exe format --check week02\lesson01_json
```

```powershell
.\.venv\Scripts\mypy.exe --strict week02\lesson01_json\json_practice.py week02\lesson01_json\test_json_practice.py
```

Codex 验收时会另外指定唯一 `--basetemp`，不会使用你的 `.pytest_tmp`。

## 完成后回复格式

```text
W2-01 完成
用时：
测试数：
Ruff check：
Ruff format --check：
mypy strict：
pytest：
最容易混淆的概念：
```

验收时我会实际读取代码、先运行失败用例或质量门，再按正确性、类型契约、命名、职责、错误边界和测试有效性审查。
