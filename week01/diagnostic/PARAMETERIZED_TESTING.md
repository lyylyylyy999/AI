# pytest 参数化测试与覆盖率

## 本课目标

- 使用一条测试函数运行多组输入。
- 为不同用例设置可读的测试 ID。
- 理解行覆盖率与未覆盖行。
- 理解覆盖率高不等于测试质量高。

## 参数化是什么

普通测试通常只有一组输入。参数化把多组输入交给同一个测试函数，pytest 会把每组输入作为独立用例运行。

下面是平均分的完整示例：

```python
@pytest.mark.parametrize(
    ("scores", "expected_average"),
    [
        ([60], 60.0),
        ([60, 80], 70.0),
        ([0, 100], 50.0),
    ],
    ids=["single-score", "two-scores", "boundary-scores"],
)
def test_average_score_cases(
    scores: list[int], expected_average: float
) -> None:
    assert average_score(scores) == pytest.approx(expected_average)
```

pytest 会将它显示成三条独立测试。某一组失败时，可以直接从 ID 看出失败场景。

## 独立任务一：参数化及格统计

把现有两个测试：

- `test_pass_score_includes_60`
- `test_pass_score_with_empty`

合并为一条参数化测试，覆盖五组数据：

| scores | 及格人数 | 及格率 | ID |
|---|---:|---:|---|
| `[59]` | 0 | 0.0 | `all-failed` |
| `[60]` | 1 | 1.0 | `passing-boundary` |
| `[100]` | 1 | 1.0 | `full-score` |
| `[59, 60, 100]` | 2 | `2 / 3` | `mixed-scores` |
| `[]` | 0 | 0.0 | `empty-scores` |

要求：

- 参数名称包含 `scores`、`expected_count`、`expected_rate`。
- 使用 `ids`。
- 及格率使用 `pytest.approx()`。
- 删除被替代的两个旧测试，避免重复覆盖同一契约。

## 独立任务二：参数化平均分

使用上面的完整示例替换原来的普通平均分测试，但不要删除空列表抛出 `ValueError` 的测试。正常返回和异常行为是两种不同契约。

## 覆盖率

从仓库根目录运行：

```powershell
.\.venv\Scripts\python.exe -m pytest week01\diagnostic\test_score_summary.py --cov=score_summary --cov-report=term-missing
```

报告中的关键列：

- `Stmts`：可执行语句数。
- `Miss`：没有被测试执行的语句数。
- `Cover`：行覆盖比例。
- `Missing`：没有执行的具体行号。

覆盖率只回答“某行是否运行过”，不能回答：

- 断言是否正确。
- 边界条件是否完整。
- 业务需求是否理解正确。
- 测试是否容易维护。

## 本轮提交要求

先不要修改 `score_summary.py`。完成参数化后运行测试和覆盖率，并回复：

```text
参数化完成
pytest 显示的测试数量：
行覆盖率：
未覆盖行号：
为什么测试函数数量和 pytest 用例数量不同：
```

