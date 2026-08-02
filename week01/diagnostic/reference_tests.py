"""成绩摘要的 pytest 参考测试。"""

import pytest

from reference_solution import (
    Student,
    average_score,
    average_scores_by_major,
    highest_scoring_student,
    main,
    pass_statistics,
)


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
    students: list[Student] = [
        {"name": f"学生{index}", "major": "测试", "score": str(score)}
        for index, score in enumerate(scores)
    ]

    assert average_score(students) == pytest.approx(expected_average)


def test_highest_score_compares_scores_numerically() -> None:
    students: list[Student] = [
        {"name": "九十二分", "major": "测试", "score": "92"},
        {"name": "一百分", "major": "测试", "score": "100"},
    ]

    top_student = highest_scoring_student(students)

    assert top_student["name"] == "一百分"
    assert top_student["score"] == "100"


@pytest.mark.parametrize(
    ("scores", "expected_count", "expected_rate"),
    [
        ([59], 0, 0.0),
        ([60], 1, 1.0),
        ([100], 1, 1.0),
        ([59, 60, 100], 2, 2 / 3),
        ([], 0, 0.0),
    ],
    ids=[
        "all-failed",
        "passing-boundary",
        "full-score",
        "mixed-scores",
        "empty-scores",
    ],
)
def test_pass_statistics_cases(
    scores: list[int], expected_count: int, expected_rate: float
) -> None:
    students: list[Student] = [
        {"name": f"学生{index}", "major": "测试", "score": str(score)}
        for index, score in enumerate(scores)
    ]

    actual_count, actual_rate = pass_statistics(students)

    assert actual_count == expected_count
    assert actual_rate == pytest.approx(expected_rate)


def test_average_scores_by_major_groups_students() -> None:
    students: list[Student] = [
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


def test_main_prints_expected_summary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    main()

    output = capsys.readouterr().out

    assert "学生人数: 8" in output
    assert "平均分: 74.50" in output
    assert "最高分: 92.0 (赵六)" in output
    assert "及格率: 75.00%" in output

