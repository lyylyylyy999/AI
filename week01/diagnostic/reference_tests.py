"""成绩摘要的 pytest 参考测试。"""

import pytest

from reference_solution import (
    average_score,
    average_scores_by_major,
    highest_scoring_student,
    pass_statistics,
)


def test_average_score_with_typical_scores() -> None:
    students = [
        {"name": "张三", "major": "应用统计", "score": "78"},
        {"name": "李四", "major": "应用统计", "score": "65"},
        {"name": "王五", "major": "应用统计", "score": "88"},
    ]

    assert average_score(students) == 77.0


def test_highest_score_compares_scores_numerically() -> None:
    students = [
        {"name": "九十二分", "major": "测试", "score": "92"},
        {"name": "一百分", "major": "测试", "score": "100"},
    ]

    top_student = highest_scoring_student(students)

    assert top_student["name"] == "一百分"
    assert top_student["score"] == "100"


def test_pass_statistics_includes_60() -> None:
    students = [
        {"name": "未及格", "major": "测试", "score": "59"},
        {"name": "边界值", "major": "测试", "score": "60"},
        {"name": "满分", "major": "测试", "score": "100"},
    ]

    passed_count, passed_rate = pass_statistics(students)

    assert passed_count == 2
    assert passed_rate == pytest.approx(2 / 3)


def test_average_scores_by_major_groups_students() -> None:
    students = [
        {"name": "张三", "major": "应用统计", "score": "92"},
        {"name": "李四", "major": "数学", "score": "95"},
        {"name": "王五", "major": "应用统计", "score": "100"},
    ]

    result = average_scores_by_major(students)

    assert result == {
        "应用统计": 96.0,
        "数学": 95.0,
    }


def test_average_score_rejects_empty_data() -> None:
    with pytest.raises(ValueError):
        average_score([])


def test_highest_score_rejects_empty_data() -> None:
    with pytest.raises(ValueError):
        highest_scoring_student([])


def test_pass_statistics_accepts_empty_data() -> None:
    assert pass_statistics([]) == (0, 0.0)

