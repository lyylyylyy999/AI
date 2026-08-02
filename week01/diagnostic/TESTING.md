# 自动化测试入门

## 本课目标

- 理解测试为什么需要可重复执行。
- 掌握 pytest 的测试发现规则和基本断言。
- 使用测试覆盖正常输入、边界输入和异常输入。
- 经历一次“红 → 绿 → 重构”循环。

## 测试文件规则

pytest 默认会发现名称以 `test_` 开头的文件和函数。

在本目录创建：

```text
test_score_summary.py
```

每条测试通常包含三个部分：

1. Arrange：准备输入数据。
2. Act：调用被测试函数。
3. Assert：检查实际结果。

## 第一条完整示例

```python
from score_summary import average_score


def test_average_score_with_typical_scores() -> None:
    scores = [78, 65, 88]

    result = average_score(scores)

    assert result == 77.0
```

运行：

```powershell
python -m pytest week01/diagnostic/test_score_summary.py -v
```

## 需要独立完成的测试

在同一文件中继续编写：

1. `max_score()`：92 分和 100 分同时存在时，应返回 100 分学生。
2. `pass_score()`：输入 `[59, 60, 100]`，及格人数应为 2，及格率应约等于 `2 / 3`。
3. `average_major()`：至少包含两个专业，检查每个专业的平均分。
4. `average_score([])`：应抛出 `ValueError`。
5. `max_score([])`：应抛出 `ValueError`。
6. `pass_score([])`：期望返回 `(0, 0.0)`。这条测试在当前实现中应该失败。

浮点数比较使用：

```python
import pytest

assert actual_rate == pytest.approx(expected_rate)
```

异常检查使用：

```python
with pytest.raises(ValueError):
    # 在这里调用预期抛出异常的函数
```

## 红、绿、重构

- 红：先运行测试，确认 `pass_score([])` 测试失败。
- 绿：暂时不要修复，先把完整失败信息发来审查。
- 重构：审查测试本身后，再修改生产代码并重新运行。

## Git 忽略文件

如果仓库根目录还没有 `.gitignore`，创建它并加入：

```gitignore
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
.env
```

`.env` 未来会保存 API 密钥，绝不能提交到 Git。

## 提交前要求

本轮先不要提交。完成测试并保留一条预期失败后，回复：

```text
测试已编写
通过数量：
失败数量：
失败测试名称：
我认为失败原因：
```

