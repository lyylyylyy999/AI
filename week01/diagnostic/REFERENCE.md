# 参考答案阅读指南

请对照 `score_summary.py` 阅读 `reference_solution.py`，不要直接覆盖自己的实现。

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

