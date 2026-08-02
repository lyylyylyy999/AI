# 参考答案阅读指南

请对照 `score_summary.py` 阅读 `reference_solution.py`，不要直接覆盖自己的实现。

## 当前阶段状态

- Python 基础诊断：已通过
- 动态专业分组：已通过
- 脚本相对路径：已通过
- 函数类型标注：已通过
- 100 分数值比较：已通过
- 自动化测试与边界处理：已通过
- 红、绿、重构循环：已通过
- pytest 参数化与可读用例 ID：已通过
- 单元测试与集成测试：已通过
- 行覆盖率分析：已通过（98%）
- argparse 命令行路径：已通过
- stdout、stderr 与退出码：已通过
- tmp_path CLI 集成测试：已通过

本阶段参考实现已经校准：函数签名明确区分 `list[Student]`、`tuple[int, float]`、`dict[str, float]` 和 `None`，最高分比较会先把 CSV 字符串转换为数值。

测试阶段的推荐写法位于 `reference_tests.py`。它与 `reference_solution.py` 配套，展示显式导入、场景化命名、参数化、浮点近似比较、异常断言、空数据契约和终端输出集成测试。

CLI 阶段的参考实现支持默认数据和用户传入路径，以 0、1、2 区分成功、文件不存在和数据错误。`main(argv)` 的设计允许测试直接模拟命令行参数，而无需创建子进程。

## 建议阅读顺序

1. 查看 `DATA_FILE`，解释为什么它不依赖程序的启动目录。
2. 查看每个函数的参数类型和返回值类型。
3. 对比两个版本查找最高分学生的方式。
4. 查看 `pass_statistics()` 如何处理 60 分和空数据。
5. 查看 `average_scores_by_major()` 中字典的结构。
6. 查看 `print_summary()` 为什么只负责组织和输出结果。

## 必须能回答的问题

1. `Student = dict[str, str]` 有什么作用？
2. `list[Student]` 表示什么？
3. `-> tuple[int, float]` 表示什么？
4. `if not students` 在判断什么？
5. `key=lambda student: int(student["score"])` 在最高分计算中起什么作用？
6. 为什么 `passing_score` 被设计成参数？
7. 为什么参考答案没有为三个专业分别创建变量？

## 对照原则

- 写法不同不等于错误，先比较正确性和可扩展性。
- 不要求立即掌握列表推导式、生成器表达式和 `lambda`。
- 优先理解函数的输入、输出和职责。
- 看完后合上参考答案，尝试用自己的话复述设计。
