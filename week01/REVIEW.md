# 第 1 周复盘与检查点

## 目标

本次不学习新语法，检查是否能够：

- 用自己的话解释已经写出的代码。
- 在没有逐步代码提示时完成一个小需求。
- 用自动化测试证明修改没有破坏旧功能。
- 使用 Ruff、mypy 和 pytest 完成自检。

## A. 概念复盘

请不查看参考答案，用自己的话回答：

1. `Path(__file__).resolve().parent` 和当前工作目录有什么区别？
2. 在专业平均分统计中，`major_stats` 的 key 和 value 分别是什么？
3. `tuple[int, float]` 表示什么？
4. 为什么 CSV 中的分数在比较或计算前必须转换为数值？
5. `main(argv=None)` 中的 `None` 表示什么？测试为什么使用 `main([])`？
6. stdout、stderr 和退出码分别解决什么问题？
7. 单元测试与集成测试的主要区别是什么？
8. Ruff format、Ruff check、mypy 和 pytest 各自负责什么？

## B. 独立修改题：可配置及格线

当前程序把 60 分写死在 `pass_score()` 中。请新增命令行选项：

```powershell
python week01\diagnostic\score_summary.py --passing-score 80
```

也应支持同时传入文件路径：

```powershell
python week01\diagnostic\score_summary.py data.csv --passing-score 80
```

### 功能要求

- 参数名：`--passing-score`。
- 类型：整数。
- 默认值：60。
- `pass_score()` 接收及格线参数，不再在函数内部写死 60。
- `main()` 将命令行参数传给 `pass_score()`。
- 不传选项时，原有输出和行为保持不变。
- `--help` 中能看到该选项。

### 测试要求

保留原有 16 条测试，并新增至少 1 条集成测试：

- 创建包含 60 分和 100 分的临时 CSV。
- 使用 `--passing-score 80`。
- 预期及格人数为 1。
- 预期及格率为 50.00%。
- 预期退出码为 0。

测试总数至少应为 17。

### 质量要求

完成后依次通过：

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

## C. 项目讲解训练

请准备一段 2 分钟以内的项目介绍，包含：

1. 项目解决什么问题。
2. 输入和输出是什么。
3. 程序如何拆分职责。
4. 如何处理错误。
5. 如何通过测试和质量工具保证可靠性。
6. 当前还存在哪些局限。

## 提交格式

完成后回复：

```text
第 1 周复盘完成

A1：
A2：
A3：
A4：
A5：
A6：
A7：
A8：

独立修改用时：
测试数量：
Ruff：
mypy：
pytest：

项目介绍：

本周最重要的三个收获：
仍然最薄弱的地方：
```

本次先不要查看参考实现，也不要提交 Git，等待最终审查。

