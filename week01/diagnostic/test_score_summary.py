import pytest

from score_summary import (
    average_major,
    average_score,
    max_score,
    pass_score,
    main,
)

@pytest.mark.parametrize(
        ("scores", "exp_average"),
        [
            ([60], 60.0),
            ([60, 80], 70.0),
            ([0, 100], 50.0)
        ],
        ids = ("single-score", "two-scores", "boundary-scores")
)
def test_average_score_with_typical_scores(scores: list[int], exp_average: float) -> None:
    assert average_score(scores) == pytest.approx(exp_average)

def test_max_score_prefers_100_over_92() -> None:
    students = [{"name": "张三", "score": "92"}, {"name": "李四", "score": "95"}, {"name": "王五", "score": "100"}]

    result_score, result_name = max_score(students)

    assert result_score == 100
    assert result_name == "王五" 

@pytest.mark.parametrize(
        ("scores", "expected_count", "expected_rate"),
        [
            ([59], 0, 0.0),
            ([60], 1, 1.0),
            ([100], 1, 1.0),
            ([59, 60, 100], 2, 2/3),
            ([], 0, 0.0)
        ],
        ids = ("all-failed", "passing-boundary", "full-score", "mixed-scores", "empty-scores")
)
def test_pass_score_includes_60(scores: list[int], expected_count: int, expected_rate: float) -> None:
    actual_count, actual_rate = pass_score(scores)
    assert actual_count == expected_count
    assert actual_rate == pytest.approx(expected_rate)

def test_average_major() -> None:
    students = [{"name": "张三", "major":"应用统计", "score": "92"}, 
                {"name": "李四", "major":"数学", "score": "95"}, 
                {"name": "王五", "major":"应用统计", "score": "100"}]

    result = average_major(students)
    assert result == {
        "应用统计": 96.0,
        "数学": 95.0,
    }

def test_average_score_with_empty() -> None:
    with pytest.raises(ValueError):
        average_score([])

def test_max_score_with_empty() -> None:
    with pytest.raises(ValueError):
        max_score([])

def test_main_prints_expected_summary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    main()

    output = capsys.readouterr().out

    assert "学生人数：8" in output
    assert "平均分：74.50" in output
    assert "最高分：92.0 (赵六)" in output
    assert "及格率：75.00%" in output