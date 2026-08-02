# 代码质量：格式化、Lint 与静态类型检查

## 本课目标

- 区分格式化、Lint、类型检查和自动化测试。
- 使用 Ruff 自动处理机械性代码风格问题。
- 使用 mypy 在不运行程序的情况下检查类型契约。
- 在自动修改后通过 Git diff 审查变化，并运行回归测试。

## 四类工具分别回答什么

| 工具 | 回答的问题 |
|---|---|
| Ruff format | 代码排版是否统一？ |
| Ruff check | 是否存在未使用导入、导入顺序、可简化写法等问题？ |
| mypy | 参数、返回值和变量类型是否一致？ |
| pytest | 程序在给定场景中的行为是否符合预期？ |

任何一项通过都不能代替其他三项。

## 当前基线

Ruff lint 发现 3 个问题：

- 两个文件的导入顺序不规范。
- `range(0, len(...))` 中的起点 `0` 多余。

Ruff format 判断两个文件需要重新排版。mypy 严格模式当前没有报错。

## 第一步：自动修复安全的 lint 问题

从仓库根目录运行：

```powershell
.\.venv\Scripts\ruff.exe check week01\diagnostic\score_summary.py week01\diagnostic\test_score_summary.py --fix
```

## 第二步：统一格式

```powershell
.\.venv\Scripts\ruff.exe format week01\diagnostic\score_summary.py week01\diagnostic\test_score_summary.py
```

格式化可能改变换行、空格和括号布局，但不应改变业务行为。

## 第三步：做一个人工重构

把 `main()` 中通过索引构造分数列表的代码：

```python
scores = []
for i in range(len(students)):
    scores.append(int(students[i]["score"]))
```

改成直接遍历学生记录的列表推导式：

```python
scores = [int(student["score"]) for student in students]
```

列表推导式的结构是：

```text
[输出表达式 for 当前元素 in 可迭代对象]
```

## 第四步：审查自动修改

```powershell
git diff -- week01\diagnostic\score_summary.py week01\diagnostic\test_score_summary.py
```

确认没有删除断言、改变退出码或修改业务条件。

## 第五步：运行四道质量门

```powershell
.\.venv\Scripts\ruff.exe check week01\diagnostic\score_summary.py week01\diagnostic\test_score_summary.py
```

```powershell
.\.venv\Scripts\ruff.exe format --check week01\diagnostic\score_summary.py week01\diagnostic\test_score_summary.py
```

```powershell
.\.venv\Scripts\mypy.exe --strict week01\diagnostic\score_summary.py week01\diagnostic\test_score_summary.py
```

```powershell
.\.venv\Scripts\python.exe -m pytest week01\diagnostic\test_score_summary.py -q
```

预期结果：

- Ruff check：`All checks passed!`
- Ruff format：`2 files already formatted`
- mypy：`Success: no issues found`
- pytest：`16 passed`

## 本轮限制

- 只修改自己的 `score_summary.py` 和 `test_score_summary.py`。
- 不格式化参考答案，方便比较你的变更范围。
- 不为了通过工具而删除类型标注或测试断言。
- 本轮先不要提交，等待代码审查。

完成后回复：

```text
代码质量检查完成
Ruff check：
Ruff format：
mypy：
pytest：
列表推导式中的 student 表示：
为什么格式化后仍需运行测试：
```

